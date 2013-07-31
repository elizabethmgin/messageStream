# Add the upper directory (where the nodebox module is) to the search path.
import os, sys; sys.path.insert(0, os.path.join("..",".."))

from nodebox.graphics import * 
from nodebox.graphics.geometry import distance, angle, smoothstep
from peewee import *
from random import seed
from math import sin, cos
import datetime, time

ROLE_USER = 0
ROLE_ADMIN = 1

DATABASE = '../_databaseFiles/Uganda07222013.db'
database = SqliteDatabase(DATABASE, threadlocals=True)
database.connect()

class BaseModel(Model):
    class Meta:
        database = database
        
class User(BaseModel):
    username = CharField()
    password = CharField()
    email = CharField(null=True)
    role = IntegerField(default=ROLE_USER)
    createdAt = DateTimeField(default=datetime.datetime.now)
    modifiedAt = DateTimeField(default=datetime.datetime.now)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
        
    def get_id(self):
           return self.id
    
    def __unicode__(self):
        return 'User: %s' % (self.username)

    class Meta:
            order_by = ('username',)
        
class Market(BaseModel):
    name = CharField(index=True)
    nickname = CharField(null=True)
    neighborhood = CharField(null=True)
    city = CharField(null=True)
    createdAt = DateTimeField(default=datetime.datetime.now)
    modifiedAt = DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return '%s located in %s, %s' % (self.name, self.neighborhood, self.city)
    class Meta:
            order_by = ('name',)
            
class Seller(BaseModel):
    givenName = CharField(null=True)
    familyName = CharField(null=True)
    kind = CharField(null=True)
    product = CharField(null=True)
    location = CharField(null=True)
    gender = CharField(null=True)
    birthDate = DateField(null=True)
    homeVillage = CharField(null=True)
    townVillage = CharField(null=True)
    language = CharField(null=True, index=True)
    phoneType = CharField(null=True)
    market = ForeignKeyField(Market, null=True, index=True)
    createdAt = DateTimeField(default=datetime.datetime.now)
    modifiedAt = DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return '%s %s sells %s' % (self.givenName, self.familyName, self.product)
    class Meta:
            order_by = ('-createdAt',)
                    
class Number(BaseModel):
    number = IntegerField(index=True)
    isActive = BooleanField(default=True)
    seller = ForeignKeyField(Seller, related_name="sellerNumbers", null=True, index=True)
    market = ForeignKeyField(Market, related_name="marketNumbers", null=True, index=True)
    user = ForeignKeyField(User, related_name="userNumbers", null=True, index=True)
    createdAt = DateTimeField(default=datetime.datetime.now)
    modifiedAt = DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return '%s : %s' % (self.createdAt, self.number)
    class Meta:
            order_by = ('-createdAt',)

class SMS(BaseModel):
    sms_id = IntegerField()
    body = CharField()
    date = DateTimeField()
    number = ForeignKeyField(Number, related_name='messages', index=True)
    createdAt = DateTimeField(default=datetime.datetime.now)
    modifiedAt = DateTimeField(default=datetime.datetime.now)
    #{u'read' : u'0', u'body' : u'Hi', u'_id': u'2551', u'date': u'1368211515895', u'address': u'+16266767023'}

    def __unicode__(self):
        return '%s // %s // %s' % (self.createdAt, self.number, self.body)
    class Meta:
            order_by = ('-createdAt',)
            
class List(BaseModel):
    name = CharField(null=True, index=True)
    seller = ForeignKeyField(Seller, null=True, index=True)
    market = ForeignKeyField(Market, null=True, index=True)
    createdAt = DateTimeField(default=datetime.datetime.now)
    modifiedAt = DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return '%s' % (self.name)
    class Meta:
            order_by = ('name',)
            
class ListRelationship(BaseModel):
    listName = ForeignKeyField(List, index=True)
    number = ForeignKeyField(Number, index=True)
    isActive = BooleanField(default=True)
    confirmed = IntegerField(default=3)
    status = CharField(default='confirmed')
    createdBy = ForeignKeyField(Number, index=True)
    modifiedBy = ForeignKeyField(Number, index=True)
    createdAt = DateTimeField(default=datetime.datetime.now)
    modifiedAt = DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return '%s : %s : %s' % (self.listName, self.number, self.isActive)
    class Meta:
            order_by = ('listName',)
    
class Outbox(BaseModel):
    number = ForeignKeyField(Number)
    body = CharField()
    sent = BooleanField(default=False)
    createdAt = DateTimeField(default=datetime.datetime.now)
    modifiedAt = DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return '%s // %s // %s // %s' % (self.sent, self.createdAt, self.number, self.body)
    class Meta:
            order_by = ('-sent',)


# Circle-packing algorithm.
# This script was used to produce one of the panels in NANOPHYSICAL:
# http://nodebox.net/code/index.php/Nanophysical

def circle(x, y, size):
   oval(x-size/2, y-size/2, size, size)

