from flask import Flask, render_template
import multiprocessing
import threading
import os
import time
import random
from forms import  NeighbourhoodStat,GetRoute


vertices = 11
matrix_slots = vertices*vertices

# Shared Memory Locations
traffic_states = multiprocessing.Array('i',vertices)
route = multiprocessing.Array('i',vertices)
graph_matrix = multiprocessing.Array('i', matrix_slots)

traffic_state = ["Value not updated yet","","Free","","Moderate Traffic","","High Traffic","","Congestion"]
r_intersections = [0]*vertices
graph = [ [ 0 for i in range(vertices) ] for j in range(vertices) ]

random.seed()


def getStats():
	while(True):
		for i in range(vertices):
			r_intersections[i] = 2*random.randint(1,4)
		time.sleep(5)

def updateStats(traffic_states,r_intersections):
	print("\n\nProcess-1 Started")
	ct = time.time()
	print('process id:', os.getpid())
	print("Work that is being done : Update Traffic Congestion values of all junctions into shared memory")
	for i in range(vertices):
		traffic_states[i] = r_intersections[i]
	print("Process-1 Completed\n")
	et = time.time()
	print("Burst Time = ",(et-ct)*1000," milliseconds","\n\n")



def buildGraph(graph_matrix,traffic_states):
	intersections = list(traffic_states)
	print("\n\nProcess-2 Started")
	ct = time.time()
	print('process id:', os.getpid())
	print("Work that is being done : Building a Graph for City Map that was displayed")
	#print(intersections)
	for i in range( matrix_slots):
		graph_matrix[i] = 0

	graph_matrix[0*vertices+1] = int((intersections[0]+intersections[1])/2)
	graph_matrix[1*vertices+0] = int((intersections[0]+intersections[1])/2)
	graph_matrix[0*vertices+5] = int((intersections[0]+intersections[5])/2)
	graph_matrix[5*vertices+0] = int((intersections[0]+intersections[5])/2)
	graph_matrix[0*vertices+8] = int((intersections[0]+intersections[8])/2)
	graph_matrix[8*vertices+0] = int((intersections[0]+intersections[8])/2)
	graph_matrix[2*vertices+1] = int((intersections[2]+intersections[1])/2)
	graph_matrix[1*vertices+2] = int((intersections[2]+intersections[1])/2)
	graph_matrix[5*vertices+1] = int((intersections[5]+intersections[1])/2)
	graph_matrix[1*vertices+5] = int((intersections[5]+intersections[1])/2)
	graph_matrix[5*vertices+6] = int((intersections[5]+intersections[6])/2)
	graph_matrix[6*vertices+5] = int((intersections[5]+intersections[6])/2)
	graph_matrix[5*vertices+8] = int((intersections[5]+intersections[8])/2)
	graph_matrix[8*vertices+5] = int((intersections[5]+intersections[8])/2)
	graph_matrix[5*vertices+9] = int((intersections[5]+intersections[9])/2)
	graph_matrix[9*vertices+5] = int((intersections[5]+intersections[9])/2)
	graph_matrix[9*vertices+8] = int((intersections[9]+intersections[8])/2)
	graph_matrix[8*vertices+9] = int((intersections[9]+intersections[8])/2)
	graph_matrix[9*vertices+10] = int((intersections[9]+intersections[10])/2)
	graph_matrix[10*vertices+9] = int((intersections[9]+intersections[10])/2)
	graph_matrix[6*vertices+10] = int((intersections[6]+intersections[10])/2)
	graph_matrix[10*vertices+6] = int((intersections[6]+intersections[10])/2)
	graph_matrix[7*vertices+10] = int((intersections[7]+intersections[10])/2)
	graph_matrix[10*vertices+7] = int((intersections[7]+intersections[10])/2)
	graph_matrix[4*vertices+10] = int((intersections[4]+intersections[10])/2)
	graph_matrix[10*vertices+4] = int((intersections[4]+intersections[10])/2)
	graph_matrix[2*vertices+3] = int((intersections[2]+intersections[3])/2)
	graph_matrix[3*vertices+2] = int((intersections[2]+intersections[3])/2)
	graph_matrix[4*vertices+3] = int((intersections[4]+intersections[3])/2)
	graph_matrix[3*vertices+4] = int((intersections[4]+intersections[3])/2)
	graph_matrix[4*vertices+7] = int((intersections[4]+intersections[7])/2)
	graph_matrix[7*vertices+4] = int((intersections[4]+intersections[7])/2)
	print("Process-2 Completed\n")
	et = time.time()
	print("Burst Time = ",(et-ct)*1000," milliseconds","\n\n")

