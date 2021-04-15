import pygame
import threading
import random
import time
import sys
import socket

cycle=1
iteration=1
# setting default values for the green signal times
default_green_duration= {0:10, 1:10, 2:10, 3:10}
# setting default values for the red signal times
default_red_duration= 150
# setting default values for the yellow signal times
default_yellow_duration= 4
# array that will contain all the signal objects
signals= []
# variable to hold the number of signals used for running for loops over the signals
n_signals= 4
# variable that will store the index of the signal that is allocated green at the moment
current_green_signal= 0
# variable that will store the index of the signal that will be allocated green next for the moment
# by default initialized to next in order
next_green_signal = (current_green_signal+1)% n_signals
# variable that holds '0' when the current signal allotted green, is turned green and '1' when turned yellow
is_current_signal_yellow=0
# holds the speeds of the vehicles. (coordinate values will be incremented based on this every iteration)
vehicle_speeds= {'car':5.25}
# array that specifies which signals have been allotted green in a particular round
# so that every signal gets a chance before a signal is alloted again
flag=[1,0,0,0]
# calculated the number of cars going up that have not crossed the signal
cars_going_up=0
# varialbe that stores the number of vehicles crossed that is displayed in the simulation
total_vehicles_crossed=0
# records the start time of the simulation, used for calculaing the elapsed time
start = time.time()
# variable that stores the totol waiting time of all cars in the simulation
total_waiting_time=0

# specifies the coordinates that vehicles generated need to start from in the simulation
x = {'right':[0,0], 'down':[550,510], 'left':[1000,1000], 'up':[415,455]}
y = {'right':[425,460], 'down':[0,0], 'left':[560,520], 'up':[1000,1000]}

# holds the vehicle objects in each direction and in each lane
vehicles = {'right': {0:[], 1:[]}, 'down': {0:[], 1:[]}, 'left': {0:[], 1:[]}, 'up': {0:[], 1:[]}}

vehicle_type = {0:'car'}

directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# specifies the coordinates the where the signals needs to be placed in the simulation
signal_coordinates= [(360,300),(610,300),(610,635),(360,635)]

# specifies the coordinates the where the signal timers needs to be placed in the simulation
signal_timer_coordinates= [(360,280),(610,280),(610,615),(360,615)]

# specifies the stop line for each road, used for calculation to check if vehicle has crossed the signal
stop_line = {'right': 380, 'down': 380, 'left': 640, 'up': 640}

# specifies the coordinates where the vehicle needs to stop by default when the signal is red
default_stop = {'right': 370, 'down': 370, 'left': 630, 'up': 630}

# specifies the gap that vehicles need to maintain when stoped at a signal
stopping_gap = 15

# specifies the gap that vehicles need to maintain when moving 
moving_gap = 15

# initilizes the pygame simulation
pygame.init()
simulation = pygame.sprite.Group()

host = '127.0.0.1'
port = 12345
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host,port))

def client(n):
    message = str(n)
    s.send(message.encode('ascii'))
# definition of signal class
class signal: 
    def __init__(self, red, yellow, green):
        self.red= red
        self.yellow=yellow
        self.green=green
        self.timer=''

