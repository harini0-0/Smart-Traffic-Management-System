from flask import Flask, render_template
import random
import threading
import time
from forms import  NeighbourhoodStat

intersections = [0]*36
userLocation = 15
random.seed()

def updateStats():
	while(True):
		for i in range(36):
			intersections[i] = random.randint(0,4)
		time.sleep(5)

StatThread = threading.Thread(target = updateStats)
StatThread.daemon = True
StatThread.start()

app = Flask(__name__)

app.config['SECRET_KEY'] = '44b2bdc8dd11b48220f1f629a14d1d2b'

@app.route('/')
def Index():
	return render_template('CityMap.html',intersections = intersections)

@app.route('/user', methods=['GET','POST'])
def User():
	form = NeighbourhoodStat()
	if form.validate_on_submit():
		userLocation = int(form.yourLocation.data)
		left = intersections[userLocation - 1]
		right = intersections[userLocation + 1]
		top = intersections[userLocation - 6]
		bottom = intersections[userLocation + 6]
		return render_template('user_neighbour.html', title='User',form = form, left = left,rigt = right, top = top, bottom = bottom)


	return render_template('user.html', title='User',form = form)


if __name__=="__main__":
    
    app.run(debug=True)