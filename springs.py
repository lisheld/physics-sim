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

### ADD OTHER OBJECTS HERE -- MAKE SURE TO CTRL-F AND REPLACE BALL WITH WHATEVER YOU MAKE###
block1 = {
"pos": screen['real_dim']/2,
"vel": np.array([-5,0]),
"accel": np.array([0,0]),
"mass": 1
}
block2 = {
"pos": screen['real_dim']/2 - 10,
"vel": np.array([0,0]),
"accel": np.array([0,0]),
"mass": 1
}


#SETTING CONSTANTS

dt = 0
speed = 1
t = 0
elastic = 1
mew = 0
k = 220



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

def distance(p1,p2):
    return sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)

#DEFINING COLLISION FUNCTIONS

collision = False
col_list = []

def bounce_vector(v,ba):
    global elastic, mew
    ca = atan2(v[1],v[0])
    n = np.array([cos(ba+pi/2),sin(ba+pi/2)]) if ba<ca<pi+ba else np.array([cos(ba-pi/2),sin(ba-pi/2)])
    u = n*np.dot(v,n)
    w = v - u
    return(mew*w-elastic*u)

def collision_behavior(ba):
    global ball
    ball['vel'] = bounce_vector(ball['vel'],ba)

def check_collision():
    global collision, elastic, block1, block2
    if distance(block1['pos'],block2['pos']) <= block


#DEFINING MOVEMENT FUNCTIONS

def force(tt,vel):
    global ball
    return(np.array([0,-ball['mass']*g]))

def polygon(cpos, r, n, alpha): #creates a circle by making a polygon with n sides where each vertex is r distance from cpos
    glBegin(GL_POLYGON) #tells OpenGL to start drawing a polygon
    da = 2*pi/n #sets the change in angle in every for loop iteration to 2pi/n
    for i in range(n): #iterates through n times and puts a vertex that is r distance from the center and da radians from the last vertex
        unit_vec = np.array([cos(alpha),sin(alpha)])
        glVertex2f(*(cpos+r*unit_vec))
        alpha += da
    glEnd()

def update_pos(object): #this function updates the position of the ball. position is updated before velocity within this function because the change in position needs to account for the previous velocity
    global ball_loc
    delta_v = integral(force,t,object['vel'])/object['mass']
    object['accel'] = force(t,object['vel'])/object['mass']
    object['pos'] = object['pos'] + second_integral(object['vel'], object['vel']+delta_v)
    object['vel'] = object['vel'] + delta_v
    if list_on:
        ball_loc = np.append(ball_loc, [screen['scale_dim']*object['pos']], axis = 0) #stores current position in loc list
    polygon(screen['scale_dim']*object['pos'],screen['scale_dim'][0]*object['radius'], 4, pi/4)


#DEFINING FUNCTION TO CREATE A TRAIL

trail_on = False #CAUSES LOTS OF LAG IF LEFT ON FOR MORE THAN A MINUTE. DT OVER 100 CAUSES AWFUL LAG!!!! NEVER USE!!
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


#CREATING WINDOW AND DISPLAYING GRAPHICS WITH PYGAME + OPENGL

def main():
    global t, dt, screen, ball, collisions
    pg.init()
    pg.display.set_mode(tuple(screen['dim']), DOUBLEBUF|OPENGL)
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                actual_loc = np.array([event.pos[0],screen['dim'][1] - event.pos[1]])
                ball['accel'] = (force(t, ball['vel'])/ball['mass'])
                ball['vel'] = (actual_loc/screen['scale_dim'] - ball['pos']) - 0.5 * ball['accel']
        gl_stupid()
        create_bounds()
        check_collision()
        update_pos(block)
        if trail_on:
            trail(ball_loc)
        glColor3f(1.0, 0.0, 0.0)
        dt = speed*clock.tick()/1000
        fps = (1/dt if dt != 0 else 0)
        pg.display.flip()
        t += dt

if __name__ == "__main__":
    main()