# definition of vehicle class 
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicle_class, direction_number, direction,going):
        pygame.sprite.Sprite.__init__(self)
        # specifies the moving angle, needed for when vehicles are turning right
        self.rotationAngle=0
        # specifies whether the vehicle is going straight or right
        self.going=going
        self.vip=0
        self.lane=lane
        self.vehicle_class=vehicle_class
        self.speed=vehicle_speeds[vehicle_class]
        self.direction_number=direction_number
        self.direction=direction

        # specifies the x coordinate 
        self.x=x[direction][lane]
        # specifies the y coordinate 
        self.y = y[direction][lane]

        # keeps track of the previous x and y coordinate values and time  needed for calculating the waiting time 
        self.previous_x=x[direction][lane]
        self.previuos_y=y[direction][lane]
        self.previous_time=time.time()

        # specifies if the vehicle has crossed or not
        # '0' for not crossed, '1' for crossed
        self.crossed = 0

        # appends this vehicle object to the behicles array that holds all vehicles
        vehicles[direction][lane].append(self)

        # keeps track of its position in the lane
        self.index = len(vehicles[direction][lane]) - 1

        # setting the image of the vehicle object randomly from 4 car images
        t= random.randint(1,4)
        path = "images/" + direction + "/" + vehicle_class + str(t) + ".png"
        self.image = pygame.image.load(path)

        # setting the stopping coordinate based on the vehicle in front, unless its the first vehicle
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
        
        # changing the starting position of newly generated vehicles behind, to avoid overlapping of cars
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
    
    # rendering the image on the screen 
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    # this function is called to move the car 
    def accelerate(self):
        global total_vehicles_crossed, total_waiting_time
        if(self.direction=='right'):
            # checks if signal line is crossed 
            if(self.crossed==0 and self.x+self.image.get_rect().width>stop_line[self.direction]):
                self.crossed = -1
                # if the vehicle crosses when the signal is green its free to move and vip is set to '1' 
                if(current_green_signal==0 and is_current_signal_yellow==0):
                    self.vip=1
            # crossed value is updated to '1' once crossed
            if self.crossed==-1 and current_green_signal==0 and is_current_signal_yellow==0:
                self.crossed=1
                total_vehicles_crossed+=1 # total vehicles counter incremented

            # if the vehicle has crossed the signal or it has space to move it moves 
            if self.vip==1 or ( (self.x+self.image.get_rect().width<=self.stop or self.crossed == 1 or (current_green_signal==0 and is_current_signal_yellow==0)) and (self.index==0 or self.x+self.image.get_rect().width <(vehicles[self.direction][self.lane][self.index-1].x - moving_gap))):
                
                # if car is going straight no turning is needed
                if self.going is 'straight':
                    self.x += self.speed # coordinate value incremented
                    
                # if the car is going right the vehicle in the simumation needs to rotate based on its position
                # the rotationAngle value is updated with this
                if self.going is 'right':
                    if self.x<stop_line[self.direction]:
                        self.x += self.speed
                    elif self.y>stop_line['up']:
                        self.y += self.speed
                        self.rotationAngle=-90
                    else:
                        # for calculating how much rotation to produce
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
            if self.crossed==-1 and current_green_signal==3 and is_current_signal_yellow==0:
                self.crossed=1
                total_vehicles_crossed+=1
            if self.vip==1 or ((self.y>=self.stop or self.crossed == 1 or (current_green_signal==3 and is_current_signal_yellow==0)) and (self.index==0 or self.y >(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + moving_gap))):                
                if self.going is 'straight':
                    self.y -= self.speed
                if self.going is 'right':
                    if self.y>stop_line[self.direction]:
                        self.y -= self.speed
                    elif self.x>stop_line['left']:
                        self.x += self.speed
                        self.rotationAngle=-90
                    else:
                        total=stop_line['up']-stop_line['down']
                        left=(self.y-stop_line['down'])-50
                        ratio=left/total
                        self.rotationAngle=-90*(1-ratio)
                        if self.rotationAngle<-90: self.rotationAngle=-90
                        self.y -= (self.speed*ratio)
                        self.x += (self.speed*(1-ratio))
        
        # for updating the total waiting time 
        if self.x== self.previous_x and self.y==self.previuos_y:
            total_waiting_time+= time.time()-self.previous_time
        self.previous_x=self.x
        self.previuos_y=self.y
        self.previous_time=time.time()

# function for displaying the rotated vehicle on the screen 
def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

# function to create the four signal objects and set their default values 
def initialize():
    ts1 = signal(0, default_yellow_duration, default_green_duration[0])
    signals.append(ts1)
    ts2 = signal(default_red_duration, default_yellow_duration, default_green_duration[1])
    signals.append(ts2)
    ts3 = signal(default_red_duration, default_yellow_duration, default_green_duration[2])
    signals.append(ts3)
    ts4 = signal(default_red_duration, default_yellow_duration, default_green_duration[3])
    signals.append(ts4)
    repeat()

