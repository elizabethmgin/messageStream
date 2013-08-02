import os, sys; sys.path.insert(0, os.path.join("..",".."))

from nodebox.graphics import * 
from nodebox.graphics.geometry import distance, angle, smoothstep

from random import seed
from math import sin,cos

from peewee import *
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
            
            
            


# Define our own circle method (NodeBox doesn't have one)
# that draws from the center.
def circle(x, y, size):
   oval(x-size/2, y-size/2, size, size)

# The main actor in the animation is a Message. 
# A Message has a set of state values: its position, size, color and delta-values.
# The delta-values affect the position and size, and are a simple way to give
# each message "character". Higher delta-values make the message more hectic.
class Message:
   # Initialize a message -- set all the values to their defaults.
   def __init__(self, sms_id):
       self.x = 300
       self.y = random(canvas.height)
       self.width = random(200, 300)
       self.height = 300
       self.dx = self.dy = self.dw = 0.0
       self.color = color(random(), 1, random(0,2), random())
       self.sms_id = sms_id
       self.sms = SMS.get(SMS.id == self.sms_id)
       self.number = Number.get(Number.number == self.sms.number.number)
       self.body = str(self.sms.body)
       self.date = str(self.sms.createdAt)[:10]
       self.message = ''
       self.rest = 0
       
   def form_Message(self):
          if self.number.seller:
              givenName = str(self.number.seller.givenName)
              familyName = str(self.number.seller.familyName)
              name = givenName + ' ' + familyName
              self.message = self.date + '\n' + str(name) + ' : "' + self.body + '"'
          else:
              self.message = self.date + '\n"' + self.body + '"'
          return self.message
   
   def set_Rest(self, rest):
       self.rest = rest
   
   def set_X(self, x):
          self.x = x
   
   # Update the internal state values.
   def update(self):
       #self.dx = self.dx+((random()*320)/300-2)
       #self.dy = self.dy+((random()*280)/300-2)
       self.dx = sin(canvas.frame/float(random(1,100))) * 20.0
       self.dy = cos(canvas.frame/float(random(1,100))) * 20.0
       self.dw = cos(canvas.frame/float(random(1,123))) * 10.0
       self.color = color(random(), random(), random(0,2), 1.0)
   
   # Draw a message: set the fill color first and draw a circle.
   def draw(self):
       # fill(self.color)
       text(self.message, x=(self.x + self.dx), y=(self.y + self.dy), width=(self.width + self.dw), font="Arial", fontsize=12, fontweight=BOLD, lineheight = 1.2, fill=self.color)
       
       
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
print len(SMS_ID_LIST)
max_index = len(SMS_ID_LIST)-1
first = SMS_ID_LIST[:30]
second = SMS_ID_LIST[30:60]
third = SMS_ID_LIST[60:90]
fourth = SMS_ID_LIST[90:120]
fifth = SMS_ID_LIST[120:150]
sixth = SMS_ID_LIST[150:180]
seventh = SMS_ID_LIST[180:max_index]

messages = []
index = 0
def setup(canvas):
   global messages
   global index
   max_index = len(SMS_ID_LIST) - 1
   in_between = float(11839860)
   for sms in SMS_ID_LIST:
       if index < max_index:
           sms_id = SMS_ID_LIST[index][0]
           current_sms_time = SMS_ID_LIST[index][1]
           next_index = index + 1
           next_sms_time = SMS_ID_LIST[next_index][1]
           sms_interval_real = next_sms_time - current_sms_time
           sms_interval_real_seconds = float(sms_interval_real.total_seconds())
           sms_interval_fake = (sms_interval_real_seconds/in_between)*float(300)
           message = Message(sms_id)
           message.form_Message()
           R = (sms_interval_fake + 1) / 2 # bring everything closer to one second
           message.set_Rest(R)
           messages.append(message)
           index += 1
       else:
           sms_id = SMS_ID_LIST[max_index][0]
           message = Message(sms_id)
           message.form_Message()
           message.set_Rest(20)
           messages.append(message)
           break
        
now = datetime.datetime.now()
def draw(canvas):
    background(1)
    global messages
    global now
    newNow = datetime.datetime.now()
    print newNow
    seed(1)
    translate(canvas.height-(canvas.frame*3), 100)
    for message in messages[:10]:
        message.update()
        message.draw()
    for message in messages[10:20]:
        message.set_X(500)
        message.update()
        message.draw()
    for message in messages[20:30]:
        message.set_X(700)
        message.update()
        message.draw()
    for message in messages[30:40]:
        message.set_X(900)
        message.update()
        message.draw()
    for message in messages[40:50]:
        message.set_X(1100)
        message.update()
        message.draw()
    for message in messages[50:60]:
        message.set_X(1300)
        message.update()
        message.draw()
    for message in messages[70:80]:
        message.set_X(1500)
        message.update()
        message.draw()
    # if canvas.height-(canvas.frame*3) < -600:
        # canvas.clear()

canvas.fps = 100
canvas.size = 1080, 764
canvas.run(draw, setup)
