#IMPORTING PACKAGES

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
"real_dim": np.array([7*6371*10**3,7*6371*10**3]), #in meters
}
screen["scale_dim"] = screen['dim']/screen['real_dim'] #sets the scale width and height by dividing the screen dimensions by the real dimensions

earth = {
"mass": 5.9734*10**24,
"radius": 6371*10**3,
"pos": screen['real_dim']/2,
}

moon = { #defines settings for moon in meters
"pos": earth['pos']+3/16*screen['real_dim'],
"vel":np.array([0,0]),
"accel":np.array([0,0]),
"radius":1737.4*10**3,
"mass":0.07346*10**24
}


#SETTING CONSTANTS

dt = 1/100
t = 0
g = 9.81
G = 6.67430*10**(-11)


#DEFINING VARIOUS MATH FUNCTIONS

def integral(tt,func,last): #integral estimation (currently using RK4)
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

def accel(t, vel):
    global earth, moon, G
    r_vec = earth['pos']-moon['pos']
    mag = norm(r_vec)
    unit_vec = r_vec/mag
    return((G*earth['mass']/(mag**2))*unit_vec)

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
    moon['accel'] = integral(t,accel,moon['vel'])
    moon['pos'] = moon['pos'] + second_integral(moon['vel'], moon['vel']+moon['accel'])
    moon['vel'] = moon['vel'] + integral(t,accel,moon['vel'])
    if list_on:
        moon_loc.append(screen['scale_dim']*moon['pos']) #stores current position in loc list
    circle(screen['scale_dim']*moon['pos'],screen['scale_dim'][0]*moon['radius'], 15) #draws the moon at the current position
    circle(screen['scale_dim']*earth['pos'],screen['scale_dim'][0]*earth['radius'], 35) #draws the earth at the current position


#DEFINING FUNCTION TO CREATE A TRAIL

trail_on = False #CAUSES LOTS OF LAG IF LEFT ON FOR MORE THAN A MINUTE. DT OVER 100 CAUSES AWFUL LAG!!!! NEVER USE!!
list_on = False #CAUSES MINOR LAG DEPENGING ON DT VALUE
if list_on or trail_on:
    list_on = True
    moon_loc = [moon['pos']*screen['scale_dim']]

def trail(list):
    glBegin(GL_POINTS)
    for pos in list:
        glVertex2f(*pos)
    glEnd()


#DEFINING FUNCTIONS FOR OPENGL TO USE

def iterate():
    glViewport(0, 0, *screen['dim'])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, screen['dim'][0], 0.0, screen['dim'][1], 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    global t, dt, collision
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    update_pos()
    if trail_on:
        trail(moon_loc)
    glColor3f(1.0, 0.0, 0.0)
    glutSwapBuffers()
    t += dt
    time.sleep(dt)


#CREATING WINDOW AND DISPLAYING GRAPHICS WITH OPENGL

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(*screen['dim'])
glutInitWindowPosition(0, 0)
wind = glutCreateWindow("Physics Sim")
glutDisplayFunc(showScreen)
glutIdleFunc(showScreen)
glutMainLoop()
