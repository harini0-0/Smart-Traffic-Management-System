from flask import Flask, render_template
import random
import threading
import time

intersections = [0]*3

def updateStats():
	while(True):
		for i in range(3):
			intersections[i] = random.randint(0,3)
		time.sleep(5)

StatThread = threading.Thread(target = updateStats)
StatThread.start()



app = Flask(__name__)

@app.route('/')
def Index():
	return render_template('CityMap.html',context = intersections)
	print(intersections[1])


if __name__=="__main__":
    
    app.run(debug=True)