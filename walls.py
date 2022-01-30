from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import numpy as np
import pandas as pd
import time
w,h = 800,900 #in pixels
rw,rh = 50,50 #in meters
sw,sh = w/rw,h/rh #sets the scale width and height by dividing the height in pixels by the height in meters
ball = { #defines settings for ball in meters
"pos": (rw/2,rh/2),
"vel":(0,0),
"accel":(0,0),
"radius":0.3,
"mass":0.454
}
bounds = []
def polygon_bounds(center, sides, radius):
    da = 2*pi/sides #sets the change in angle in every for loop iteration to 2pi/n
    alpha = 0 #sets the angle to 0
    for i in range(sides): #iterates through n times and puts a vertex that is r distance from the center and da radians from the last vertex
        bounds.append((round(center[0]+cos(alpha)*radius, 4),round(center[1]+sin(alpha)*radius, 4)))
        alpha += da
polygon_bounds((w/2,h/2),8,w/2-10)
#bounds = [(10,10), (10,h-10), (w-10,h-10), (w-10,10)]
#bounds = [(w/2,10),(10,h/2),(w/2,h-10),(w-10,h/2)]

ball['vel'] = (15*cos(pi/6), 10*sin(pi/6))
dt = 1/500
t = 0
g = 9.81
collision = False
bound_angle = None
ball_loc = [(ball['pos'][0]*sw, ball['pos'][1]*sh)]
col_list = []
def integral(tt,func,last): #integral estimation (currently using RK4)
    out = []
    for i in range(len(func(1,last))):
        k1 = func(tt,last)[i]
        k2 = func(tt*dt/2,last[i]+dt*k1/2)[i]
        k3 = func(tt*dt/2,last[i]+dt*k2/2)[i]
        k4 = func(tt + dt,last[i]+dt*k3)[i]
        out.append((dt/6)*(k1+2*k2+2*k3+k4))
    return tuple(out)

def second_integral(v, vf): #calculates area of trapezoid with base1 = v and base2 = vf
    return (np.multiply(np.add(v,vf),(dt/2)))


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

def accel(t, vel):
    return(0,-g)

def circle(cpos, r, n): #creates a circle by making a polygon with n sides where each vertex is r distance from (cx,cy)
    glBegin(GL_POLYGON) #tells OpenGL to start drawing a polygon
    da = 2*pi/n #sets the change in angle in every for loop iteration to 2pi/n
    alpha = 0 #sets the angle to 0
    for i in range(n): #iterates through n times and puts a vertex that is r distance from the center and da radians from the last vertex
        glVertex2f(cpos[0]+r*cos(alpha), cpos[1]+r*sin(alpha))
        alpha += da
    glEnd()


def update_pos(): #this function updates the position of the ball. position is updated before velocity within this function because the change in position needs to account for the previous velocity
    global ball
    ball['pos'] = np.add(ball['pos'],second_integral(ball['vel'], np.add(ball['vel'], integral(t,accel,ball['vel']))))
    ball['vel'] = np.add(ball['vel'], integral(t,accel,ball['vel']))
    #print(sw*x,sh*y) #for debugging why the ball is in china
    #ball_loc.append(np.multiply((sw,sh),ball['pos'])) #stores current position in loc list
    circle(np.multiply(ball['pos'],(sw,sh)),sh*ball['radius'], 15) #draws a circle at the current position

def create_bounds():
    glBegin(GL_LINE_LOOP)
    for bound in bounds:
        glVertex2f(bound[0], bound[1])
    glEnd()

def check_collision():
    global collision, sh, ball, bound_angle, col_list
    col_list.append(collision)
    if len(col_list) > 3:
        del col_list[0]
    collision = False
    for i in range(len(bounds)):
        if i == len(bounds)-1:
            next = 0
        else:
            next = i+1
        distance = point_bounds_distance(np.multiply((sw,sh),ball['pos']), bounds[next], bounds[i])
        tempba = atan2((bounds[next][1]-bounds[i][1]),(bounds[next][0]-bounds[i][0]))
        if distance != None:
            if distance <= sh*ball['radius'] and not any(col_list):
                print('hit')
                bound_angle = tempba
                collision = True
                ball['pos'] = np.add(ball['pos'],np.multiply(ball['radius']-distance/sh,(cos(tempba-pi/2),sin(tempba-pi/2))))
                break

def bounce_vector(v,ba):
    ca = atan2(v[1],v[0])
    n = (cos(ba+pi/2),sin(ba+pi/2)) if ba<ca<pi+ba else (cos(ba-pi/2),sin(ba-pi/2))
    u = np.multiply(n,np.dot(v,n))
    w = np.subtract(v,u)
    return np.subtract(w,u) #coefficient of w changes friction, coefficient of u changes elasticity of ball

def collision_behavior():
    global ball, bound_angle
    ball['vel'] = bounce_vector(ball['vel'],bound_angle)

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
    if collision:
        collision_behavior()
    update_pos()
    check_collision()
    #trail(ball_loc)
    glColor3f(1.0, 0.0, 0.0)
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
