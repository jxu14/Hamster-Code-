import Tkinter as tk  
import sys
import time  
import math
import pdb
import threading
from HamsterAPI.comm_ble import RobotComm

class virtual_robot:
    def __init__(self):
        #self.robot = None
        self.l = 20*math.sqrt(2) # half diagonal - robot is 40 mm square
        self.x = 0 # x coordinate
        self.y = 0 # y coordinate
        self.a = 0 # angle of the robot, 0 when aligned with verticle axis
        self.dist_l = False
        self.dist_r = False #distance
        self.floor_l = False 
        self.floor_r = False 
        self.sl = 0 # speed of left wheel
        self.sr = 0 # speed of right wheel
        self.t = 0 # last update time

    def reset_robot(self):
        self.x = 0 # x coordinate
        self.y = 0 # y coordinate
        self.a = 0 # angle of the robot, 0 when aligned with verticle axis
        self.dist_l = False
        self.dist_r = False #
        self.floor_l = False 
        self.floor_r = False     
        self.sl = 0 # speed of left wheel
        self.sr = 0 # speed of right wheel
        self.t = 0 # last update time

    def set_robot_speed(self, w_l, w_r):
        self.sl = w_l
        self.sr = w_r

    def set_robot_pose(self, a, x, y):
        self.a = a
        self.x = x
        self.y = y

    def set_robot_prox_dist(self, dist_l, dist_r):
        self.dist_l = dist_l
        self.dist_r = dist_r

    def set_robot_floor (self, floor_l, floor_r):
        self.floor_l = floor_l
        self.floor_r = floor_r

