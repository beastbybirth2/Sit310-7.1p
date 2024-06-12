#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped, AprilTagDetectionArray

class Target_Follower:
    def __init__(self):
        # Initialize the ROS node
        rospy.init_node('target_follower_node', anonymous=True)

        # Set up the shutdown hook
        rospy.on_shutdown(self.shutdown_handler)

        # Publisher for velocity commands
        self.velocity_publisher = rospy.Publisher('/duckieshop/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        # Subscriber for AprilTag detections
        self.tag_subscriber = rospy.Subscriber('/duckieshop/apriltag_detector_node/detections', AprilTagDetectionArray, self.detection_callback, queue_size=1)
        
        rospy.spin()  # Keep the node running

    # Callback function for AprilTag detections
    def detection_callback(self, msg):
        self.process_detections(msg.detections)

    # Function to handle safe shutdown
    def shutdown_handler(self):
        rospy.loginfo("Shutting down. Stopping the robot...")
        self.halt_robot()

    # Function to stop the robot by sending zero velocity
    def halt_robot(self):
        stop_msg = Twist2DStamped()
        stop_msg.header.stamp = rospy.Time.now()
        stop_msg.v = 0.0
        stop_msg.omega = 0.0
        self.velocity_publisher.publish(stop_msg)

    # Function to process detections and move the robot accordingly
    def process_detections(self, detections):
        if not detections:
            self.halt_robot()
            return

        # Get the position of the first detected tag
        tag_position = detections[0].transform.translation
        x, y, z = tag_position.x, tag_position.y, tag_position.z

        rospy.loginfo("Tag position: x=%f, y=%f, z=%f", x, y, z)
        rospy.sleep(1)

        # Move forward if the tag is far
        if z > 0.15:
            self.send_velocity(0.2, 0)
        
        # Move backward if the tag is too close
        elif z < 0.10:
            self.send_velocity(-0.2, 0)
        
        # Rotate left if the tag is to the right
        elif x > 0.05:
            self.send_velocity(0, -0.4)
        
        # Rotate right if the tag is to the left
        elif x < -0.05:
            self.send_velocity(0, 0.4)
        
        # Stop the robot after the command
        self.halt_robot()

    # Function to send velocity commands to the robot
    def send_velocity(self, linear_velocity, angular_velocity):
        velocity_msg = Twist2DStamped()
        velocity_msg.header.stamp = rospy.Time.now()
        velocity_msg.v = linear_velocity
        velocity_msg.omega = angular_velocity
        self.velocity_publisher.publish(velocity_msg)
        rospy.sleep(0.2)

if __name__ == '__main__':
    try:
        Target_Follower()
    except rospy.ROSInterruptException:
        pass
