import sys
import Tkinter as tk
from HamsterAPI.comm_ble import RobotComm
from Tkinter import *
import time
#for PC, need to import from commm_usb

class Robots(object):
    def __init__(self, robotList):
        self.robotList = robotList
        return

    def move_forward(self, event=None):
        if self.robotList:
            for robot in self.robotList:
                robot.set_wheel(0,30)
                robot.set_wheel(1,30)
        else:
            print "waiting for robot"

    def move_backward(self, event=None):
        if self.robotList:
            for robot in self.robotList:
                robot.set_wheel(0,-30)
                robot.set_wheel(1,-30)
        else:
            print "Waiting for robot"

    def move_left(self, event=None):
        if self.robotList:
            for robot in self.robotList:
                robot.set_wheel(0,-30)
                robot.set_wheel(1,30)
        else:
            print "Waiting for robot"

    def move_right(self, event=None):
        if self.robotList:
            for robot in self.robotList:
                robot.set_wheel(0,30)
                robot.set_wheel(1,-30)
        else:
            print "Waiting for robot"

    def get_prox(self, sideNumber, event=None):
        if self.robotList:
            for robot in self.robotList:
                return robot.get_proximity(sideNumber)
        else:
            print "Waiting for robot"
            return None


    def get_floor(self, sideNumber, event=None):
        if self.robotList:
            for robot in self.robotList:
                return robot.get_floor(sideNumber)
        else:
            print "Waiting for robot"
            return None

    def stop_move(self, event=None):
        if self.robotList:
            for robot in self.robotList:
                robot.set_wheel(0,0)
                robot.set_wheel(1,0)
        else:
            print "Waiting for robot"

    def reset_robot(self, event=None): # use Hamster API reset()
        robot.reset()
        time.sleep(0.1)
    

class UI(object):
    def __init__(self, root, robot_handle):
        self.root = root
        self.robot_handle = robot_handle # handle to robot commands


        self.canvas = None
        self.prox_l_id = None
        self.prox_r_id = None
        self.floor_l_id = None
        self.floor_r_id = None


        

        self.initUI()
        return

    def initUI(self):
        ###################################################################
        # Create a Hamster joystick window which contains
        # 1. a canvas widget where "sensor readings" are displayed
        # 2. a square representing Hamster
        # 3. 4 canvas items to display floor sensors and prox sensors
        # 4. a button for exit, i.e., a call to stopProg(), given in this class DONE
        # 5. listen to key press and key release when focus is on this window
        ###################################################################

        self.root.title('Jeremy\'s Hamster Joystick')

        b2 = tk.Button(self.root, text='Exit', command = self.root.quit)
        b2.pack(side='bottom')

        self.canvas = Canvas(self.root, width=500, height=300)

        self.canvas.create_rectangle(175, 60, 325, 210, fill="blue")


        self.floor_l_id = self.canvas.create_rectangle(200,85,230,115, fill = "white")
        self.floor_r_id = self.canvas.create_rectangle(270, 85, 300, 115, fill = "white")

        self.prox_l_id = self.canvas.create_line(210, 0, 210, 85, width = 3, fill = "white")
        self.prox_r_id = self.canvas.create_line(290, 0, 290, 85, width = 3, fill = "white")

        self.display_sensor()

        self.canvas.bind("<KeyPress>", self.keydown)
        self.canvas.bind("<KeyRelease>", self.keyup)

        self.canvas.focus_set()

        self.canvas.pack()


        






    
    ######################################################
    # This function refreshes floor and prox sensor display every 100 milliseconds.
    # Register callback using Tkinter's after method().
    ######################################################
    def display_sensor(self):
        # These are the coordinates 
        # w.create_rectangle(185,70,200,85, fill = "white")
        # w.create_rectangle(305, 70, 315, 85, fill = "white")

        if(self.robot_handle.get_floor(0)<50):
            self.canvas.itemconfig(self.floor_l_id,fill = "black")
        else: 
            self.canvas.itemconfig(self.floor_l_id,fill = "white")
        if(self.robot_handle.get_floor(1)<50):
            self.canvas.itemconfig(self.floor_r_id, fill = "black")
        else:
            self.canvas.itemconfig(self.floor_r_id,fill = "white")
        if(self.robot_handle.get_prox(0) > 15):
            self.canvas.itemconfig(self.prox_l_id, fill = "black")
        else: 
            self.canvas.itemconfig(self.prox_l_id,fill = "white")
        if(self.robot_handle.get_prox(1)):
            self.canvas.itemconfig(self.prox_r_id, fill = "black")
        else:
            self.canvas.itemconfig(self.prox_r_id,fill = "white")

        self.root.after(100, self.display_sensor)


    ####################################################
    # Implement callback function when key press is detected
    ####################################################
    def keydown(self, event):

        if(event.char is "w"):
            self.robot_handle.move_forward()
        if(event.char is "a"):
            self.robot_handle.move_left()
        if(event.char is "s"):
            self.robot_handle.move_backward()
        if(event.char is "d"):
            self.robot_handle.move_right()



            


    #####################################################
    # Implement callback function when key release is detected
    #####################################################
    def keyup(self, event):
        self.robot_handle.stop_move()

    def stopProg(self, event=None):
        self.root.quit()    # close window
        self.robot_handle.reset_robot()
        return

def main(argv=None):
    gMaxRobotNum = 1 # max number of robots to control
    comm = RobotComm(gMaxRobotNum)
    comm.start()
    print 'Bluetooth starts'
    robotList = comm.robotList

    robot_handle = Robots(robotList)
    m = tk.Tk() #root
    gui = UI(m, robot_handle)

    m.mainloop()

    comm.stop()
    comm.join()

if __name__== "__main__":
    sys.exit(main())