class virtual_world:
    def __init__(self):
        self.real_robot = False
        self.go = False # activate robot behavior
        self.vrobot = virtual_robot()
        self.canvas = None
        self.canvas_width = 0
        self.canvas_height = 0
        self.area = []
        self.map = []
        #self.cobs = []
        self.f_cell_list = []
        self.goal_list = []
        self.goal_list_index = 0
        self.goal_t = "None"
        self.goal_x = 0
        self.goal_y = 0
        self.goal_a = 0
        self.goal_achieved = True
        self.trace = False #leave trace of robot
        self.prox_dots = False # draw obstacles detected as dots on map
        self.floor_dots = False
        self.localize = False
        self.glocalize = False
        self.draw=False
        #self.numref={}
        
    def add_obstacle(self,rect):
        self.map.append(rect)
        return


    def draw_map(self):
        canvas_width = self.canvas_width
        canvas_height = self.canvas_height
        c=0
        for rect in self.map:
            x1 = canvas_width + rect[0]
            y1= canvas_height - rect[1]
            x2= canvas_width + rect[2]
            y2 = canvas_height - rect[3]
            colors=['green','blue','grey','black','orange','red','purple']
            self.canvas.create_rectangle([x1,y1,x2,y2], outline=colors[c%7], fill="grey")
            c+=1

        # for cobs in self.cobs:
        #     x1 = canvas_width + cobs[0]
        #     y1= canvas_height - cobs[1]
        #     x2= canvas_width + cobs[2]
        #     y2 = canvas_height - cobs[3]
            #self.canvas.create_rectangle([x1,y1,x2,y2], fill=None)

    #method checks for the next direction
   

    def draw_robot(self):
        canvas_width = self.canvas_width
        canvas_height = self.canvas_height
        pi4 = 3.1415 / 4 # quarter pi
        vrobot = self.vrobot
        a1 = vrobot.a + pi4
        a2 = vrobot.a + 3*pi4
        a3 = vrobot.a + 5*pi4
        a4 = vrobot.a + 7*pi4

        x1 = canvas_width + vrobot.l * math.sin(a1) + vrobot.x
        x2 = canvas_width + vrobot.l * math.sin(a2) + vrobot.x
        x3 = canvas_width + vrobot.l * math.sin(a3) + vrobot.x        
        x4 = canvas_width + vrobot.l * math.sin(a4) + vrobot.x

        y1 = canvas_height - vrobot.l * math.cos(a1) - vrobot.y
        y2 = canvas_height - vrobot.l * math.cos(a2) - vrobot.y
        y3 = canvas_height - vrobot.l * math.cos(a3) - vrobot.y
        y4 = canvas_height - vrobot.l * math.cos(a4) - vrobot.y

        points = (x1,y1,x2,y2,x3,y3,x4,y4)
        poly_id = vrobot.poly_id
        self.canvas.coords(poly_id, points)    

        if (self.trace):
            pi3 = 3.1415/3
            a1 = vrobot.a
            a2 = a1 + 2*pi3
            a3 = a1 + 4*pi3
            x1 = canvas_width + 3 * math.sin(a1) + vrobot.x
            x2 = canvas_width + 3 * math.sin(a2) + vrobot.x
            x3 = canvas_width + 3 * math.sin(a3) + vrobot.x 
            y1 = canvas_height - 3 * math.cos(a1) - vrobot.y
            y2 = canvas_height - 3 * math.cos(a2) - vrobot.y
            y3 = canvas_height - 3 * math.cos(a3) - vrobot.y
            self.canvas.create_polygon([x1,y1,x2,y2,x3,y3], outline="blue")

    def radial_intersect (self, a_r, x_e, y_e):
        shortest = False
        p_intersect = False
        p_new = False

        for obs in self.map:
            x1 = obs[0]
            y1 = obs[1]
            x2 = obs[2]
            y2 = obs[3]
            # first quadron
            if (a_r >= 0) and (a_r < 3.1415/2): 
                #print "radial intersect: ", x_e, y_e
                if (y_e < y1):
                    x_i = x_e + math.tan(a_r) * (y1 - y_e)
                    y_i = y1
                    if (x_i > x1 and x_i < x2):
                        p_new = [x_i, y_i, 1] # 1 indicating intersecting a bottom edge of obs
                if (x_e < x1):
                    x_i = x1
                    y_i = y_e + math.tan(3.1415/2 - a_r) * (x1 - x_e)
                    if (y_i > y1 and y_i < y2):
                        p_new = [x_i, y_i, 2] # left edge of obs
            # second quadron
            if (a_r >= 3.1415/2) and (a_r < 3.1415): 
                if (y_e > y2):
                    x_i = x_e + math.tan(a_r) * (y2 - y_e)
                    y_i = y2
                    if (x_i > x1 and x_i < x2):
                        p_new = [x_i, y_i, 3] # top edge
                if (x_e < x1):
                    x_i = x1
                    y_i = y_e + math.tan(3.1415/2 - a_r) * (x1 - x_e)
                    if (y_i > y1 and y_i < y2):
                        p_new = [x_i, y_i, 2] #left edge
            # third quadron
            if (a_r >= 3.1415) and (a_r < 1.5*3.1415): 
                if (y_e > y2):
                    x_i = x_e + math.tan(a_r) * (y2 - y_e)
                    y_i = y2
                    if (x_i > x1 and x_i < x2):
                        p_new = [x_i, y_i, 3] #top edge
                if (x_e > x2):
                    x_i = x2
                    y_i = y_e + math.tan(3.1415/2 - a_r) * (x2 - x_e)
                    if (y_i > y1 and y_i < y2):
                        p_new = [x_i, y_i, 4] # right edge
            # fourth quadron
            if (a_r >= 1.5*3.1415) and (a_r < 6.283): 
                if (y_e < y1):
                    x_i = x_e + math.tan(a_r) * (y1 - y_e)
                    y_i = y1
                    if (x_i > x1 and x_i < x2):
                        p_new = [x_i, y_i, 1] # bottom edge
                if (x_e > x2):
                    x_i = x2
                    y_i = y_e + math.tan(3.1415/2 - a_r) * (x2 - x_e)
                    if (y_i > y1 and y_i < y2):
                        p_new = [x_i, y_i, 4] # right edge
            if p_new:
                dist = abs(p_new[0]-x_e) + abs(p_new[1]-y_e) 
                if shortest:
                    if dist < shortest:
                        shortest = dist
                        p_intersect = p_new
                else:
                    shortest = dist
                    p_intersect = p_new
            p_new = False

        if p_intersect: 
            return p_intersect
        else:
            return False

    def get_vrobot_prox(self, side):
        vrobot = self.vrobot

        a_r = vrobot.a # robot is orientation, same as sensor orientation
        if (a_r < 0):
            a_r += 6.283
        if (side == "left"):
            a_e = vrobot.a - 3.1415/4.5 #emitter location
        else:
            a_e = vrobot.a + 3.1415/4.5 #emitter location
        x_e = (vrobot.l-2) * math.sin(a_e) + vrobot.x #emiter pos of left sensor
        y_e = (vrobot.l-2) * math.cos(a_e) + vrobot.y #emiter pos of right sensor

        intersection = self.radial_intersect(a_r, x_e, y_e)

        if intersection:
            x_i = intersection[0]
            y_i = intersection[1]
            if (side == "left"):
                vrobot.dist_l = math.sqrt((y_i-y_e)*(y_i-y_e) + (x_i-x_e)*(x_i-x_e))
                if vrobot.dist_l > 120:
                    vrobot.dist_l = False
                return vrobot.dist_l
            else:
                vrobot.dist_r = math.sqrt((y_i-y_e)*(y_i-y_e) + (x_i-x_e)*(x_i-x_e))
                if vrobot.dist_r > 120:
                    vrobot.dist_r = False
                return vrobot.dist_r
        else:
            if (side == "left"):
                vrobot.dist_l = False
                return False
            else:
                vrobot.dist_r = False
                return False

    def draw_prox(self, side):
        canvas_width = self.canvas_width
        canvas_height = self.canvas_height
        vrobot = self.vrobot
        if (side == "left"):
            a_e = vrobot.a - 3.1415/5 #emitter location
            prox_dis = vrobot.dist_l
            prox_l_id = vrobot.prox_l_id
        else:
            a_e = vrobot.a + 3.1415/5 #emitter location
            prox_dis = vrobot.dist_r
            prox_l_id = vrobot.prox_r_id
        if (prox_dis):
            x_e = (vrobot.l-4) * math.sin(a_e) + vrobot.x #emiter pos of left sensor
            y_e = (vrobot.l-4) * math.cos(a_e) + vrobot.y #emiter pos of right sensor
            x_p = prox_dis * math.sin(vrobot.a) + x_e
            y_p = prox_dis * math.cos(vrobot.a) + y_e
            if (self.prox_dots):
                self.canvas.create_oval(canvas_width+x_p-1, canvas_height-y_p-1, canvas_width+x_p+1, canvas_height-y_p+1, outline='red')
            point_list = (canvas_width+x_e, canvas_height-y_e, canvas_width+x_p, canvas_height-y_p)
            self.canvas.coords(prox_l_id, point_list)
        else:
            point_list = (0,0,0,0)
            self.canvas.coords(prox_l_id, point_list)

    def draw_floor(self, side):
        canvas_width = self.canvas_width
        canvas_height = self.canvas_height
        vrobot = self.vrobot
        if (side == "left"):
            border = vrobot.floor_l
            floor_id = vrobot.floor_l_id
            a = vrobot.a - 3.1415/7 #rough position of the left floor sensor
        else:
            border = vrobot.floor_r
            floor_id = vrobot.floor_r_id
            a = vrobot.a + 3.1415/7 #rough position of the left floor sensor         
        x_f = (vrobot.l - 12) * math.sin(a) + vrobot.x
        y_f = (vrobot.l - 12) * math.cos(a) + vrobot.y
        points = (canvas_width+x_f-2, canvas_height-y_f-2, canvas_width+x_f+2, canvas_height-y_f+2)
        self.canvas.coords(floor_id, points)
        if (border): 
            self.canvas.itemconfig(floor_id, outline = "black", fill="black")
            if (self.floor_dots):
                self.canvas.create_oval(canvas_width+x_f-2, canvas_height-y_f-2, canvas_width+x_f+2, canvas_height-y_f+2, fill='black')
        else:
            self.canvas.itemconfig(floor_id, outline = "white", fill="white")

    ######################################################################
    # This function returns True when simulated robot would collide with 
    # one of the obstacles at given pose(a,x,y)
    ######################################################################
    def in_collision(self, a, x, y): #angle, x-center,y-center
        pi4= 3.1415 / 4
        for rect in self.map:
            d=3.1415/4
            s=0 #self.vrobot.l-20/(math.cos(d))

            #print self.vrobot.l-20/(math.cos(d))
            #print 'rect:x1' +str(rect[0])+",y1"+str(rect[1])+",x2"+str(rect[2])+",y2"+str(rect[3])
            #print 'rect:' +str(self.canvas_width + rect[0])+","+str(self.canvas_height - rect[1])+","+str(self.canvas_width + rect[2])+","+str(self.canvas_height - rect[3])

            #print str(math.sqrt(self.vrobot.l*self.vrobot.l+self.vrobot.l*self.vrobot.l)-self.vrobot.l)
            while d<3.1415*2+3.1415/4:
                #print "thingy "+str(math.sqrt(self.vrobot.l*self.vrobot.l+self.vrobot.l*self.vrobot.l)-abs(20/(math.cos(d))))
                #print str(math.sqrt(self.vrobot.l*self.vrobot.l+self.vrobot.l*self.vrobot.l))+" "+str(abs(20/(math.cos(d))))
                s=math.sqrt(self.vrobot.l*self.vrobot.l+self.vrobot.l*self.vrobot.l)-abs(20/(math.cos(d+a)))

                if (s==math.sqrt(self.vrobot.l*self.vrobot.l+self.vrobot.l*self.vrobot.l)):
                    s=0
            #    elif(s<math.sqrt(self.vrobot.l*self.vrobot.l+self.vrobot.l*self.vrobot.l) and s>self.vrobot.l):
            #        s+= abs(math.sin(d*3.1425))/6
            #    else:
            #        s-=abs(math.sin(d*3.1425))/6
                point = [self.canvas_width + self.vrobot.l * math.sin(d+a) + x-s,self.canvas_height-self.vrobot.l * math.cos(d+a) - y+s] #x coordinate, y coordinate
                #if(d%3.1415==0):
                    #print str(point[0]) +" "+str(point[1])
                if(self.canvas_width+rect[0]<point[0] and self.canvas_height-rect[1]>point[1] and self.canvas_width + rect[2]>point[0] and self.canvas_height - rect[3]<point[1]):  #checks for in box
                    #return True    
                    #print 'True'
                    #print str(point[0]) +" "+str(point[1])
                    return True
                d+=.1
        #print'false'
        return False


