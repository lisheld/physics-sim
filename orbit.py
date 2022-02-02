#IMPORTING PACKAGES

import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import numpy as np
from numpy.linalg import *
import pandas as pd
import time


#DEFINING OBJECTS

screen = {
"dim": np.array([800,800]), #in pixels
"real_dim": np.array([11*6371*10**3,11*6371*10**3]), #in meters
}
screen["scale_dim"] = screen['dim']/screen['real_dim'] #sets the scale width and height by dividing the screen dimensions by the real dimensions

earth = {
"mass": 5.9734*10**24,
"radius": 6371*10**3,
"pos": screen['real_dim']/2,
}

moon = { #defines settings for moon in meters
"pos": earth['pos']+np.array([1.25*6371*10**3,0]),
"vel":np.array([0,9000]),
"accel":np.array([0,0]),
"radius":1737.4*10**3,
"mass":0.07346*10**24
}
earth['radius']

#SETTING CONSTANTS

dt = 0
speed = 1000
t = 0
g = 9.81
G = 6.67430*(10**(-11))


#DEFINING VARIOUS MATH FUNCTIONS

def integral(func,tt,last): #integral estimation (currently using RK4)
    k1 = func(tt,last)
    k2 = func(tt*dt/2,last+dt*k1/2)
    k3 = func(tt*dt/2,last+dt*k2/2)
    k4 = func(tt + dt,last+dt*k3)
    return ((dt/6)*(k1+2*k2+2*k3+k4))

def second_integral(v, vf): #calculates area of trapezoid with base1 = v and base2 = vf
    return ((v+vf)*(dt/2))

def in_between(b1,b2,p):
    return b1 < p < b2 or b2 < p < b1


#DEFINING MOVEMENT FUNCTIONS

def force(tt,vel):
    global earth, moon, G
    r_vec = earth['pos']-moon['pos']
    mag = norm(r_vec)
    unit_vec = r_vec/mag
    #print((G*earth['mass']/(mag**2))*unit_vec)
    return((G*earth['mass']*moon['mass']/(mag**2))*unit_vec)

def circle(cpos, r, n): #creates a circle by making a polygon with n sides where each vertex is r distance from (cx,cy)
    glBegin(GL_POLYGON) #tells OpenGL to start drawing a polygon
    da = 2*pi/n #sets the change in angle in every for loop iteration to 2pi/n
    alpha = 0 #sets the angle to 0
    for i in range(n): #iterates through n times and puts a vertex that is r distance from the center and da radians from the last vertex
        unit_vec = np.array([cos(alpha),sin(alpha)])
        glVertex2f(*(cpos+r*unit_vec))
        alpha += da
    glEnd()

def update_pos(): #this function updates the position of the moon. position is updated before velocity within this function because the change in position needs to account for the previous velocity
    global moon, earth, t
    delta_v = integral(force,t,moon['vel'])/moon['mass']
    moon['accel'] = force(t,moon['vel'])/moon['mass']
    moon['pos'] = moon['pos'] + second_integral(moon['vel'], moon['vel']+delta_v)
    moon['vel'] = moon['vel'] + delta_v
    if list_on and dt != 0:
        if (t/dt)%100==0:
            moon_loc.append(screen['scale_dim']*moon['pos']) #stores current position in loc list
    earth['pos'] = screen['real_dim']/2
    circle(screen['scale_dim']*moon['pos'],screen['scale_dim'][0]*moon['radius'], 20) #draws the moon at the current position
    circle(screen['scale_dim']*earth['pos'],screen['scale_dim'][0]*earth['radius'], 35) #draws the earth at the current position


#DEFINING FUNCTION TO CREATE A TRAIL

trail_on = True #CAUSES LOTS OF LAG IF LEFT ON FOR MORE THAN A MINUTE. DT OVER 100 CAUSES AWFUL LAG!!!! NEVER USE!!
list_on = False #CAUSES MINOR LAG DEPENGING ON DT VALUE
if list_on or trail_on:
    list_on = True
    moon_loc = [moon['pos']*screen['scale_dim']]

def trail(list):
    glBegin(GL_POINTS)
    for i in range(len(list)):
        glVertex2f(*list[i])
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


#CREATING WINDOW AND DISPLAYING GRAPHICS WITH OPENGL

def main():
    global t, dt, screen, speed
    pg.init()
    pg.display.set_mode(tuple(screen['dim']), DOUBLEBUF|OPENGL)
    clock = pg.time.Clock()
    zoom = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.MOUSEWHEEL:
                zoom = event.y
                #screen['real_dim'] = screen['real_dim']*(1-zoom*0.25)
        gl_stupid()
        update_pos()
        if trail_on:
            trail(moon_loc)
        glColor3f(1.0, 0.0, 0.0)
        dt = speed*clock.tick()/1000
        fps = (1/dt if dt != 0 else 0)
        pg.display.flip()
        t += dt

if __name__ == "__main__":
    main()
