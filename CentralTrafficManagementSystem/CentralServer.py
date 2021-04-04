from flask import Flask, render_template
import random
import threading
import time
from forms import  NeighbourhoodStat

intersections = [0]*11
userLocation = 15
congestion_state = ["Free","Moderate Traffic","Congestion","High Congestion"]

random.seed()

def updateStats():
	while(True):
		for i in range(11):
			intersections[i] = random.randint(0,3)
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
		left = congestion_state[intersections[userLocation - 1]]
		right = congestion_state[intersections[userLocation + 1]]
		top = congestion_state[intersections[userLocation - 6]]
		bottom = congestion_state[intersections[userLocation + 6]]
		return render_template('user_neighbour.html', title='User',form = form, left = left,right = right, top = top, bottom = bottom)


	return render_template('user.html', title='User',form = form)


if __name__=="__main__":
    
    app.run(debug=True)