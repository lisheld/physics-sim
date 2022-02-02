#IMPORTING PACKAGES

import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import numpy as np
import pandas as pd
import time


#DEFINING OBJECTS

screen = {
"dim": np.array([800,800]), #in pixels
"real_dim": np.array([50,50]), #in meters
}
screen["scale_dim"] = screen['dim']/screen['real_dim'] #sets the scale width and height by dividing the screen dimensions by the real dimensions

ball = { #defines settings for ball in meters
"pos": screen['real_dim']/2,
"vel":np.array([15*cos(pi/6), 10*sin(pi/6)]),
"accel":np.array([0,0]),
"radius":1,
"mass":0.454,
"fnet":np.array([0,0])
}


#SETTING CONSTANTS

dt = 0
speed = 3
t = 0
g = 9.81
k = 1 #spring constant
mew = 1 #friction constant


#DEFINING VARIOUS MATH FUNCTIONS

def integral(func, tt,last): #integral estimation (currently using RK4)
    k1 = func(tt,last)
    k2 = func(tt*dt/2,last+dt*k1/2)
    k3 = func(tt*dt/2,last+dt*k2/2)
    k4 = func(tt + dt,last+dt*k3)
    return ((dt/6)*(k1+2*k2+2*k3+k4))

def second_integral(v, vf): #calculates area of trapezoid with base1 = v and base2 = vf
    return ((v+vf)*(dt/2))

def in_between(b1,b2,p):
    return b1 < p < b2 or b2 < p < b1

def point_bounds_distance(point,bound1,bound2): #calculates the distance between a point and the line between the 2 bounds. looks complicated but is pretty simple point-line distance math
    if bound1[0] == bound2[0]:
        if in_between(bound1[1],bound2[1],point[1]):
            return abs(point[0]-bound1[0])
    else:
        if bound1[1] == bound2[1]:
            if in_between(bound1[0],bound2[0],point[0]):
                return abs(point[1]-bound1[1])
        else:
            bslope = (bound2[1]-bound1[1])/(bound2[0]-bound1[0])
            yb0 = bound1[1]-bslope*bound1[0]
            pslope = -1/bslope
            yp0 = point[1]-pslope*point[0]
            xint = (yp0-yb0)/(bslope-pslope)
            yint = bslope*xint+yb0
            if in_between(bound1[1], bound2[1], yint) and in_between(bound1[0], bound2[0], xint):
                return sqrt((point[1]-yint)**2+(point[0]-xint)**2)


#DEFINING MOVEMENT FUNCTIONS

def force(tt,vel):
    global ball
    return(np.array([0,-ball['mass']*g]))

def circle(cpos, r, n): #creates a circle by making a polygon with n sides where each vertex is r distance from cpos
    glBegin(GL_POLYGON) #tells OpenGL to start drawing a polygon
    da = 2*pi/n #sets the change in angle in every for loop iteration to 2pi/n
    alpha = 0 #sets the angle to 0
    for i in range(n): #iterates through n times and puts a vertex that is r distance from the center and da radians from the last vertex
        unit_vec = np.array([cos(alpha),sin(alpha)])
        glVertex2f(*(cpos+r*unit_vec))
        alpha += da
    glEnd()

def update_pos(): #this function updates the position of the ball. position is updated before velocity within this function because the change in position needs to account for the previous velocity
    global ball, ball_loc
    delta_v = integral(force,t,ball['vel'])/ball['mass']
    ball['accel'] = force(t,ball['vel'])/ball['mass']
    ball['pos'] = ball['pos'] + second_integral(ball['vel'], ball['vel']+delta_v)
    ball['vel'] = ball['vel'] + delta_v
    if list_on:
        ball_loc = np.append(ball_loc, [screen['scale_dim']*ball['pos']], axis = 0) #stores current position in loc list
    circle(screen['scale_dim']*ball['pos'],screen['scale_dim'][0]*ball['radius'], 15)


