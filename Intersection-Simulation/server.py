 # import socket programming library
import socket
# import thread module
from _thread import *
import threading
  
print_lock = threading.Lock()
  
# thread function
def threaded(c):
    while True:
  
        # data received from client
        data = c.recv(1024)
        if not data:
            print_lock.release()
            break
        print("Current Traffic Status at the junction is : ")
        stat = int(data)
        if stat <= 10:
            print("Free")
        elif stat<=15:
            print("Moderate Traffic")
        elif stat<=20:
            print("High Traffic")
        elif stat>20:
            print("Congestion")
        c.send(data)
    c.close()
  
  
def Main():
    host = ""
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)
  
    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")
  
    # a forever loop until client wants to exit
    while True:
  
        # establish connection with client
        c, addr = s.accept()
  
        # lock acquired by client
        print_lock.acquire()
        #print('Connected to :', addr[0], ':', addr[1])
  
        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    s.close()
  
  
if __name__ == '__main__':
    StatThread = threading.Thread(target = Main())
    StatThread.daemon = True
    StatThread.start()