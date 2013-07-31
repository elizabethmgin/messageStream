import os, sys; sys.path.insert(0, os.path.join("..",".."))

from nodebox.graphics import * 
from nodebox.graphics.geometry import distance, angle, smoothstep

from random import seed
from math import sin,cos


# Define our own circle method (NodeBox doesn't have one)
# that draws from the center.
def circle(x, y, size):
   oval(x-size/2, y-size/2, size, size)

# The main actor in the animation is a Ball. 
# A Ball has a set of state values: its position, size, color and delta-values.
# The delta-values affect the position and size, and are a simple way to give
# each ball "character". Higher delta-values make the ball more hectic.
class Ball:
   # Initialize a ball -- set all the values to their defaults.
   def __init__(self):
       self.x = random(canvas.width-100)
       self.y = random(canvas.height)
       self.size = random(10, 72)
       self.dx = self.dy = self.ds = 0.0
       self.color = color(random(), 1, random(0,2), random())

   # Update the internal state values.
   def update(self):
       self.dx = sin(canvas.frame/float(random(1,100))) * 20.0
       self.dy = cos(canvas.frame/float(random(1,100))) * 20.0
       self.ds = cos(canvas.frame/float(random(1,123))) * 10.0
       self.color = color(random(), random(), random(0,2), random())
   
   # Draw a ball: set the fill color first and draw a circle.
   def draw(self):
       fill(self.color)
       circle(self.x + self.dx, self.y + self.dy, self.size + self.ds)

balls = []
def setup(canvas):
   global balls; balls = []
   for i in range(30):
       balls.append(Ball())

def draw(canvas):
    background(1)
    global balls
    seed(1)
    translate(100, canvas.height-canvas.frame)
    for ball in balls:
        ball.update()
        ball.draw()

canvas.fps = 30
canvas.size = 1080, 764
canvas.run(draw, setup)