class Circle:
    
    def __init__(self, x, y, radius, sms_id):
        """ An object that can be passed to pack(), 
            with a repulsion radius and an image to draw inside the radius.
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.width = random(10,72)
        self.sms_id = sms_id
        self.goal = Point(x,y)
        self.color = color(random(), 1, random(0,2), 1.0)
        self.sms = SMS.get(SMS.id == self.sms_id)
        self.number = Number.get(Number.number == self.sms.number.number)
        self.body = str(self.sms.body)
        self.date = str(self.sms.createdAt)[:10]
        self.message = ''
       
    def contains(self, x, y):
        return distance(self.x, self.y, x, y) <= self.radius
        
    def form_Message(self):
           if self.number.seller:
               givenName = str(self.number.seller.givenName)
               familyName = str(self.number.seller.familyName)
               name = givenName + ' ' + familyName
               self.message = self.date + '\n' + str(name) + ' agamba: "' + self.body + '"'
           else:
               self.message = self.date + '\n"' + self.body + '"'
           return self.message
        
    def draw(self):
        # fill(self.color)
        # circle(self.x, self.y, self.size)
        text(self.message, x=self.x, y=self.y, width=self.width,
               font = "Droid Serif", 
               fontsize = 12, 
               fontweight = BOLD,
               lineheight = 1.9,
               fill = self.color)
        a = angle(self.x, self.y, self.goal.x, self.goal.y)
        r = self.radius * 1.25 # Let the cells overlap a little bit.
        push()
        translate(self.x, self.y)
        scale(r*2 / min(5, 5))
        rotate(a)
        # image(self.image, x=-r, y=-r) # Rotate from image center.
        pop()
        
global SMS_ID_LIST        
SMS_ID_LIST = []
for sms in SMS.select().order_by(SMS.createdAt):
    if (sms.number.number != 180):
        if (sms.number.number != 0):
            if (sms.number.number != 256774712133):
                if (sms.number.number != 14845575821):
                    sms_list = []
                    sms_list.append(sms.id)
                    sms_list.append(sms.createdAt)
                    SMS_ID_LIST.append(sms_list)
                else:
                    print '14845575821'
            else:
                print '256774712133'
        else:
            print '0'
    else:
        print '180'
print SMS_ID_LIST
 
def pack(circles, x, y, padding=2, exclude=[]):
    """ Circle-packing algorithm.
        Groups the given list of Circle objects around (x,y) in an organic way.
    """
    # Ported from Sean McCullough's Processing code:
    # http://www.cricketschirping.com/processing/CirclePacking1/
    # See also: http://en.wiki.mcneel.com/default.aspx/McNeel/2DCirclePacking
    
    # Repulsive force: move away from intersecting circles.
    for i, circle1 in enumerate(circles):
        for circle2 in circles[i+1:]:
            d = distance(circle1.x, circle1.y, circle2.x, circle2.y)
            r = circle1.radius + circle2.radius + padding
            if d < r - 0.01:
                dx = circle2.x - circle1.x
                dy = circle2.y - circle1.y
                vx = (dx / d) * (r-d) * 0.5
                vy = (dy / d) * (r-d) * 0.5
                if circle1 not in exclude:
                    circle1.x -= vx
                    circle1.y -= vy
                if circle2 not in exclude:
                    circle2.x += vx
                    circle2.y += vy
    
    # Attractive force: move all circles to center.
    for circle in circles:
        circle.goal.x = x
        circle.goal.y = y
        if circle not in exclude:
            damping = circle.radius ** 3 * 0.000001 # Big ones in the middle.
            vx = (circle.x - x) * damping
            vy = (circle.y - y) * damping
            circle.x -= vx
            circle.y -= vy

def cell(t):
    # Returns a random PNG-image from cells/
    # Some cells occur more frequently than others:
    # t is a number between 0.0 and 1.0 that determines which image to pick.
    # This is handy when combined with smoothstep(), 
    # then we can put a preference on empty blue cells,
    # while still ensuring that some of each cell appear.
    if t < 0.4: 
        img = choice([
            "green-empty1.png", 
            "green-empty2.png", 
            "green-empty3.png"] + [
            "green-block1.png", 
            "green-block2.png"] * 2)
    elif t < 0.5: 
        img = choice([
            "green-circle1.png", 
            "green-circle2.png"])
    elif t < 0.6: 
        img = choice([
            "green-star1.png", 
            "green-star2.png"])
    else: 
        img = choice([
            "blue-block.png",
            "blue-circle.png",
            "blue-star.png"] + [
            "blue-empty1.png", 
            "blue-empty2.png"] * 5)
    return Image(os.path.join("_images/cells", img))

circles = []
def setup(canvas):
    index = 0
    global circles; circles = []
    max_index = len(SMS_ID_LIST) - 1
    for sms in SMS_ID_LIST:
        if index < max_index:
        # Create a group of n cells.
        # Smoothstep yields more numbers near 1.0 than near 0.0, 
        # so we'll got mostly empty blue cells.
            t = smoothstep(0, max_index, index)
            sms_id = SMS_ID_LIST[index][0]
            message = Circle(x = random(-100), # Start offscreen to the left.
                   y = random(canvas.height), 
              radius = 10 + 0.5 * t*index, sms_id=sms_id)
            message.form_Message()
            circles.append(message)
            index += 1
        else:
            t = smoothstep(0, max_index, index)
            sms_id = SMS_ID_LIST[max_index][0]
            message = Circle(x = random(-100), # Start offscreen to the left.
                   y = random(canvas.height), 
              radius = 10 + 0.5 * t*index, sms_id=sms_id)
            message.form_Message()
            circles.append(message)
            

dragged = None
def draw(canvas):
    
    background(1)
    
    # Cells can be dragged:
    global dragged
    if dragged:
        dragged.x = canvas.mouse.x
        dragged.y = canvas.mouse.y
    if not canvas.mouse.pressed:
        dragged = None
    elif not dragged:
        for circle in circles:
            if circle.contains(canvas.mouse.x, canvas.mouse.y): 
                dragged = circle; break
    
    for circle in circles:
        circle.draw()
    
    pack(circles, 600, 600, exclude=[dragged])
     
canvas.size = 1080, 764
canvas.run(draw, setup)