# recurrsive fuction to update and change the signals adaptively 
def repeat():
    global current_green_signal, is_current_signal_yellow, next_green_signal, flag, cars_going_up, cycle, iteration
    
    # wait untill the green time alloted is complete
    while(signals[current_green_signal].green>0):
        updateValues()
        time.sleep(1)

    # we set the signal to yellow 
    is_current_signal_yellow = 1  

    # we set the stop values of the vehicles in the lane to the default stop values to aviod them crossing the signal 
    for i in range(0,2):
        for vehicle in vehicles[directionNumbers[current_green_signal]][i]:
            vehicle.stop=default_stop[directionNumbers[current_green_signal]]
        
    total_cars=[]
    # we loop over the vehicles to calculate the number of vehicles waiting in each direction  
    for i in range(0,4):
        total=0
        for j in range(0,2):
            for vehicle in vehicles[directionNumbers[i]][j]:
                if vehicle.crossed != 1 and vehicle.vip!=1:
                    total=total+1
        total_cars.append(total)
    # total_cars[3]=cars_going_up
    
    # select a signal which hasnt been alloted green in the round temprorally
    if flag[0] is 0:
        next_green_signal=0
    elif flag[1] is 0:
        next_green_signal=1
    elif flag[2] is 0:
        next_green_signal=2
    elif flag[3] is 0:
        next_green_signal=3
    
    # loop over the roads and find the signal with the most cars waiting which hasnt been alloted green already in the round 
    for i in range(0,4):
        print(directionNumbers[i],": ",total_cars[i])
        if flag[i]==0 and total_cars[i]>total_cars[next_green_signal]:
            next_green_signal=i
    # once we've selected a signal we update the value of flag to remember the signals that have been alloted in the round 
    flag[next_green_signal]=1
    # if next_green_signal==3:
    #     cars_going_up=0

    # we wait for the time alloted to yellow to get over 
    while(signals[current_green_signal].yellow>0):  
        updateValues()
        time.sleep(1)
    
    # update the value to 0
    is_current_signal_yellow = 0  
    
    # update the values of the green, yellow, red times of the signal to its default value 
    signals[current_green_signal].green = default_green_duration[current_green_signal]
    signals[current_green_signal].yellow = default_yellow_duration
    signals[current_green_signal].red = default_red_duration
    
    
    # update the signal value to to signal that be chose
    current_green_signal = next_green_signal 
    print("Signal updated to :", directionNumbers[current_green_signal])
    print("iteration: ", iteration % 4, ", Cycle: ", cycle)
    # allocate the green time based on the number of cars waiting with min of 2 secs and max of 20 secs 
    signals[current_green_signal].green= 2
    if total_cars[current_green_signal]/2 > 2 and total_cars[current_green_signal]/2 <= 20:
        signals[current_green_signal].green= int(total_cars[current_green_signal]/2)
        print("time allotted to signal: ",signals[current_green_signal].green)
    elif total_cars[current_green_signal]/2 > 20:
        signals[current_green_signal].green= 20
        print("time allotted to signal: ",signals[current_green_signal].green)
    next_green_signal = (current_green_signal+1)%n_signals
    StatThread = threading.Thread(target = client(total_cars[0]+total_cars[1]+total_cars[2]+total_cars[3]))
    StatThread.daemon = True
    StatThread.start()

    # check if all the signal have been allocated green once and if so reset the flag values to start a new round 
    all_one=True
    for i in flag:
        if i is 0:
            all_one=False
    if all_one is True:
        cycle=cycle+1
        for i in range(0,4):
            flag[i]=0
    iteration=iteration+1
    repeat()

# function is called every 1sec to update the green, yellow, red values of the signals 
def updateValues():
    for i in range(0, n_signals):
        if(i==current_green_signal):
            if(is_current_signal_yellow==0):
                signals[i].green-=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

# function that is called every 1sec to generate vehicles 
def generateVehicles():
    global cars_going_up, vehicle_type
    while(True):
        # randomly allocating the details the vehicle being generated
        lane_number = random.randint(0,1)
        going='straight'
        temp2= random.randint(0,1)
        if temp2 is 1 and lane_number is 1:
            going='right'
        temp = random.randint(0,99)
        direction_number = 0
        # dist= [25,50,75,100]
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
            going='straight'
            # cars_going_up=cars_going_up+1
        
        # creating the vehicle object 
        Vehicle(lane_number, vehicle_type[0], direction_number, directionNumbers[direction_number],going)
        
        time.sleep(1)


class Main:
    # thread to run the initilize function and then recursively the repeat funcion
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    
    thread1.daemon = True
    thread1.start() 
    
    # building the screen for the simulation 
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

    # thread to generate vehicles continously 
    thread2 =   threading.Thread(name="generateVehicles",target=generateVehicles, args=())
    thread2.daemon = True
    thread2.start()

    # while loop that countinously updates the simulation screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.blit(background,(0,0))  
        signal  
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

        h = font.render('ADAPTIVE TRAFFIC SIGNAL', True, white, black)
        screen.blit(h,(700,200))

        # displaying stats on the screen 

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
        
        # updates the vehicle coordinates in the simulation  
        for vehicle in simulation:  
            if vehicle.going=='right':
                blitRotateCenter(screen, vehicle.image, (vehicle.x,vehicle.y), vehicle.rotationAngle)
            else:
                screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.accelerate()
        pygame.display.update()


Main()