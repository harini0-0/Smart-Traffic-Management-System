import threading
import time

#North-South Road is Road 1 (NS)
#South-North Road is Road 2 (SN)
#East-West Road is Road 3 (EW)
#West-East Road is Road 4 (WE)

NS = 2
SN = 2
EW = 0
WE = 0

red=0
yellow=1
green=2
signal_time = [5,2,5]
signal_color = ["RED","YELLOW", "GREEN"]
signal_message = ["STOP","WAIT","GO"]

def output(signal):
    if signal==red:
    	NS = 2
    	SN = 2
    	EW = 0
    	WE = 0
    elif signal==yellow:
    	NS = 1
    	SN = 1
    	EW = 1
    	WE = 1
    elif signal==green:
    	NS = 0
    	SN = 0
    	EW = 2
    	WE = 2
    print("For Road 1 (NS) :")
    print("Signal Color :",signal_color[NS])
    print(signal_message[NS],"\n")
    print("For Road 2 (SN) :")
    print("Signal Color :",signal_color[SN])
    print(signal_message[SN],"\n")
    print("For Road 3 (EW) :")
    print("Signal Color :",signal_color[EW])
    print(signal_message[EW],"\n")
    print("For Road 4 (WE) :")
    print("Signal Color :",signal_color[WE])
    print(signal_message[WE],"\n\n")

def assign_signal(signal):
	if signal==red:
		NS = 2
		SN = 2
		EW = 0
		WE = 0
	elif signal==yellow:
		NS = 1
		SN = 1
		EW = 1
		WE = 1
	elif signal==green:
		NS = 0
		SN = 0
		EW = 2
		WE = 2



def run(signal):
    for i in range(100):
        output(signal)
        time.sleep(signal_time[signal])
        signal = (signal+1)%3
        char = input()
        if char=='s':
            break
        
    

y = threading.Thread(target=run, args=(0, ))
y.start()