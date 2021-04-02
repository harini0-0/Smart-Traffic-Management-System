import threading
import time
import random

intersections = [0]*36
random.seed()
def updateStats():
	for i in range(36):
		intersections[i] = random.randint(0,4)
	time.sleep(5)

if __name__=="__main__":
	updateStats()
	print(intersections)
	