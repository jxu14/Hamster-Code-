'''
/* =======================================================================
   (c) 2015, Kre8 Technology, Inc.
   This is a program that is provided to students in Robot AI class.
   Students use this it to build different Hamster behaviors.

   Name:          tk_behaviors_starter.py
   By:            Qin Chen
   Last Updated:  5/10/18

   PROPRIETARY and CONFIDENTIAL
   ========================================================================*/
'''
import sys
import time
import threading
import Tkinter as tk
from HamsterAPI.comm_ble import RobotComm	# no dongle
#from HamsterAPI.comm_usb import RobotComm	# yes dongle

################################
# Hamster control
################################
class RobotBehaviorThread(threading.Thread):
	def __init__(self, robotList):
		super(RobotBehaviorThread, self).__init__()
		self.go = False
		self.done = False
		self.shy = False
		self.follow = False
		# self.line = False
		self.robotList = robotList
		return

	def run(self):
		robot=None
		while not self.done:
			for robot in self.robotList:
				if robot and self.go:
					robot.set_wheel(0, 30)
					robot.set_wheel(1, 30)

			for robot in self.robotList:

				if robot and self.shy:
					if robot.get_proximity(1) >= 30 or robot.get_proximity(0) >= 30:
						robot.set_wheel(0, -60)
						robot.set_wheel(1, -60)

					else:
						robot.set_wheel(0, 30)
						robot.set_wheel(1, 30)

			for robot in self.robotList:
				if robot and self.follow:
					if robot.get_proximity(1) >= 30 or robot.get_proximity(0) >= 30:
						robot.set_wheel(0, 40 - robot.get_proximity(0))
						robot.set_wheel(1, 40 - robot.get_proximity(1))

					else:
						robot.set_wheel(0, 0)
						robot.set_wheel(1, 0)

			# for robot in self.robotList:
			# 	if robot and self.line:
			# 		if robot.get_floor(0) < 10 or robot.get_floor(1) < 10:
			# 			robot.set_wheel(0, 40 - robot.get_floor(0))
			# 			robot.set_wheel(1, 40 - robot.get_floor(1))
			# 		else:
			# 			robot.set_wheel(0, 30)
			# 			robot.set_wheel(1, 30)

		# stop robot activities, such as motion, LEDs and sound
		# clean up after exit button pressed
		if robot:
			robot.reset()
			time.sleep(0.1)
		return

class GUI(object):
	def __init__(self, root, robot_control):
		self.root = root
		self.robot_control = robot_control
		root.geometry('250x30')
		root.title('Hamster Control')

		b1 = tk.Button(root, text='Go')
		b1.pack(side='left')
		b1.bind('<Button-1>', self.startProg)

		b2 = tk.Button(root, text='Exit')
		b2.pack(side='left')
		b2.bind('<Button-1>', self.stopProg)

		b3 = tk.Button(root, text='Shy')
		b3.pack(side='left')
		b3.bind('<Button-1>', self.shyProg)

		b3 = tk.Button(root, text='Follow')
		b3.pack(side='left')
		b3.bind('<Button-1>', self.follow)

		# b4 = tk.Button(root, text='Follow Line')
		# b4.pack(side='left')
		# b4.bind('<Button-1>', self.line)
		return
	
	def startProg(self, event=None):
		self.robot_control.go = True
		return

	def stopProg(self, event=None):
		self.robot_control.done = True		
		self.root.quit() 	# close window
		return

	def shyProg(self, event=None):
		self.robot_control.shy = True
		return

	def follow(self, event=None):
		self.robot_control.follow = True
		return

	# def line(self, event=None):
	# 	self.robot_control.line = True
	# 	return


#################################
# Don't change any code below!! #
#################################

def main():
    # instantiate COMM object
    gMaxRobotNum = 1; # max number of robots to control
    comm = RobotComm(gMaxRobotNum)
    comm.start()
    print 'Bluetooth starts'  
    robotList = comm.robotList

    behaviors = RobotBehaviorThread(robotList)
    behaviors.start()

    frame = tk.Tk()
    GUI(frame, behaviors)
    frame.mainloop()

    comm.stop()
    comm.join()
    print("terminated!")

if __name__ == "__main__":
    sys.exit(main())

