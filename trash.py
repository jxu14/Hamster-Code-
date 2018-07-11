import sys
import time
import threading
import Tkinter as tk
import Queue
import random
from HamsterAPI.comm_ble import RobotComm

class Event(object):
	def __init__(self, event_type, event_data):
		self.type = event_type #string
		self.data = event_data #list of number or character depending on type

# Finite state machine engine
##############################
class StateMachine(object):
	def __init__(self, name, eventQ_handle):
		self.name = name		# machine name
		self.states = []	# list of lists, [[state name, event, transition, next_state],...]
		self.start_state = None
		self.end_states = []	# list of name strings
		self.q = eventQ_handle
		return

	def set_start_state(self, state_name):
		self.start_state = state_name
		return

	def get_start_state(self):
		return self.start_state
		
	def add_end_state(self, state_name):
		self.end_states.append(state_name)
		return
			
	def add_state(self, state, event, callback, next_state):
		self.states.append([state, event, callback, next_state]) # append to list
		return
	
	# you must set start state before calling run()
	def run(self):
		#print 'entering run'
		current_state = self.start_state
		#while not self.q.empty(): # for a machine that has end states
		while True:
			#print 'in while'
			if current_state in self.end_states:
				break
			#print('queue', self.q)
			if not self.q.empty():
				e = self.q.get()
				for c in self.states:
					if(e.type == 'obstacle_right'):
						# print 'obstacle right'
						continue
					if (c[0] == current_state and c[1] == e.type):
						#print 'current_state', current_state, ' ', 'NEW STATE', e.type
						c[2]()	# invoke callback function
						current_state = c[3] 	# next state
						break	# get out of inner for-loop
		return