def getNeighbourhood(intersections,graph,n_j,n_s,vertices,userLocation):
	print("\n\nProcess-3 Started")
	ct = time.time()
	print('process id:', os.getpid())
	print("Work that is being done : Getting Traffic Status of neighborhood locations")
	for i in range(vertices):
			if graph[userLocation][i] != 0:
				n_j[i]=i
				n_s[i] = intersections[i]
	print("Process-3 Completed\n")
	et = time.time()
	print("Burst Time = ",(et-ct)*1000," milliseconds","\n\n")

def dijkstra(route,graph, src, j):
	print("\n\nProcess-4 Started")
	ct = time.time()
	print('process id:', os.getpid())
	print("Work that is being done : Finding the least congested path between source and destination")
	row = len(graph)
	col = len(graph[0])
	for i in range(vertices):
		route[i] = 0

	dist = [float("Inf")] * row
	parent = [-1] * row
	dist[src] = 0
	queue = []

	for i in range(row):
		queue.append(i)

	while queue:
		minimum = float("Inf")
		min_index = -1

		for i in range(len(dist)):
			if dist[i] < minimum and i in queue:
				minimum = dist[i]
				min_index = i
		u = min_index

		queue.remove(u)

		for i in range(col):
			if graph[u][i] and i in queue:
				if dist[u] + graph[u][i] < dist[i]:
					dist[i] = dist[u] + graph[u][i]
					parent[i] = u

	while (j!=src):
		route[j] = 1
		j = parent[j]
	route[src] = 1

	print("Process-4 Completed\n")
	et = time.time()
	print("Burst Time = ",(et-ct)*1000," milliseconds","\n\n")




app = Flask(__name__)

app.config['SECRET_KEY'] = '44b2bdc8ddverticesb48220f1f629a14d1d2b'

StatThread = threading.Thread(target = getStats)
StatThread.daemon = True
StatThread.start()
process_count = 0
process_queue = []

@app.route('/')
def Index():
	global process_count
	process_1 = multiprocessing.Process(target= updateStats, args=(traffic_states,r_intersections))
	process_queue.append(process_1)
	process_queue[process_count].start()
	process_queue[process_count].join()
	process_count+=1
	#print(list(traffic_states))
	return render_template('CityMap.html',intersections = list(traffic_states))

@app.route('/user', methods=['GET','POST'])
def User():
	global process_count
	StatForm = NeighbourhoodStat()
	RouteForm = GetRoute()
	if StatForm.validate_on_submit():
		process_2 = multiprocessing.Process(target= buildGraph, args=(graph_matrix,traffic_states))
		process_queue.append(process_2)
		process_queue[process_count].start()
		process_queue[process_count].join()
		process_count+=1
		intersections = list(traffic_states)
		n_j = multiprocessing.Array('i',vertices)
		n_s = multiprocessing.Array('i',vertices)
		n_j_r =[]
		n_s_r =[]
		userLocation = int(StatForm.yourLocation.data)
		for i in range(vertices):
			for j in range(vertices):
				graph[i][j] = graph_matrix[i*vertices+j]

		process_3 = multiprocessing.Process(target= getNeighbourhood, args=(intersections,graph,n_j,n_s,vertices,userLocation))
		process_queue.append(process_3)
		process_queue[process_count].start()
		process_queue[process_count].join()
		process_count+=1
		for i in range(vertices):
			if graph[userLocation][i] != 0:
				n_j_r.append(i)
				n_s_r.append(traffic_state[intersections[i]])

		pairs = zip(n_s_r,n_j_r)

		return render_template('user_neighbour.html', title='User',StatForm = StatForm,RouteForm = RouteForm, context = pairs)

	if RouteForm.validate_on_submit():
		process_2 = multiprocessing.Process(target= buildGraph, args=(graph_matrix,traffic_states))
		process_queue.append(process_2)
		process_queue[process_count].start()
		process_queue[process_count].join()
		process_count+=1
		userLocation = int(RouteForm.userLocation.data)
		destination = int(RouteForm.destination.data)
		for i in range(vertices):
			for j in range(vertices):
				graph[i][j] = graph_matrix[i*vertices+j]

		process_4 = multiprocessing.Process(target =dijkstra,args=(route,graph,userLocation,destination))
		process_queue.append(process_4)
		process_queue[process_count].start()
		process_queue[process_count].join()
		process_count+=1
		
		
		return render_template('user_map.html', title='User',StatForm = StatForm,RouteForm = RouteForm, intersections = list(route))



	return render_template('user.html', title='User',StatForm = StatForm, RouteForm = RouteForm)


if __name__=="__main__":
    
    app.run(debug=True)