gRobotList = []

class GUIpart(object):    
    def __init__(self, gui_root, vWorld):
        self.gui_root = gui_root
        self.vWorld = vWorld

        # instance variables
        self.button4=None
        self.button5=None
        self.button6=None
        self.button8=None
        self.button11=None
        self.rCanvas = None
        self.xgoal=200
        self.ygoal=200
        self.numref={}
        self.numbox={}
        self.path=False
        self.initUI()

    def initUI(self):
        self.gui_root.title("Hamster Simulator")
        canvas_width = 440#440 # half width
        canvas_height = 300#300 # half height
        vRobot = self.vWorld.vrobot
        #creating the virtual appearance of the robot
        
        self.rCanvas = tk.Canvas(self.gui_root, bg="white", width=canvas_width*2, height=canvas_height*2)
        self.rCanvas.pack()
        self.vWorld.canvas = self.rCanvas
        self.vWorld.canvas_width = canvas_width
        self.vWorld.canvas_height = canvas_height

        # visual elements of the virtual robot 
        poly_points = [0,0,0,0,0,0,0,0]
        vRobot.poly_id = self.rCanvas.create_polygon(poly_points, fill='blue') #robot
        vRobot.prox_l_id = self.rCanvas.create_line(0,0,0,0, fill="red") #prox sensors
        vRobot.prox_r_id = self.rCanvas.create_line(0,0,0,0, fill="red")
        vRobot.floor_l_id = self.rCanvas.create_oval(0,0,0,0, outline="white", fill="white") #floor sensors
        vRobot.floor_r_id = self.rCanvas.create_oval(0,0,0,0, outline="white", fill="white")
        #time.sleep(1)

        button0 = tk.Button(self.gui_root,text="Grid")
        button0.pack(side='left')
        button0.bind('<Button-1>', self.drawGrid)

        button01 = tk.Button(self.gui_root,text="Go")
        button01.pack(side='left')
        button01.bind('<Button-1>', self.go)

        button1 = tk.Button(self.gui_root,text="Clear")
        button1.pack(side='left')
        button1.bind('<Button-1>', self.clearCanvas)

        button2 = tk.Button(self.gui_root,text="Reset")
        button2.pack(side='left')
        button2.bind('<Button-1>', self.resetvRobot)

        button3 = tk.Button(self.gui_root,text="Map")
        button3.pack(side='left')
        button3.bind('<Button-1>', self.drawMap)

        self.button11 = tk.Button(self.gui_root,text="Real Robot")
        self.button11.pack(side='left')
        self.button11.bind('<Button-1>', self.toggleRobot)

        button9 = tk.Button(self.gui_root,text="Exit")
        button9.pack(side='left')
        button9.bind('<Button-1>', self.exit_prog)

        self.gui_root.bind("<KeyPress>", self.keydown)
        self.gui_root.bind("<KeyRelease>", self.keyup)

        return

    def keydown(self, event):
        if event.char == 'w':
            self.move_up()
        elif event.char == 's':
            self.move_down()
        elif event.char == 'a':
            self.move_left()
        elif event.char == 'd':
            self.move_right()
        return

    def keyup(self, event):
        if event.char == 'w' or event.char == 's' or event.char == 'a' or event.char == 'd':
            self.stop_move()
        return

    def drawGrid(self, event=None):
        print "draw Grid"
        canvas_width = self.vWorld.canvas_width
        canvas_height = self.vWorld.canvas_height
        x1 = 0
        x2 = canvas_width*2
        y1 = 0
        y2 = canvas_height*2
        del_x = 40 #changed
        del_y = 40 #changed
        num_x = x2 / del_x
        num_y = y2 / del_y
        directions =[1,1,-1,-1]

        # draw center (0,0)
        self.rCanvas.create_rectangle(canvas_width-3,canvas_height-3,canvas_width+3,canvas_height+3, fill="red")
        # horizontal grid
        for i in range (0,num_y):
            y = i * del_y
            #self.rCanvas.create_text(x1,y,fill="black",text=10)
            self.rCanvas.create_line(x1, y, x2, y, fill="yellow")
        # verticle grid
        for j in range (0, num_x):
            x = j * del_x
            self.rCanvas.create_line(x, y1, x, y2, fill="yellow")       
        n=0
        while n < 4:
            count=1
            c=count+1
            x=self.xgoal
            y=self.ygoal
            x3=self.xgoal
            if(n%2==0):#vertical
                for j in range (0, 2*canvas_height/del_y):
                    y += directions[n]*del_y
                    self.rCanvas.create_text(x+5,y+5,fill="black",text=count)
                    self.numref[str(0)+","+str((j+1)*directions[n])]=count
                    count+=1
                    c=count
                    x3=self.xgoal
                    x4=self.xgoal
                    for h in range(0, 2*canvas_width/del_x):
                        x3+=directions[1]*del_x
                        self.rCanvas.create_text(x3+5,y+5,fill="black",text=c)
                        self.numref[str(h+1)+","+str((j+1)*directions[n])]=c
                        x4+=directions[2]*del_x
                        self.rCanvas.create_text(x4+5,y+5,fill="black",text=c)
                        self.numref[str(-1*(h+1))+","+str((j+1)*directions[n])]=c
                        c+=1
            else:#horizontal
                for i in range (0,2*canvas_width/del_x):
                    x+=directions[n]*del_x
                    self.rCanvas.create_text(x+5,y+5,fill="black",text=count)
                    self.numref[str((i+1)*directions[n])+","+str(0)]=count
                    count+=1
            n+=1

        for obs in self.vWorld.map:
            # rect x1,y1,x2,y2  rect5 = [0, -50, 40, 50]
            obsx= canvas_width+obs[0]
            obsy= canvas_height+obs[1]
            width=obs[2]-obs[0]
            length=40+obs[3]-obs[1]
            wx=width/del_x
            ly=length/del_y
            sx=obsx/del_x
            sy=obsy/del_y
            x=self.xgoal
            y=self.ygoal
            #for i in range(sx,wx+sx):
            #    for j in range(sy,ly+sy):
            #        print str(i)+" "+str(j)
            #        self.numref[str(i)+","+str(j)]=100
                    #self.rCanvas.itemconfig(self.numbox[str(i)+","+str(j)],text=100)
            #        print self.numref[str(i-x)+","+str(j-y)]
            for r in range(sy-1,sy+ly+1):
                for c in range(sx-1,wx+sx+1):
                    self.rCanvas.create_rectangle(c*del_x,r*del_y,c*del_x+del_x,r*del_y+del_y,fill="grey")
                    self.numref[str((c-x/del_x))+","+str(-1*(r-y/del_y))]=100
            for i in range(sx,wx+sx):
                for j in range(sy,ly+sy):
                    #print str(i)+" "+str(j)
                    self.numref[str(i-x/del_x)+","+str(-1*(j-y/del_y))]=100
                    self.rCanvas.create_rectangle(i*del_x,j*del_y,i*del_x+del_x,j*del_y+del_y,fill="black")
                    #print self.numref[str(i)+","+str(j)]
        self.rCanvas.create_text(self.xgoal+5,self.ygoal+5,fill="red",text=0)
        self.numref[str(0)+","+str(0)]=0
        self.vWorld.draw=True
        print self.numref
        return


    def apf(self,event=None):
        event=self.vWorld.event
        cdirection=self.vWorld.cdirection
        #if(event[2]==cdirection):
        #    self.mo
        #elif event[2]=='NorthWest':


        return

    def go(self,event=None):
        self.path=True


        return self.path

    def drawMap(self, event=None):
        self.vWorld.draw_map()
        return

    def resetvRobot(self, event=None):
        self.vWorld.vrobot.x = 220
        self.vWorld.vrobot.y = 0
        self.vWorld.vrobot.a = -1.571
        self.vWorld.goal_achieved = True
        self.vWorld.goal_list_index = 0
        return

    def clearCanvas(self, event=None):
        self.rCanvas.delete("all")
        poly_points = [0,0,0,0,0,0,0,0]
        self.vWorld.vrobot.poly_id = self.rCanvas.create_polygon(poly_points, fill='blue')
        self.vWorld.vrobot.prox_l_id = self.rCanvas.create_line(0,0,0,0, fill="red")
        self.vWorld.vrobot.prox_r_id = self.rCanvas.create_line(0,0,0,0, fill="red")
        self.vWorld.vrobot.floor_l_id = self.rCanvas.create_oval(0,0,0,0, outline="white", fill="white")
        self.vWorld.vrobot.floor_r_id = self.rCanvas.create_oval(0,0,0,0, outline="white", fill="white")
        return

    def toggleTrace(self, event=None):
        if self.vWorld.trace == True:
            self.vWorld.trace = False
            self.button4["text"] = "Trace"
        else:
            self.vWorld.trace = True
            self.button4["text"] = "No Trace"
        return

    def toggleProx(self, event=None):
        if self.vWorld.prox_dots == True:
            self.vWorld.prox_dots = False
            self.button5["text"] = "Prox Dots"
        else:
            self.vWorld.prox_dots = True
            self.button5["text"] = "No Prox Dots"
        return

    def toggleFloor(self, event=None):
        if self.vWorld.floor_dots == True:
            self.vWorld.floor_dots = False
            self.button6["text"] = "Floor Dots"
        else:
            self.vWorld.floor_dots = True
            self.button6["text"] = "No Floor Dots"
        return

    def toggleRobot(self, event=None):
        if self.vWorld.real_robot:
            robot = self.vWorld.real_robot
            robot.set_wheel(0,0)
            robot.set_wheel(1,0)
            self.vWorld.real_robot = False
            self.button11["text"] = "Real Robot"
        else:
            if (len(gRobotList) > 0):
                self.vWorld.real_robot = gRobotList[0]
                robot = self.vWorld.real_robot
                robot.set_wheel(0, self.vWorld.vrobot.sl)
                robot.set_wheel(1, self.vWorld.vrobot.sr) 
                self.button11["text"] = "Simulation"
        return

    def toggleGo(self, event=None):
        if self.vWorld.go:
            self.vWorld.go = False
            self.button8["text"] = "Go"
        else:
            self.vWorld.go = True
            self.button8["text"] = "Pause"
        return

    def getGoal(self, event):
        self.vWorld.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, outline = "blue")
        canvas_width = self.vWorld.canvas_width
        canvas_height = self.vWorld.canvas_height
        self.vWorld.goal_x = event.x - canvas_width
        self.vWorld.goal_y = canvas_height - event.y 
        return

    def move_up(self, event=None):
        self.vWorld.vrobot.sl = 30
        self.vWorld.vrobot.sr = 30
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def move_down(self, event=None):
        self.vWorld.vrobot.sl = -30
        self.vWorld.vrobot.sr = -30
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def move_left(self, event=None):
        self.vWorld.vrobot.sl = 10
        self.vWorld.vrobot.sr = 30
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def move_right(self, event=None):
        self.vWorld.vrobot.sl = 30
        self.vWorld.vrobot.sr = 10
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def stop_move(self, event=None):
        self.vWorld.vrobot.sl = 0
        self.vWorld.vrobot.sr = 0
        robot = self.vWorld.real_robot
        if robot:
            robot.set_wheel(0, self.vWorld.vrobot.sl)
            robot.set_wheel(1, self.vWorld.vrobot.sr)
        return

    def exit_prog(self, event=None):
        self.vWorld.gQuit = True
        self.gui_root.quit()
        for robot in gRobotList:
            robot.reset()
        return

    def draw_virtual_world(self):       
        self.vWorld.draw_robot()
        self.vWorld.draw_prox("left")
        self.vWorld.draw_prox("right")
        self.vWorld.draw_floor("left")
        self.vWorld.draw_floor("right")
        self.gui_root.after(50, self.draw_virtual_world)
        return