#DEFINING COLLISION FUNCTIONS

collision = False
col_list = []

def bounce_vector(v,ba):
    global k, mew
    ca = atan2(v[1],v[0])
    n = (cos(ba+pi/2),sin(ba+pi/2)) if ba<ca<pi+ba else (cos(ba-pi/2),sin(ba-pi/2))
    u = np.multiply(n,np.dot(v,n))
    w = np.subtract(v,u)
    return np.subtract(mew*w,k*u)

def collision_behavior(ba):
    global ball
    ball['vel'] = bounce_vector(ball['vel'],ba)

def check_collision():
    global collision, ball, col_list
    col_list.append(collision)
    if len(col_list) > 3:
        del col_list[0]
    collision = False
    for i in range(len(bounds)):
        if i == len(bounds)-1:
            next = 0
        else:
            next = i+1
        distance = point_bounds_distance(screen['scale_dim']*ball['pos'], bounds[next], bounds[i])
        bound_angle = atan2((bounds[next][1]-bounds[i][1]),(bounds[next][0]-bounds[i][0]))
        if distance != None:
            if distance <= screen['scale_dim'][0]*ball['radius'] and not any(col_list):
                #print('hit')
                collision = True
                ball['pos'] += (ball['radius']-distance/screen['scale_dim'][0])*np.array([cos(bound_angle-pi/2),sin(bound_angle-pi/2)])
                collision_behavior(bound_angle)
                break


#DEFINING FUNCTION TO CREATE A TRAIL

trail_on = True #CAUSES LOTS OF LAG IF LEFT ON FOR MORE THAN A MINUTE. DT OVER 100 CAUSES AWFUL LAG!!!! NEVER USE!!
list_on = False #CAUSES MINOR LAG DEPENGING ON DT VALUE
if list_on or trail_on:
    list_on = True
    ball_loc = [ball['pos']*screen['scale_dim']]

def trail(list):
    glBegin(GL_POINTS)
    for pos in list:
        glVertex2f(*pos)
    glEnd()


#DEFINING FUNCTIONS FOR OPENGL TO USE

def gl_stupid(): #NO IDEA WHAT HALF THIS DOES! SOMETHING WITH BUFFERS AND MATRICES
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, *screen['dim'])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, screen['dim'][0], 0.0, screen['dim'][1], 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()


#DEFINING THE BOUNDS

bounds=[]
def polygon_bounds(center, sides, radius):
    da = 2*pi/sides #sets the change in angle in every for loop iteration to 2pi/n
    alpha = 0 #sets the angle to 0
    for i in range(sides): #iterates through n times and puts a vertex that is r distance from the center and da radians from the last vertex
        bounds.append((round(center[0]+cos(alpha)*radius, 4),round(center[1]+sin(alpha)*radius, 4)))
        alpha += da

polygon_bounds(screen['dim']/2,8,screen['dim'][0]/2 - 10)
#bounds = [(10,10), (10,h-10), (w-10,h-10), (w-10,10)]
#bounds = [(w/2,10),(10,h/2),(w/2,h-10),(w-10,h/2)]

def create_bounds():
    glBegin(GL_LINE_LOOP)
    for bound in bounds:
        glVertex2f(*bound)
    glEnd()


#CREATING WINDOW AND DISPLAYING GRAPHICS WITH PYGAME + OPENGL

def main():
    global t, dt, screen
    pg.init()
    pg.display.set_mode(tuple(screen['dim']), DOUBLEBUF|OPENGL)
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
        gl_stupid()
        create_bounds()
        check_collision()
        update_pos()
        if trail_on:
            trail(ball_loc)
        glColor3f(1.0, 0.0, 0.0)
        dt = speed*clock.tick()/1000
        fps = (1/dt if dt != 0 else 0)
        pg.display.flip()
        t += dt

if __name__ == "__main__":
    main()
