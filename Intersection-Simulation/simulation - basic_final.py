import random
import time
import threading
import pygame
import sys

# next_green_signal= {0:20, 1:20, 2:20, 3:20}
default_green_duration= {0:6, 1:6, 2:6, 3:6}
default_red_duration= 150
default_yellow_duration= 4
signals= []
n_signals= 4
current_green_signal= 0
next_green_signal = (current_green_signal+1)% n_signals
is_current_signal_yellow=0
vehicle_speeds= {'car':5.25, 'bus':1.8, 'truck':1.8, 'bike':2.5}
total_vehicles_crossed=0
start = time.time()
total_waiting_time=0

x = {'right':[0,0], 'down':[550,510], 'left':[1000,1000], 'up':[415,455]}
y = {'right':[425,460], 'down':[0,0], 'left':[560,520], 'up':[1000,1000]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}

vehicleTypes = {0:'car'}

directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

signal_coordinates= [(360,300),(610,300),(610,635),(360,635)]

signal_timer_coordinates= [(360,280),(610,280),(610,615),(360,615)]

stop_line = {'right': 380, 'down': 380, 'left': 640, 'up': 640}

default_stop = {'right': 370, 'down': 370, 'left': 630, 'up': 630}

stopping_gap = 15

moving_gap = 25

pygame.init()
simulation = pygame.sprite.Group()

