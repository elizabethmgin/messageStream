# Add the upper directory (where the nodebox module is) to the search path.
import os, sys; sys.path.insert(0, os.path.join("..",".."))

from nodebox.graphics import *
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

global WIDTH
global HEIGHT
WIDTH = 1680
HEIGHT = 1050
global FRAME
FRAME = canvas.frame       
            
class Message(object):
   def __init__(self, sms_id):
       self.width = 1000
       self.x = 300
       self.y = 900
       self.dx = self.dy = 0.0
       self.color = color(1, random(100, 110), random(100,110), .9)
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
           self.message = self.date + '\n' + str(name) + ' agamba: "' + self.body + '"'
       else:
           self.message = self.date + '\n"' + self.body + '"'
       return self.message
   
   def set_Rest(self, rest):
       self.rest = rest
       
   def update(self, y):
       self.y = y
       
   def white(self):
       self.color = color(255,255,255, 1.0)

   # Draw a ball: set the fill color first and draw a circle.
   def draw(self):
       text(self.message, x=self.x, y=self.y, width=self.width,
           font = "Droid Serif", 
           fontsize = 24, 
           fontweight = BOLD,
           lineheight = 1.9,
           fill = self.color)
    
def get_Image(sms_id):
    sms = SMS.get(SMS.id == sms_id)
    number = Number.get(Number.number == sms.number.number)
    seller = str(number.seller.givenName)
    path = "../_animationFiles/_images/" + seller + ".jpg"
    woman = Image(path)
    return woman  
    

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

global MESSAGE_LIST
MESSAGE_LIST = []
index = 0
max_index = len(SMS_ID_LIST) - 1
in_between = float(11839860)
for sms in SMS_ID_LIST:
    if index < max_index:
        sms_id = SMS_ID_LIST[index][0]
        current_sms_time = SMS_ID_LIST[index][1]
        print "CURRENT_SMS_TIME: " + str(current_sms_time)
        next_index = index + 1
        next_sms_time = SMS_ID_LIST[next_index][1]
        sms_interval_real = next_sms_time - current_sms_time
        print "SMS_INTERVAL_REAL: " + str(sms_interval_real)
        sms_interval_real_seconds = float(sms_interval_real.total_seconds())
        print "SMS_INTERVAL_REAL_SECONDS: " + str(sms_interval_real_seconds)
        sms_interval_fake = (sms_interval_real_seconds/in_between)*float(300)
        print "SMS_INTERVAL_FAKE: " + str(sms_interval_fake)
        message = Message(sms_id)
        message.form_Message()
        # R = (sms_interval_fake + 1) / 2 # bring everything closer to one second
        message.set_Rest(sms_interval_fake)
        print "MESSAGE REST: " + str(message.rest)
        MESSAGE_LIST.append(message)
        print "MESSAGE_LIST: " + str(MESSAGE_LIST)
        index += 1
    else:
        sms_id = SMS_ID_LIST[max_index][0]
        message = Message(sms_id)
        message.form_Message()
        message.set_Rest(sms_interval_fake)
        MESSAGE_LIST.append(message)
        print "MESSAGE_LIST: " + str(MESSAGE_LIST)
        
global ML_INDEX
global Y_MOVE
ML_INDEX = 0
Y_MOVE = 900
def draw(canvas):
    global MESSAGE_LIST
    global HEIGHT
    global FRAME
    global ML_INDEX
    global Y_MOVE
    seed(1)
    max_index = len(MESSAGE_LIST) - 1
    # translate(0, HEIGHT-FRAME)
    if ML_INDEX < max_index:
        if Y_MOVE < 0:
            print 'within if Y_MOVE < 0'
            canvas.clear()
            message = MESSAGE_LIST[ML_INDEX]
            message.draw()
            print 'should have drawn message'
            time.sleep(message.rest)
            print 'MESSAGE: ' + str(message.message)
            print 'REST: ' + str(message.rest)
            print 'done resting'
            ML_INDEX += 1
            Y_MOVE = 700
            print 'Y_MOVE: ' + str(Y_MOVE)
        elif Y_MOVE == 900:
            print 'within elif Y_MOVE == 900'
            message = MESSAGE_LIST[ML_INDEX]
            message.draw()
            print 'should have drawn message'
            time.sleep(message.rest)
            print 'MESSAGE: ' + str(message.message)
            print 'REST: ' + str(message.rest)
            print 'done resting'
            ML_INDEX += 1
            Y_MOVE -= 200
            print 'Y_MOVE: ' + str(Y_MOVE)
        else:
            print 'within else'
            message = MESSAGE_LIST[ML_INDEX]
            message.update(Y_MOVE)
            message.draw()
            print 'should have drawn message'
            time.sleep(message.rest)
            print 'MESSAGE: ' + str(message.message)
            print 'REST: ' + str(message.rest)
            print 'done resting'
            ML_INDEX += 1
            Y_MOVE -= 200
            print 'Y_MOVE: ' + str(Y_MOVE)
    else:
        canvas.clear()
        message = MESSAGE_LIST[max_index]
        message.draw()
        print 'should have drawn message'
        time.sleep(120)
        print 'done resting'
        sys.exit()
        

# canvas.fullscreen = True
# canvas.fps = 1
canvas.size = WIDTH, HEIGHT
canvas.run(draw)