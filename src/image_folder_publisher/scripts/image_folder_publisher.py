#!/usr/bin/env python
from __future__ import print_function

import roslib
roslib.load_manifest('image_folder_publisher')

import sys
import os
from os import listdir
from os.path import isfile, join

import rospy
import cv2

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class image_folder_publisher:
    def __init__(self):
        self.__app_name = "image_folder_publisher"

        self._cv_bridge_left = CvBridge()
        self._cv_bridge_right = CvBridge()

        self._topic_name_left = rospy.get_param('~topic_name_left', '/image_raw_left')
        self._topic_name_right = rospy.get_param('~topic_name_right', '/image_raw_right')
        rospy.loginfo("[%s] (topic_name) Publishing Images to topic  %s", self.__app_name, self._topic_name_left)
        rospy.loginfo("[%s] (topic_name) Publishing Images to topic  %s", self.__app_name, self._topic_name_right)

        self._image_publisher_left = rospy.Publisher(self._topic_name_left, Image, queue_size=1)
        self._image_publisher_right = rospy.Publisher(self._topic_name_right, Image, queue_size=1)

        self._rate = rospy.get_param('~publish_rate', 15)
        rospy.loginfo("[%s] (publish_rate) Publish rate set to %s hz", self.__app_name, self._rate)

        self._sort_files = rospy.get_param('~sort_files', True)
        rospy.loginfo("[%s] (sort_files) Sort Files: %r", self.__app_name, self._sort_files)

        self._frame_id = rospy.get_param('~frame_id', 'camera')
        rospy.loginfo("[%s] (frame_id) Frame ID set to  %s", self.__app_name, self._frame_id)

        self._loop = rospy.get_param('~loop', 1)
        rospy.loginfo("[%s] (loop) Loop  %d time(s) (set it -1 for infinite)", self.__app_name, self._loop)

        self._image_folder = rospy.get_param('~image_folder', '')
        if self._image_folder == '' or not os.path.exists(self._image_folder) or not os.path.isdir(self._image_folder):
            #import pdb; pdb.set_trace()
            rospy.logfatal("[%s] (image_folder) Invalid Image folder", self.__app_name)
            sys.exit(0)
        rospy.loginfo("[%s] Reading images from %s", self.__app_name, self._image_folder)

    def run(self):
        ros_rate = rospy.Rate(self._rate)

        dir_left=self._image_folder + '/left/'
        dir_right=self._image_folder + '/right/'
        #import pdb; pdb.set_trace()

        files_in_dir_right = [f for f in listdir(dir_right) if  isfile(join(dir_right, f))]
        files_in_dir_left = [f for f in listdir(dir_left) if isfile(join(dir_left, f))]
        if self._sort_files:
            files_in_dir_left.sort()
        try:
            while self._loop != 0:
                for f in files_in_dir_left:
                    if not rospy.is_shutdown():
                        if isfile(join(dir_left, f)):
                            cv_image_left = cv2.imread(join(dir_left, f))
                            cv_image_right = cv2.imread(join(dir_right,'right'+f[4:]))

                            #import pdb; pdb.set_trace()
                            if cv_image_left is not None:
                                ros_msg = self._cv_bridge_left.cv2_to_imgmsg(cv_image_left, "bgr8")
                                ros_msg.header.frame_id = self._frame_id
                                ros_msg.header.stamp = rospy.Time.now()
                                self._image_publisher_left.publish(ros_msg)
                                ros_msg = self._cv_bridge_right.cv2_to_imgmsg(cv_image_right, "bgr8")
                                ros_msg.header.frame_id = self._frame_id
                                ros_msg.header.stamp = rospy.Time.now()
                                self._image_publisher_right.publish(ros_msg)

                                rospy.loginfo("[%s] Published %s", self.__app_name, join(self._image_folder, f))
                            else:
                                rospy.loginfo("[%s] Invalid image file %s", self.__app_name, join(self._image_folder, f))
                            ros_rate.sleep()
                    else:
                        return
                self._loop = self._loop - 1
        except CvBridgeError as e:
            rospy.logerr(e)

def main(args):
    rospy.init_node('image_folder_publisher', anonymous=True)

    image_publisher = image_folder_publisher()
    image_publisher.run()


if __name__ == '__main__':
    main(sys.argv)
