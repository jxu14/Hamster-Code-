
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
from HamsterAPI.comm_ble import RobotComm    # no dongle
#from HamsterAPI.comm_usb import RobotComm    # yes dongle

################################
# Hamster control
################################
class RobotBehaviorThread(threading.Thread):
    def __init__(self, robotList):
        super(RobotBehaviorThread, self).__init__()
        self.lineFollow = False
        self.done = False
        self.shy = False
        self.robotList = robotList
        return

    def run(self):
        robot=None
        while not self.done:
            for robot in self.robotList:
                if robot and self.lineFollow:
                    #############################################
                    # START OF YOUR WORKING AREA!!!
                    #############################################

                    # 
                    
                    if(robot.get_floor(0) > 50 and robot.get_floor(1)<50):
                        robot.set_wheel(0,30)
                        robot.set_wheel(1,-30)

                    elif(robot.get_floor(0)<50 and robot.get_floor(1)>50):
                        robot.set_wheel(0,-30)
                        robot.set_wheel(1,30)

                    else:
                        robot.set_wheel(0,30)
                        robot.set_wheel(1,30)

            for robot in self.robotList:

                if robot and self.shy:
                    if robot.get_proximity(1) >= 30 or robot.get_proximity(0) >= 30:
                        robot.set_wheel(0, -60)
                        robot.set_wheel(1, -60)

                    else:
                        robot.set_wheel(0, 30)
                        robot.set_wheel(1, 30)

            for robot in self.robotList:
                if robot and self.lineFollow:
                    if robot.get_proximity(1) >= 30 or robot.get_proximity(0) >= 30:
                        robot.set_wheel(0, 40 - robot.get_proximity(0))
                        robot.set_wheel(1, 40 - robot.get_proximity(1))

                    else:
                        robot.set_wheel(0, 0)
                        robot.set_wheel(1, 0)
                    
                    #############################################
                    # END OF YOUR WORKING AREA!!!
                    #############################################                    
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


        #This code creates a button. Use it to make more
        b1 = tk.Button(root, text='LineFollow')
        b1.pack(side='left')
        b1.bind('<Button-1>', self.startFollow)

        b2 = tk.Button(root, text='Exit')
        b2.pack(side='left')
        b2.bind('<Button-1>', self.stopProg)

        b3 = tk.Button(root, text='Shy')
        b3.pack(side='left')
        b3.bind('<Button-1>', self.shyProg)

        return
    
    def startFollow(self, event=None):
        self.robot_control.lineFollow = True
        return

    def stopProg(self, event=None):
        self.robot_control.done = True      
        self.root.quit()    # close window
        return

    def shyProg(self, event=None):
        self.robot_control.shy = True
        return



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
