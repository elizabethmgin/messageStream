# Add the upper directory (where the nodebox module is) to the search path.
import os, sys; sys.path.insert(0, os.path.join("..",".."))

from nodebox.graphics import *
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

# list of all sms ids
# index variable x = 0
# in ratio to time, 2-d list

def get_Message(sms_id):
    sms = SMS.get(SMS.id == sms_id)
    #number = Number.get(Number.number == sms.number.number)
    #seller = str(number.seller.givenName)
    body = str(sms.body)
    date = str(sms.createdAt)[:10]
    message = date + '\n"' + body + '"'
    txt = Text(message, 
        font = "Droid Serif", 
        fontsize = 30, 
        fontweight = BOLD,
        lineheight = 1.9,
        fill = color(0.25))
    return txt
    
def get_Image(sms_id):
    sms = SMS.get(SMS.id == sms_id)
    number = Number.get(Number.number == sms.number.number)
    seller = str(number.seller.givenName)
    path = "../_animationFiles/_images/" + seller + ".jpg"
    woman = Image(path)
    return woman    

SMS_ID_LIST = []
INDEX = 0
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
    
def draw(canvas):
    # for index in sms_id_list:
    global SMS_ID_LIST
    global INDEX
    max_index = len(SMS_ID_LIST) - 1
    in_between = float(11839860)
    if INDEX < max_index:
        canvas.clear()
        sms_id = SMS_ID_LIST[INDEX][0]
        current_sms_time = SMS_ID_LIST[INDEX][1]
        print "CURRENT_SMS_TIME: " + str(current_sms_time)
        next_index = INDEX + 1
        next_sms_time = SMS_ID_LIST[next_index][1]
        sms_interval_real = next_sms_time - current_sms_time
        print "SMS_INTERVAL_REAL: " + str(sms_interval_real)
        sms_interval_real_seconds = float(sms_interval_real.total_seconds())
        print "SMS_INTERVAL_REAL_SECONDS: " + str(sms_interval_real_seconds)
        sms_interval_fake = (sms_interval_real_seconds/in_between)*float(150)
        print "SMS_INTERVAL_FAKE: " + str(sms_interval_fake)
        txt = get_Message(sms_id)
        x = (canvas.width - textwidth(txt)) / 2
        y = 250
        txt.style(0, 10, fontsize=txt.fontsize/2, fontweight=NORMAL)
        text(txt, x, y)
        woman = get_Image(34)
        image(woman, x, y=400)
        INDEX += 1
        print "SMS_INTERVAL_FAKE: " + str(sms_interval_fake)
        time.sleep(sms_interval_fake)
    else:
        canvas.clear()
        sms_id = SMS_ID_LIST[max_index][0]
        txt = get_Message(sms_id)
        x = (canvas.width - textwidth(txt)) / 2
        y = 250
        txt.style(0, 10, fontsize=txt.fontsize/2, fontweight=NORMAL)
        text(txt, x, y)
        woman = get_Image(34)
        image(woman, x, y=400)
        time.sleep(20)

# canvas.fullscreen = True
canvas.size = 1680, 1050
# canvas.fps = 1
canvas.run(draw)