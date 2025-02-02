#!/usr/bin/env python

'''
Coordinates the movements of the tilting stand and the gathering of laser scan data.
Saves the angle and laser scan data into a PointCloudSliceMsg and publishes this message.

Obtains the laser scan by subscribing to ROS topic "scan".
Obtains the current tilt angle by subscribing to ROS topic "angle".

Controls when the tilting stand takes a step in tilt angle by publishing to ROS topic "step".
Gathers the laser scan and angle information and publishes them onto ROS topic "slice".
'''

import rospy                        #for interacting with ROS topics and parameters
import sys, getopt                  #for parameters and sys.exit()
from std_msgs.msg import Float64, Int32
from sensor_msgs.msg import PointCloud2, LaserScan
from tilting_lidar_scanner.msg import PointCloudSliceMsg

import re                           #for findall()
import string                       #for split()
import time

# Change this to change the speed of this program:
hertz = 100

first = True

# initialize ROS node
rospy.init_node('PC_Generator', anonymous=True)

# instantiate publisher
stepPublisher = rospy.Publisher("step", Int32, queue_size = 0)
slicePublisher = rospy.Publisher("slice", PointCloudSliceMsg, queue_size = 0)
# cloudPublisher = rospy.Publisher("pointCloud", PointCloud2, queue_size = 0)

# instantiate messages to publish
stepMsg = Int32()
cloudMsg = PointCloud2()

# Explicitly declare these global variables (probably not necessary)
currentAngle = None
currentScan = None

# Declare some ROS topic subscriber callback function
def scanCallback(msg):
    global currentScan
    #print "PCG: scanCallback called"
    currentScan = msg

def angleCallback(msg):
    global currentAngle
    #print "PCG: angleCallback called, angle is {0}".format(msg.data)
    currentAngle = msg.data


# Instantiate the subscribers
scanSubscriber  = rospy.Subscriber("scan", LaserScan, scanCallback)
angleSubscriber = rospy.Subscriber("angle", Float64, angleCallback)

def firstScan():
    global currentAngle
    # Since this is our first scan, there will be no angle data
    # as the angle is 0.0
    currentAngle = 0.0
    print "The first angle is: 0.0"

    # Wait until we receive a scan from the LiDAR scanner
    done = False
    while not done and not rospy.is_shutdown():
        if currentScan == None:
            print "PCG: Has not found first scan yet..."
        else:
            # We have received the scan now, which is stored in currentScan
            print "PCG: The first scan is {0}".format(currentScan)
            # Now we can leave this loop
            done = True
    # We have finished our first scan and can now go on to the main loop

# Create a rate control object
rate = rospy.Rate(hertz)

while not rospy.is_shutdown():

    if first and currentAngle == None:
        firstScan()
        first = False

        lsaMsg = PointCloudSliceMsg()
        lsaMsg.laserScan = currentScan
        lsaMsg.tiltAngle = currentAngle
        slicePublisher.publish(lsaMsg)

        currentScan = None
        currentAngle = None

        time.sleep(.1)
        # Take a step, and then we wait for the angle return data
        stepPublisher.publish(stepMsg)
        print "PCG: Take a step."
    else:

        # Wait until we get an angle back from the TSN (Tilting Stand Node)\
        print "PCG: Waiting for angle..."
        done = False
        while not done and not rospy.is_shutdown():

            # Very temporary -------- REMOVE ME ----------
            if currentAngle == 0.0:
                print "I HAVE FINISHED!!!"
                time.sleep(200)
            # Very temporary -------- REMOVE ME ----------

            if currentAngle == None:
                print "PCG: Did not receive current angle yet..."
            else:
                print "PCG: The current angle is {0}".format(currentAngle)
                done = True

        currentScan = None

        #time.sleep(1)

        # Wait until we receive a scan from the LiDAR scanner
        print "PCG: Waiting for LiDAR scan..."
        done = False
        while not done and not rospy.is_shutdown():
            if currentScan == None:
                print "PCG: Did not receive current scan yet..."
            else:
                # We have received the scan now, which is stored in currentScan
                #print "PCG: The current scan is {0}".format(currentScan)
                print "We have received SCAN data!"
                done = True


        if currentAngle != None and currentScan != None:
            #print "PCG: Got both laser scan data and angle data!"
            # TODO: Store this information in a data structure
            # Check if we've received a full point cloud scan
            # (for each angle between 0 and 90 degrees, we got a laser scan)
            # If we got the full point cloud scan, do some math to
            # generate the actual point cloud message


            # At this point we should have the angle and the scan
            # Now we can combine it into one message and publish it as cloudMsg
            print "------- WE HAVE BOTH ANGLE AND SCAN DATA -------"

            lsaMsg = PointCloudSliceMsg()
            lsaMsg.laserScan = currentScan
            lsaMsg.tiltAngle = currentAngle
            slicePublisher.publish(lsaMsg)

            # Reset the scan and angle data
            currentScan = None
            currentAngle = None

            # Take a step, and then we wait for the angle return data
            stepPublisher.publish(stepMsg)
            print "PCG: Take a step."

    # cloudPublisher.publish(cloudMsg)

    rate.sleep()


print "PCG done, waiting until ctrl+c is hit..."
rospy.spin()  # just to prevent this node from exiting