class signal: 
    def __init__(self, red, yellow, green):
        self.red= red
        self.yellow=yellow
        self.green=green
        self.timer=''

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicle_class, direction_number, direction,going):
        pygame.sprite.Sprite.__init__(self)
        self.rotationAngle=0
        self.going=going
        self.vip=0
        self.lane=lane
        self.vehicle_class=vehicle_class
        self.speed=vehicle_speeds[vehicle_class]
        self.direction_number=direction_number
        self.direction=direction
        self.x=x[direction][lane]
        self.y = y[direction][lane]
        self.previous_x=x[direction][lane]
        self.previuos_y=y[direction][lane]
        self.previous_time=time.time()
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        t= random.randint(1,4)
        path = "images/" + direction + "/" + vehicle_class + str(t) + ".png"
        self.image = pygame.image.load(path)

        if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed==0): 
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stopping_gap 
            elif (direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + stopping_gap
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stopping_gap
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stopping_gap
        else:
            self.stop = default_stop[direction]
        
        if(direction=='right'):
            temp = self.image.get_rect().width + stopping_gap    
            x[direction][lane] -= temp
        elif(direction=='left'):
            temp = self.image.get_rect().width + stopping_gap
            x[direction][lane] += temp
        elif(direction=='down'):
            temp = self.image.get_rect().height + stopping_gap
            y[direction][lane] -= temp
        elif(direction=='up'):
            temp = self.image.get_rect().height + stopping_gap
            y[direction][lane] += temp

        simulation.add(self)
    
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))


    def accelerate(self):
        global total_vehicles_crossed, total_waiting_time
        if(self.direction=='right'):
            if(self.crossed==0 and self.x+self.image.get_rect().width>stop_line[self.direction]):
                self.crossed = -1
                if(current_green_signal==0 and is_current_signal_yellow==0):
                    self.vip=1
            if self.crossed==-1 and current_green_signal==0 and is_current_signal_yellow==0:
                self.crossed=1
                total_vehicles_crossed+=1
            if self.vip==1 or ( (self.x+self.image.get_rect().width<=self.stop or self.crossed == 1 or (current_green_signal==0 and is_current_signal_yellow==0)) and (self.index==0 or self.x+self.image.get_rect().width <(vehicles[self.direction][self.lane][self.index-1].x - moving_gap))):
                if self.going is 'straight':
                    self.x += self.speed
                if self.going is 'right':
                    if self.x<stop_line[self.direction]:
                        self.x += self.speed
                    elif self.y>stop_line['up']:
                        self.y += self.speed
                        self.rotationAngle=-90
                    else:
                        total=stop_line['left']-stop_line['right']
                        left=stop_line['left']-self.x-50
                        ratio=left/total
                        self.rotationAngle=-90*(1-ratio)
                        if self.rotationAngle<-90: self.rotationAngle=-90
                        self.x += (self.speed*ratio)
                        self.y += (self.speed*(1-ratio))

                
        elif(self.direction=='down'):
            if(self.crossed==0 and self.y+self.image.get_rect().height>stop_line[self.direction]):
                self.crossed = -1
                if(current_green_signal==1 and is_current_signal_yellow==0):
                    self.vip=1
            if self.crossed==-1 and current_green_signal==1 and is_current_signal_yellow==0:
                self.crossed=1
                total_vehicles_crossed+=1
            if self.vip==1 or   ((self.y+self.image.get_rect().height<=self.stop or self.crossed == 1 or (current_green_signal==1 and is_current_signal_yellow==0)) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - moving_gap))):
                if self.going is 'straight':
                    self.y += self.speed
                if self.going is 'right':
                    if self.y<stop_line[self.direction]:
                        self.y += self.speed
                    elif self.x<stop_line['right']:
                        self.x -= self.speed
                        self.rotationAngle=-90
                    else:
                        total=stop_line['up']-stop_line['down']
                        left=stop_line['up']-self.y-50
                        ratio=left/total
                        self.rotationAngle=-90*(1-ratio)
                        if self.rotationAngle<-90: self.rotationAngle=-90
                        self.y += (self.speed*ratio)
                        self.x -= (self.speed*(1-ratio))

        elif(self.direction=='left'):
            if(self.crossed==0 and self.x<stop_line[self.direction]):
                self.crossed = -1
                if(current_green_signal==2 and is_current_signal_yellow==0):
                    self.vip=1
            if self.crossed==-1 and current_green_signal==2 and is_current_signal_yellow==0:
                self.crossed=1
                total_vehicles_crossed+=1
            if self.vip==1 or ((self.x>=self.stop or self.crossed == 1 or (current_green_signal==2 and is_current_signal_yellow==0)) and (self.index==0 or self.x >(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + moving_gap))):                
                if self.going is 'straight':
                    self.x -= self.speed
                if self.going is 'right':
                    if self.x>stop_line[self.direction]:
                        self.x -= self.speed
                    elif self.y<stop_line['down']:
                        self.y -= self.speed
                        self.rotationAngle=-90
                    else:
                        total=stop_line['left']-stop_line['right']
                        left=(self.x-stop_line['right'])
                        ratio=left/total
                        self.rotationAngle=-90*(1-ratio)
                        if self.rotationAngle<-90: self.rotationAngle=-90
                        self.x -= (self.speed*ratio)
                        self.y -= (self.speed*(1-ratio))

        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stop_line[self.direction]):
                self.crossed = -1
                if(current_green_signal==3 and is_current_signal_yellow==0):
                    self.vip=1
                    # print("vip treatment\n")
            if self.crossed==-1 and current_green_signal==3 and is_current_signal_yellow==0:
                self.crossed=1
                total_vehicles_crossed+=1
            if self.vip==1 or ((self.y>=self.stop or self.crossed == 1 or (current_green_signal==3 and is_current_signal_yellow==0)) and (self.index==0 or self.y >(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + moving_gap))):                
                if self.going is 'straight':
                    self.y -= self.speed
                if self.going is 'right':
                    if self.y>stop_line[self.direction]:
                        self.x -= self.speed
                    elif self.x>stop_line['left']:
                        self.x += self.speed
                        self.rotationAngle=-90
                    else:
                        total=stop_line['up']-stop_line['down']
                        left=(self.y-stop_line['down'])-50
                        ratio=left/total
                        self.rotationAngle=-90*(1-ratio)
                        if self.rotationAngle<-90: self.rotationAngle=-90
                        self.x -= (self.speed*ratio)
                        self.y += (self.speed*(1-ratio))
        if self.x== self.previous_x and self.y==self.previuos_y:
            total_waiting_time+= time.time()-self.previous_time
        self.previous_x=self.x
        self.previuos_y=self.y
        self.previous_time=time.time()


def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


def initialize():
    ts1 = signal(0, default_yellow_duration, default_green_duration[0])
    signals.append(ts1)
    ts2 = signal(ts1.yellow+ts1.green, default_yellow_duration, default_green_duration[1])
    signals.append(ts2)
    ts3 = signal(default_red_duration, default_yellow_duration, default_green_duration[2])
    signals.append(ts3)
    ts4 = signal(default_red_duration, default_yellow_duration, default_green_duration[3])
    signals.append(ts4)
    repeat()