class VirtualHamsterWorld(object):
    def __init__(self):
        self.vrobot = None
        self.vworld = None
        self.gQuit = False
        self.numref={}
        self.event=[0,0,None]
        self.cdirection='West'
        self.create_world()

    def set_numref(self,n):
        self.numref=n
        return

    def check_box(self, currentD,x,y):
        print "check"
        minbox={}
        d=[1,1,-1,-1]
        event=""
        nextD=[x,y]
        c=[1,0,1,0]
        if(self.numref[str(x)+","+str(y)]==9 and (y==0)):
            nextD[c[0]]=1
            nextD[c[3]]=-1
        for i in range(0,4):
            if i%2==0:#even number 0,2 
                if self.numref[str(x)+","+str(y+d[i])]<self.numref[str(x)+","+str(y)]:
                    #minbox[d[i]]=(self.numref[str(x)+","+str(y+d[i])])
                    if d[i]==1:
                        event+='North'
                    else:
                        event+='South'
                    #nextD[c[i]]=nextD[c[i]]+d[i]
                    nextD[c[i]]=d[i]
            else:
                if self.numref[str(x+d[i])+","+str(y)]<self.numref[str(x)+","+str(y)]:
                    if d[i]==1:
                        event+='East'
                    else:
                        event+='West'
                    #nextD[c[i]]=nextD[c[i]]+d[i]
                    nextD[c[i]]=d[i]
        if((self.numref[str(x)+","+str(y)]==9 or self.numref[str(x)+","+str(y)]==8 or self.numref[str(x)+","+str(y)]==7 or self.numref[str(x)+","+str(y)]==6) and y==1):
            nextD[0]=-1
            nextD[1]=0  




        nextD.append(event)
        print "next Coordinate "+str(nextD)
        return nextD
        pass

    def create_world(self):       
        self.vrobot = virtual_robot()
        self.vrobot.t = time.time()

        #create the virtual worlds that contains the virtual robot
        self.vworld = virtual_world()
        self.vworld.vrobot = self.vrobot
        
        #objects in the world
        self.vworld.map = []

        # take out map to test real robot
        # local obstacle avoidance using APF
        rect1 = [-100, -180, 0, -140]
        rect2 = [-140, -180, -100, -80]
        rect3 = [-100, 140, 0, 180]
        rect4 = [-140, 80, -100, 180]
        rect5 = [0, -50, 40, 50]
        rect6 = [-260, -20, -220, 20]
        rect7 = [40, 60, 140, 100]

        self.vworld.area = [-300,-200,300,200]

        #self.vworld.add_obstacle(rect1)
        #self.vworld.add_obstacle(rect2)
        ##self.vworld.add_obstacle(rect3)
        #self.vworld.add_obstacle(rect4)
        self.vworld.add_obstacle(rect5)
        #self.vworld.add_obstacle(rect6)
        #self.vworld.add_obstacle(rect7)

        # set initial pose of robot wrt robot coordinate system
        self.vworld.vrobot.x = 220  # 200 pixels to the right from center(origin of robot coor. syst.)
        self.vworld.vrobot.y = 0
        self.vworld.vrobot.a = 1.5*3.1415    # facing west
    
        return

    # Update data components of the simulator.
    def update_virtual_world(self):
        waiting_for_robot = True

        while waiting_for_robot and self.vworld.real_robot:
            if len(gRobotList) > 0:
                robot = gRobotList[0] 
                waiting_for_robot = False
                #print "connected to robot"
            #else:
                #print "waiting for robot to connect"
            time.sleep(0.1)

        noise_prox = 35 # noise level for proximity
        noise_floor = 20 #floor ambient color - if floor is darker, set higher noise
        p_factor = 1.3 #proximity conversion - assuming linear
        #prox_conv_l = [0, 0, 0, 60, 50, 40, 30, 20, 20]
        prox_conv_l = [85,85,82,75,67,59,51,47,40,35]
        prox_conv_r = [85,85,82,75,67,59,51,47,40,35]

        #################################
        # Find the value of distance factor for your Hamster

        d_factor = 1 # travel distance conversion
        #################################

        #a_factor = 17.5 #turning speed of -15 vs angle 
        b = 35 #distance in mm, between two wheels

        vrobot = self.vworld.vrobot


        while not self.gQuit:
            t = time.time()
            del_t = t - vrobot.t
            vrobot.t = t # update the tick

            #NEW CODE FOR FINAL 
            #check blocks
            #goalx=self.vworld.goalx
            #goaly=self.vworld.goaly
            del_x = 40 #changed # same as above
            del_y = 40 #changed
            xcoord=1+math.trunc(round((180+vrobot.x)/del_x))
            ycoord=3+math.trunc(round((vrobot.y-200)/del_y))
            box = str(1+math.trunc(round((180+vrobot.x)/del_x))) +","+str(3+math.trunc(round((vrobot.y-200)/del_y)))
            print box
            direction='West'
            print self.numref
            #if self.vworld.path:
            if self.vworld.draw:
                self.event=self.check_box(direction,xcoord,ycoord)



            # compute new pose
            ms = (vrobot.sl*del_t+vrobot.sr*del_t)/2 #speed of the center
            new_vrobot_a = vrobot.a + (vrobot.sl-vrobot.sr)*del_t/b
            new_vrobot_x = vrobot.x + ms * math.sin(vrobot.a) * d_factor + self.event[0]
            new_vrobot_y = vrobot.y + ms * math.cos(vrobot.a) * d_factor + self.event[1]
            #time.sleep(.1)
            ##########################
            # If in collision, Hamster should stop moving, which means no update
            # of its pose.
            ##########################
            if not self.vworld.in_collision(new_vrobot_a, new_vrobot_x, new_vrobot_y):
                vrobot.a = new_vrobot_a
                vrobot.x = new_vrobot_x
                vrobot.y = new_vrobot_y






            while (vrobot.a >= 3.1415):
                vrobot.a -= 6.283

            # update sensors
            if (self.vworld.real_robot):    # convert prox sensor readings to number of pixels for the red beams
                robot = self.vworld.real_robot
                robot.set_wheel_balance(8)
                prox_l = robot.get_proximity(0)
                prox_r = robot.get_proximity(1)

                if (prox_l > noise_prox):
                    i = 0
                    while (prox_conv_l[i] > prox_l) and (i < 9):
                        i += 1
                    if (vrobot.dist_l and vrobot.sl == 0 and vrobot.sr == 0):
                        vrobot.dist_l = vrobot.dist_l*2.0 + i*10 + 10 - (prox_l - prox_conv_l[i])*10/(prox_conv_l[i-1] - prox_conv_l[i])
                        vrobot.dist_l = vrobot.dist_l / 3.0
                    else:
                        vrobot.dist_l = i*10 + 10 - (prox_l - prox_conv_l[i])*10/(prox_conv_l[i-1] - prox_conv_l[i])
                else:
                    vrobot.dist_l = False

                if (prox_r > noise_prox):
                    i = 0
                    while (prox_conv_r[i] > prox_r) and (i < 9):
                        i += 1
                    if (vrobot.dist_r and vrobot.sl == 0 and vrobot.sr == 0):
                        vrobot.dist_r = vrobot.dist_r*2.0 +i*10 + 10 - (prox_r - prox_conv_r[i])*10/(prox_conv_r[i-1] - prox_conv_r[i])
                        vrobot.dist_r = vrobot.dist_r / 3.0
                    else:
                        vrobot.dist_r = i*10 + 10 - (prox_r - prox_conv_r[i])*10/(prox_conv_r[i-1] - prox_conv_r[i])
                else:
                    vrobot.dist_r = False
            else:               # simulate prox sensors
                self.vworld.get_vrobot_prox("left")
                self.vworld.get_vrobot_prox("right")

            if (self.vworld.real_robot):
                floor_l = robot.get_floor(0)
                floor_r = robot.get_floor(1)
            else:
                floor_l = 100 #white
                floor_r = 100
            if (floor_l < noise_floor):
                vrobot.floor_l = floor_l
            else:
                vrobot.floor_l = False

            if (floor_r < noise_floor):
                vrobot.floor_r = floor_r
            else:
                vrobot.floor_r = False

            time.sleep(0.05)#.05
        return














def main():
    global gRobotList

    gMaxRobotNum = 1 # max number of robots to control
    comm = RobotComm(gMaxRobotNum)
    comm.start()
    #print 'Bluetooth starts'
    gRobotList = comm.robotList
    
    root = tk.Tk() #root

    world_handle = VirtualHamsterWorld()
    t_update_world = threading.Thread(name='update_world', target=world_handle.update_virtual_world)
    t_update_world.daemon = True
    t_update_world.start()



    gui_handle = GUIpart(root, world_handle.vworld)
    gui_handle.draw_virtual_world()     # this method runs in main thread

    world_handle.set_numref(gui_handle.numref)

    root.mainloop()

    comm.stop()
    comm.join()

if __name__== "__main__":
    sys.exit(main())