################################
# Hamster control
################################
class RobotBehavior(object):
	def __init__(self, robot_list):
		self.counter = 0 
		self.done = False	# set by GUI button
		self.go = False		# set by GUI button
		self.robot_list = robot_list
		self.robot = None
		self.q = Queue.Queue()	# event queue for FSM
		self.first = True
		self.spawn_threads()
		return

	def spawn_threads(self):
		event_watcher=threading.Thread(name='event_watcher_thread', target=self.event_watcher, args=(self.q,))
		event_watcher.daemon = True
		event_watcher.start()
		
		fsm  =  StateMachine("FSM",self.q)
		fsm.set_start_state("forward")
		
		fsm.add_state("forward","free",self.moving_forward,"forward")
		fsm.add_state("forward","obstacle_right",self.turning_right,"right")
		fsm.add_state("forward","obstacle_left",self.turning_left,"left")
		fsm.add_state("forward","done",self.kill,"Finish")

		fsm.add_state("left","free",self.moving_forward,"forward")
		fsm.add_state("left","obstacle_right",self.turning_right,"right")
		fsm.add_state("left","obstacle_left",self.turning_left,"left")
		fsm.add_state("left","done",self.kill,"Finish")


		fsm.add_state("right","free",self.moving_forward,"forward")
		fsm.add_state("right","obstacle_right",self.turning_right,"right")
		fsm.add_state("right","obstacle_left",self.turning_left,"left")
		fsm.add_state("right","done",self.kill,"Finish")


		fsm.add_state("border", "free", self.moving_forward, "forward")
		fsm.add_state("forward", "border_event", self.back_up, "border")
		fsm.add_state("left", "border_event", self.back_up, "border")
		fsm.add_state("right","border_event",self.back_up,"border" )
		fsm.add_state("border","done",self.kill,"Finish")


		fsm.add_end_state('Finish')

		t_fsm = threading.Thread(name = 'StateMachine', target=fsm.run)
		t_fsm.daemon=True
		t_fsm.start()


		###########################################################
		# Two threads are created here.
		# 1. create a watcher thread that reads sensors and registers events: obstacle on left, right or no obstacle. This
		# 	thread runs the method event_watcher() you are going to implement below.
		# 2. Instantiate StateMachine and populate it with avoidance states, triggers, etc. Set start state.
		# 3. Create a thread to run FSM engine.
		###########################################################	
		

	def event_watcher(self, q):

		while not self.done:
			if self.robot_list and self.go:
				self.robot = self.robot_list[0]
				proxl = self.robot.get_proximity(0)
				proxr = self.robot.get_proximity(1)
				border = self.robot.get_floor(0)
				

				#print ("This is right"), proxr
				#print("This is left"), proxl
				#print(proxl, proxr)
				#print ('This is first:'), self.first
				if self.first == True:
					self.robot.set_wheel(0,30)
					self.robot.set_wheel(1,30)
					self.first = False

					
				if self.counter  == 3:
					obs_event = Event("done",[])
					q.put(obs_event)

				else:

					if border < 60:
						obs_event = Event("border_event", [border,proxl,proxr])
						q.put(obs_event)

					else:
					#	print ("This is right"), proxr
					#	print("This is left"), proxl

						if proxl > 30 or proxr > 30: #and abs(proxl-proxr) < 3:
							
							if(abs(proxl - proxr) < 10):
								obs_event = Event("free", [])
								q.put(obs_event)
								
							elif proxl > proxr:
								#print "PROXL > PROXR"
								obs_event = Event("obstacle_left", [proxl])
								q.put(obs_event)

							elif proxr > proxl:
								#print "PROXR > PROXL"
								obs_event = Event("obstacle_right", [proxr])
								q.put(obs_event)
							
							else:
								obs = Event("free", [])
								q.put(obs_event)

						

						else:
							obs_event = Event("free", [])
							q.put(obs_event)

			else:
				#print 'waiting ...'
				pass
			time.sleep(0.01)	# delay to give alert thread more processing time. Otherwise, it doesn't seem to have a chance to serve 'free' event
	

				
				###########################################################
				# Implement event producer here. The events are obstacle on left, right or no obstacle. Design your
				# logic for what event gets created based on sensor readings.
				###########################################################
				

	#######################################
	# Implement Hamster movements to avoid obstacle
	#######################################
	def turning_left(self):
		#print 'turning_left'
		self.robot.set_wheel(0,0)	
		self.robot.set_wheel(1,30)
		

	def turning_right(self):
		if self.robot:
			#print 'turning_right'
			self.robot.set_wheel(0,30)
			self.robot.set_wheel(1,0)
		

	def moving_forward(self):
		#print 'forward'
		self.robot.set_wheel(0,100)
		self.robot.set_wheel(1,100)

	def back_up(self):
		turn = random.randint(350,750)/1000.0
		#print 'backing up'
		self.robot.set_wheel(0,0)
		self.robot.set_wheel(1,0)
		self.robot.set_wheel(0,-30)
		self.robot.set_wheel(1,-30)
		time.sleep(0.50)

		print ('this is counter', self.counter)


		if self.robot.get_proximity(0) > 0 or self.robot.get_proximity(1) > 0:
			print 'complete'
			self.counter +=1 
			print ('this is counter', self.counter)


		self.robot.set_wheel(0,100)
		self.robot.set_wheel(1,-100)
		time.sleep(0.5)
		self.robot.set_wheel(0,30)
		self.robot.set_wheel(1,30)

		
	
	def kill(self):
		self.robot.set_wheel(0,0)
		self.robot.set_wheel(1,0)
		self.robot.set_led(0,6)
		self.robot.set_led(1,6)
		self.robot.set_buzzer(30)

		


		  
class GUI(object):
	def __init__(self, root, robot_control):
		self.root = root
		self.robot_control = robot_control
		
		canvas = tk.Canvas(root, bg="white", width=300, height=250)
		canvas.pack(expand=1, fill='both')
		canvas.create_rectangle(175, 175, 125, 125, fill="green")

		b1 = tk.Button(root, text='Go')
		b1.pack()
		b1.bind('<Button-1>', self.startProg)

		b2 = tk.Button(root, text='Exit')
		b2.pack()
		b2.bind('<Button-1>', self.stopProg)
		return
	
	def startProg(self, event=None):
		self.robot_control.go = True
		return

	def stopProg(self, event=None):
		self.robot_control.done = True		
		self.root.quit() 	# close window
		return

def main():
	gMaxRobotNum = 1 # max number of robots to control
	comm = RobotComm(gMaxRobotNum)
	comm.start()
	print 'Bluetooth starts'

	robot_list = comm.robotList
	behaviors = RobotBehavior(robot_list)

	frame = tk.Tk()
	GUI(frame, behaviors)
	frame.mainloop()

	comm.stop()
	comm.join()
	return

if __name__ == "__main__":
	sys.exit(main())