import sys
import time
import threading
import Tkinter as tk
import Queue
from HamsterAPI.comm_ble import RobotComm
import logging	

logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s',)

class Event(object):
    def __init__(self, event_type, event_data):
        self.type = event_type #string
        self.data = event_data #list of number or character depending on type

##############################
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
		current_state = self.start_state
		#while not self.q.empty(): # for a machine that has end states
		while True:
			if current_state in self.end_states:
				break
			if not self.q.empty():
				e = self.q.get()
				for c in self.states:
					if c[0] == current_state and c[1] == e.type:
						c[2]()	# invoke callback function
						current_state = c[3] 	# next state
						break	# get out of inner for-loop
		return

################################
# Hamster control
################################
class RobotBehavior(object):
	def __init__(self, robot_list):
		self.done = False	# set by GUI button
		self.go = False		# set by GUI button
		self.robot_list = robot_list
		self.robot = None
		self.q = Queue.Queue()	# event queue for FSM
		self.spawn_threads()

		self.borderTimes = 0
		self.isPushingBox = False

		return

	def spawn_threads(self):
		###########################################################
		# Two threads are created here.
		# 1. create a watcher thread that reads sensors and registers events: obstacle on left, right or no obstacle. This
		# 	thread runs the method event_watcher() you are going to implement below. DONE
		# 2. Instantiate StateMachine and populate it with avoidance states, triggers, etc. Set start state.
		# 3. Create a thread to run FSM engine.
		###########################################################	

		logging.debug("Threads have been called")


		t = threading.Thread(name='event watch thread', target=self.event_watcher, args = (self.q,))
		t.daemon = True
		t.start()

		stateMachine = StateMachine("StateMachineObject", self.q)
		stateMachine.set_start_state("forward")

		stateMachine.add_state("forward", "free", self.moving_forward, "forward")
		stateMachine.add_state("forward", "obstacle_left", self.turning_left, "left")
		stateMachine.add_state("forward", "obstacle_right", self.turning_right, "right")
		stateMachine.add_state("forward", "border", self.border_turn, "forward")
		stateMachine.add_state("forward", "obstacle_straight", self.moving_forward, "forward")

		stateMachine.add_state("left", "obstacle_left", self.turning_left, "left")
		stateMachine.add_state("left", "obstacle_right", self.turning_right, "right")
		stateMachine.add_state("left", "free", self.moving_forward, "forward")
		stateMachine.add_state("left", "border", self.border_turn, "forward")
		stateMachine.add_state("left", "obstacle_straight", self.moving_forward, "forward")

		stateMachine.add_state("right", "free", self.moving_forward, "forward")
		stateMachine.add_state("right", "obstacle_right", self.turning_right, "right")
		stateMachine.add_state("right", "obstacle_left", self.turning_left, "left")
		stateMachine.add_state("right", "border", self.border_turn, "forward")
		stateMachine.add_state("right", "obstacle_straight", self.moving_forward, "forward")





		stateMachine.add_end_state("finished")

		t_FSM = threading.Thread(name = "FSM_Thread", target = stateMachine.run)
		t_FSM.daemon =True
		t_FSM.start()



	def event_watcher(self, q):

		while not self.done:
			if self.robot_list and self.go:
				logging.debug("events are being watched")
				self.robot = self.robot_list[0]
				
				###########################################################
				# Implement event producer here. The events are obstacle on left, right or no obstacle. Design your
				# logic for what event gets created based on sensor readings.
				###########################################################

				prox_l = self.robot.get_proximity(0)
				prox_r = self.robot.get_proximity(1)

				floor_l = self.robot.get_floor(0)
				floor_r = self.robot.get_floor(1)


				if prox_l > 50 or prox_r >50:

					if abs(prox_r-prox_l) <= 5:
						self.isPushingBox = True
						obs_event = Event("obstacle_straight", [prox_l, prox_r])
						self.q.put(obs_event)

					elif prox_l>prox_r:
						obs_event = Event("obstacle_left", [prox_l, prox_r])
						self.q.put(obs_event)
					else:
						obs_event = Event("obstacle_right", [prox_l, prox_r])
						self.q.put(obs_event)
				else:
					obs_event = Event("free", [prox_l, prox_r])
					self.q.put(obs_event)

				if floor_l < 60 or floor_r < 60:
					obs_event = Event("border", [floor_l, floor_r])
					self.q.put(obs_event)

			time.sleep(0.1)
		return

	#######################################
	# Implement Hamster movements to avoid obstacle
	#######################################
	def turning_left(self):
		self.robot.set_wheel(0, -30)
		self.robot.set_wheel(1,30)


	def turning_right(self):
		self.robot.set_wheel(0,30)
		self.robot.set_wheel(1,-30)


	def moving_forward(self):
		self.robot.set_wheel(0,70)
		self.robot.set_wheel(1,70)
	

	def border_turn(self):

		logging.debug(self.borderTimes)
		logging.debug(self.isPushingBox)

		if(self.isPushingBox):
			self.borderTimes += 1
			self.isPushingBox = False

		if(self.borderTimes >= 3):
			self.robot.set_wheel(0,0)
			self.robot.set_wheel(1,0)
			self.robot.set_musical_note(50)

		else:
			self.robot.set_wheel(0,-70)
			self.robot.set_wheel(1,70)

		time.sleep(0.1)

		  
class GUI(object):
	def __init__(self, root, robot_control):
		self.root = root
		self.robot_control = robot_control
		
		canvas = tk.Canvas(root, bg="white", width=300, height=250)
		canvas.pack(expand=1, fill='both')
		canvas.create_rectangle(175, 175, 125, 125, fill="red")

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


