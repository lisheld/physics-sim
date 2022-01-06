#poop
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import numpy as np
import pandas as pd
import time
w,h = 800,800
rw,rh = 25,25
sw,sh = w/rw,h/rh #sets the scale width and height by dividing the height in pixels by the height in meters
ball = {
"pos": [0,12.5],
"vel":10,
"angle":pi/3,
"radius":0.3,
"mass":0.454
}
bounds = [(10,10),(10,h-10),(w-10,h-10),(w-10,10)]
vx,vy,x,y=ball['vel']*cos(ball['angle']), ball['vel']*sin(ball['angle']), ball['pos'][0], ball['pos'][1]
dt = 1/100
t = 0
g = 9.81

def integral(tt,func): #integral estimation
    #print(x, ha)
    return (dt/6)*(func(tt)+4*func((2*tt+dt)/2)+func(tt+dt))

def second_integral(v, vf): #calculates area of trapezoid with base1 = v and base2 = vf
    return (v+vf/2)*dt



def point_bounds_distance(point,bound1,bound2): #calculates the distance between a point and the line between the 2 bounds. looks complicataed but is pretty simple point-line distance math
    if bound1[0] == bound2[0]:
        if (bound1[1] <= point[1] <= bound2[1]) or (bound2[1] <= point[1] <= bound1[1]):
            return abs(point[0]-bound1[0])
    elif bound1[1] == bound2[1]:
        if (bound1[0] <= point[0] <= bound2[0]) or (bound2[0] <= point[0] <= bound1[0]):
            return abs(point[1]-bound1[1])
    else:
        bslope = (bound2[1]-bound1[1])/(bound2[0]-bound1[0])
        yb0 = bound1[1]-bslope*bound1[0]
        pslope = -1/bslope
        yp0 = point[1]-pslope*point[1]
        xint = (yp0-yb0)/(bslope-pslope)
        yint = bslope*xint+yb0
        if ((bound1[1] <= yint <= bound2[1]) or (bound2[1] <= yint <= bound1[1])) and ((bound1[0] <= xint <= bound2[0]) or (bound2[0] <= xint <= bound1[0])):
            return abs(-bslope*point[0]+point[1]+bslope*bound1[0]-bound1[1])/sqrt(bslope**2 + 1)

def accel_y(t): #put function for y-acceleration as a function of time here
    #print("accel_y") #debugging
    return -g

def accel_x(t): #put function for x-acceleration as a function of time here
    #print("accel_x") #debugging
    return 0

def circle(cx, cy, r, n): #creates a circle by making a polygon with n sides where each vertex is r distance from (cx,cy)
    glBegin(GL_POLYGON) #tells OpenGL to start drawing a polygon
    da = 2*pi/n #sets the change in angle in every for loop iteration to 2pi/n
    alpha = 0 #sets the angle to 0
    for i in range(n): #iterates through n times and puts a vertex that is r distance from the center and da radians from the last vertex
        glVertex2f(cx+cos(alpha)*r, cy+sin(alpha)*r)
        alpha += da
    glEnd()

ball_loc = []

def update_pos(): #this function updates the position of the ball. position is updated before velocity within this function because the change in position needs to account for the previous velocity
    global x,y,vx,vy #imports global variables to function
    x += second_integral(vx, vx + integral(t, accel_x)) #updates x position
    vx += integral(t, accel_x) #updates the velocity in the x direction
    y += second_integral(vy, vy + integral(t, accel_y)) #updates y position
    vy += integral(t, accel_y) #updates the velocity in the y direction
    #print(sw*x,sh*y) #for debugging why the ball is in china
    ball_loc.append((sw*x,sh*y)) #stores current position in loc list
    circle(sw*x,sh*y, sh*ball['radius'], 30) #draws a circle at the current position

def create_bounds():
    glBegin(GL_LINE_LOOP)
    for bound in bounds:
        glVertex2f(bound[0], bound[1])
    glEnd()
intersect_angle = 0
col_list = []
def check_collision():
    global col_list, sh, ball
    col_list = []
    for i in range(len(bounds)):
        if i == len(bounds)-1:
            distance = point_bounds_distance(ball_loc[-1], bounds[i], bounds[0])
            tempia = atan((bounds[i][1]-bounds[0][1])/(bounds[i][0]-bounds[0][0])) #need to fix here to calculate angle properly
        else:
            distance = point_bounds_distance(ball_loc[-1], bounds[i], bounds[i+1])
            tempia = atan((bounds[i][1]-bounds[i+1][1])/(bounds[i][0]-bounds[i+1][0])) #need to fix here to calculate angle properly
        try:
            if distance <= sh*ball['radius']:
                col_list.append(True)
                intersect_angle = tempia
            else:
                col_list.append(False)
        except:
            col_list.append(False)

def collision_behavior():
    global vy, vx
    collision_angle = atan(vy/vx)
    bounce_angle = pi - (collision_angle - intersect_angle)
    vy = vy*sin(bounce_angle)
    vx = vx*cos(bounce_angle)



def trail(list):
    glBegin(GL_POINTS)
    for pos in list:
        glVertex2f(pos[0],pos[1])
    glEnd()

def iterate():
    glViewport(0, 0, w,h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, w, 0.0, h, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()


def showScreen():
    global t, dt, collision
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    create_bounds()
    update_pos()
    check_collision()
    trail(ball_loc)
    glColor3f(1.0, 0.0, 0.0)
    if any(col_list):
        collision_behavior()
    glutSwapBuffers()
    t += dt
    time.sleep(dt)



glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(w,h)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow("Physics Sim")
glutDisplayFunc(showScreen)
glutIdleFunc(showScreen)
glutMainLoop()