def repeat():
    global current_green_signal, is_current_signal_yellow, next_green_signal
    while(signals[current_green_signal].green>0):
        updateValues()
        time.sleep(1)
    is_current_signal_yellow = 1   
    for i in range(0,3):
        for vehicle in vehicles[directionNumbers[current_green_signal]][i]:
            vehicle.stop=default_stop[directionNumbers[current_green_signal]]
    while(signals[current_green_signal].yellow>0):  
        updateValues()
        time.sleep(1)
    is_current_signal_yellow = 0  
    
    signals[current_green_signal].green = default_green_duration[current_green_signal]
    signals[current_green_signal].yellow = default_yellow_duration
    signals[current_green_signal].red = default_red_duration
       
    current_green_signal = next_green_signal 
    next_green_signal = (current_green_signal+1)%n_signals
    signals[next_green_signal].red = signals[current_green_signal].yellow+signals[current_green_signal].green
    repeat()

def updateValues():
    for i in range(0, n_signals):
        if(i==current_green_signal):
            if(is_current_signal_yellow==0):
                signals[i].green-=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

def generateVehicles():
    while(True):
        vehicle_type = 0
        lane_number = random.randint(0,1)
        going='straight'
        temp2= random.randint(0,1)
        if temp2 is 1 and lane_number is 1:
            going='right'
        temp = random.randint(0,99)
        direction_number = 0
        dist= [40,60,90,100]
        if(temp<dist[0]):
            direction_number = 0   
        elif(temp<dist[1]):
            direction_number = 1
        elif(temp<dist[2]):
            direction_number = 2
            going='straight'
        elif(temp<dist[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number],going)
        
        time.sleep(1)
        # print(vehicles)


class Main:
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    
    thread1.daemon = True
    thread1.start() 
    
    black = (0, 0, 0)
    white = (255, 255, 255) 
    screenWidth = 1000
    screenHeight = 1000
    screenSize = (screenWidth, screenHeight)
    background = pygame.image.load('images/intersection.png')
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)
    thread2 =   threading.Thread(name="generateVehicles",target=generateVehicles, args=())
    thread2.daemon = True
    thread2.start()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.blit(background,(0,0))   
        for i in range(0,n_signals):
            if(i==current_green_signal):
                if(is_current_signal_yellow==1):
                    signals[i].timer = signals[i].yellow
                    screen.blit(yellowSignal, signal_coordinates[i])
                else:
                    signals[i].timer = signals[i].green
                    screen.blit(greenSignal, signal_coordinates[i])
            else:
                if(signals[i].red<=10):
                    signals[i].timer = signals[i].red
                else:
                    signals[i].timer = "W"
                screen.blit(redSignal, signal_coordinates[i])
        timers = ["","","",""]
        for i in range(0,n_signals):  
            timers[i] = font.render(str(signals[i].timer), True, white, black)
            screen.blit(timers[i],signal_timer_coordinates[i])
        

        h = font.render('STATIC TRAFFIC SIGNAL', True, white, black)
        screen.blit(h,(700,200))

        t = font.render('Total vehicles crossed: '+str(total_vehicles_crossed), True, white, black)
        screen.blit(t,(60,200))

        current_time = time.time() -start
        seconds=int(current_time%60)
        minutes=int(current_time//60)
        time_string = font.render('Time elapsed: '+str(minutes)+' mins '+str(seconds)+' secs', True, white, black)
        screen.blit(time_string,(60,230))

        seconds=int(total_waiting_time%60)
        minutes=int(total_waiting_time//60)
        hours=minutes//60
        minutes=minutes%60
        if hours>0:
            w = font.render('TWaiting time: '+ str(hours) +'hrs'+ str(minutes)+' mins '+str(seconds)+' secs', True, white, black)
        elif minutes>0:
            w = font.render('TWaiting time: '+str(minutes)+' mins '+str(seconds)+' secs', True, white, black)
        else:
            w = font.render('TWaiting time: '+str(seconds)+' secs', True, white, black)
        screen.blit(w,(60,260))
        

        for vehicle in simulation:  
            if vehicle.going=='right':
                # screen.blit(rot_center(vehicle.image,vehicle.rotationAngle,vehicle.x, vehicle.y))
                blitRotateCenter(screen, vehicle.image, (vehicle.x,vehicle.y), vehicle.rotationAngle)
            else:
                screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.accelerate()
        pygame.display.update()


Main()