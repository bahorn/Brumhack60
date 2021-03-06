
################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import threading
import Tkinter as tk
from socketIO_client import SocketIO

hostname = "<INSERT HOST HERE>"
right = [0,0,0]
left = [0,0,0]

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, height=500, width=500, bg='white')
        self.canvas.pack(padx=10,pady=10)
        self.right = self.canvas.create_oval(100,100,50, 50,fill="#eee")
        self.left = self.canvas.create_oval(100, 100, 50, 50, fill="#111")
        self.canvas.after(50, self.updatePosition)
        self.canvas.update()
        self.root.mainloop()
   
    def updatePosition(self):
        global right, left
        
        Red=hex(int(right[1]/8)%255)[2:]
        Blue=hex(int(right[1]/8)%255)[2:]
        Green=hex(int(right[1]/8)%255)[2:]
        
        Col="#"+str(Red)+str(Blue)+str(Green)
        
        while len(Col)<7:
            Col+="8"
        
        self.canvas.itemconfig(self.right, fill=Col)
        self.canvas.itemconfig(self.left, fill=Col)
        for i in range(0,len(right)):
            right[i] = right[i]+250
        for i in range(0,len(left)):
            left[i] = left[i]+250
        count = right[1]/5
        self.canvas.coords(self.right, right[0], right[2], 
            right[0]+count, right[2]+count)
        count = left[1]/5
        self.canvas.coords(self.left, left[0], left[2],
            left[0]+count, left[2]+count)
        self.canvas.update()
        self.canvas.after(10, self.updatePosition)

class SampleListener(Leap.Listener):
    finger_names = ['Thb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
	global hostname
        print "Initialized"
        self.socketio = SocketIO(hostname, 5000)
    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);
        controller.config.set("Gesture.ScreenTap.MinDistance", 1.0)
    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        global right, left
        t_pos = [0,0,0]
        t_dir = [0,0,0]
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        #print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
        #      frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

#            print "  %s, id %d, position: %s" % (
#                handType, hand.id, hand.palm_position)

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction
            if hand.is_left:
                left[0] = hand.palm_position[0]
                left[1] = hand.palm_position[1]
                left[2] = hand.palm_position[2]
            else:
                right[0] = hand.palm_position[0]
                right[1] = hand.palm_position[1]
                right[2] = hand.palm_position[2]

            self.socketio.emit('input', 
                {
                    "action":"move",
                    "value":{
                        "hand":handType,
                        "direction":[
                            hand.palm_position[0],
                            hand.palm_position[1],
                            hand.palm_position[2]
                        ]
                    },
                        "timestamp":frame.timestamp
                })

            # Calculate the hand's pitch, roll, and yaw angles
            '''print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
                direction.pitch * Leap.RAD_TO_DEG,
                normal.roll * Leap.RAD_TO_DEG,
                direction.yaw * Leap.RAD_TO_DEG)'''

            # Get arm bone
            arm = hand.arm
            '''print "  Arm direction: %s, wrist position: %s, elbow position: %s" % (
            arm.direction,
            arm.wrist_position,
            arm.elbow_position)'''

            # Get fingers
            for finger in hand.fingers:

                '''print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
                    self.finger_names[finger.type],
                    finger.id,
                    finger.length,
                    finger.width)'''
                
                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    '''print "      Bone: %s, start: %s, end: %s, direction: %s" % (
                        self.bone_names[bone.type],
                        bone.prev_joint,
                        bone.next_joint,
                        bone.direction)'''
            
        # Get tools
        for tool in frame.tools:

            '''print "  Tool id: %d, position: %s, direction: %s" % (
                tool.id, tool.tip_position, tool.direction)'''

        # Get gestures
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gesture)

                # Determine clock direction using the angle between the pointable and the circle normal
                if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                    clockwiseness = "clockwise"
                else:
                    clockwiseness = "counterclockwise"

                # Calculate the angle swept since the last frame
                swept_angle = 0
                if circle.state != Leap.Gesture.STATE_START:
                    previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                    swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                '''print "  Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                        gesture.id, self.state_names[gesture.state],
                        circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)'''

            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                ''' print "  Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                        gesture.id, self.state_names[gesture.state],
                        swipe.position, swipe.direction, swipe.speed)'''
                for i in range(0, 3):
                    t_pos[i] = swipe.position[i]
                for i in range(0, 3):
                    t_dir[i] = swipe.direction[i]
                self.socketio.emit('input', 
                    {
                        "action":"swipe",
                        "value":{
                            "speed":swipe.speed,
                            "position":t_pos, 
                            "direction":t_dir
                        },
                        "timestamp":frame.timestamp
                    })
            if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                keytap = KeyTapGesture(gesture)
                print "  Key Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_names[gesture.state],
                        keytap.position, keytap.direction )
                for i in range(0, 3):
                    t_pos[i] = keytap.position[i]
                for i in range(0, 3):
                    t_dir[i] = keytap.direction[i]
                self.socketio.emit('input',
                    {
                        "action":"keytap",
                        "value":{
                            "position":t_pos,
                            "direction":t_dir
                        },
                        "timestamp":frame.timestamp
                    })
            if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                screentap = ScreenTapGesture(gesture)
                print "  Screen Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_names[gesture.state],
                        screentap.position, screentap.direction )
                for i in range(0, 3):
                    t_pos[i] = screentap.position[i]
                for i in range(0, 3):
                    t_dir[i] = screentap.direction[i]
                self.socketio.emit('input',
                    {
                        "action":"screentap",
                        "value":{
                            "position":t_pos,
                            "direction":t_dir
                        },
                        "timestamp":frame.timestamp
                    })
        if not (frame.hands.is_empty and frame.gestures().is_empty):
            pass

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

def uilol():
    a = GUI()

if __name__ == "__main__":
    t = threading.Thread(target=main)
    t.start()
    t = threading.Thread(target=uilol)
    t.start()

