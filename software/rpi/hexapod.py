#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Libraries
# https://circuitpython.readthedocs.io/projects/servokit/en/latest/
from adafruit_servokit import ServoKit

from leg import Leg

# python3-numpy
import numpy as np
import time
import json

SIN30 = 0.5
COS30 = 0.866
SIN45 = 0.7071
COS45 = 0.7071
SIN15 = 0.2588
COS15 = 0.9659


class Hexapod:

    def __init__(self):
        # x -> right
        # y -> front
        # z -> up
        # origin is the center of the body
        # roots are the positions of the bottom screws
        # length units are in mm
        # time units are in ms

        with open('./config.json', 'r') as read_file:
            self.config = json.load(read_file)

        self.mount_x = np.array(self.config['legMountX'])
        self.mount_y = np.array(self.config['legMountY'])
        self.root_j1 = self.config['legRootToJoint1']
        self.j1_j2 = self.config['legJoint1ToJoint2']
        self.j2_j3 = self.config['legJoint2ToJoint3']
        self.j3_tip = self.config['legJoint3ToTip']
        self.mount_angle = np.array(self.config['legMountAngle'])/180*np.pi

        self.mount_position = np.zeros((6, 3))
        self.mount_position[:, 0] = self.mount_x
        self.mount_position[:, 1] = self.mount_y

        # Objects
        self.pca_right = ServoKit(channels=16, address=0x40, frequency=120)
        self.pca_left = ServoKit(channels=16, address=0x41, frequency=120)

        # front right
        self.leg_0 = Leg(0,
                         [self.pca_left.servo[15], self.pca_left.servo[2],
                             self.pca_left.servo[1]],
                         correction=[-6, 4, -6])
        # center right
        self.leg_1 = Leg(1,
                         [self.pca_left.servo[7], self.pca_left.servo[8],
                             self.pca_left.servo[6]],
                         correction=[3, -5, -6])
        # rear right
        self.leg_2 = Leg(2,
                         [self.pca_left.servo[0], self.pca_left.servo[14],
                             self.pca_left.servo[13]],
                         correction=[3, -6, -5])
        # rear left
        self.leg_3 = Leg(3,
                         [self.pca_right.servo[15], self.pca_right.servo[1],
                             self.pca_right.servo[2]],
                         correction=[-3, -4, 6])
        # center left
        self.leg_4 = Leg(4,
                         [self.pca_right.servo[7], self.pca_right.servo[6],
                             self.pca_right.servo[8]],
                         correction=[-6, 2, 0])
        # front left
        self.leg_5 = Leg(5,
                         [self.pca_right.servo[0], self.pca_right.servo[13],
                             self.pca_right.servo[14]],
                         correction=[-6, 4, 0])

        # self.leg_0.reset()
        # self.leg_1.reset()
        # self.leg_2.reset()
        # self.leg_3.reset()
        # self.leg_4.reset()
        # self.leg_5.reset()

        self.standby()

        self.ik(self.standby_coordinate)
        print(self.angles)

    def standby(self):
        self.standby_coordinate = np.zeros((6, 3))

        self.standby_coordinate[:, 0] = np.array(self.mount_x)+(self.root_j1+self.j1_j2+(
            self.j2_j3*COS30)+self.j3_tip*SIN15)*np.cos(self.mount_angle)
        self.standby_coordinate[:, 1] = self.mount_y + (self.root_j1+self.j1_j2+(
            self.j2_j3*COS30)+self.j3_tip*SIN15)*np.sin(self.mount_angle)
        self.standby_coordinate[:, 2] = self.j2_j3 * \
            SIN30 - self.j3_tip * COS15

        self.leg_0.set_angle(0, 90)
        self.leg_0.set_angle(1, 60)
        self.leg_0.set_angle(2, 75)

        self.leg_1.set_angle(0, 90)
        self.leg_1.set_angle(1, 60)
        self.leg_1.set_angle(2, 75)

        self.leg_2.set_angle(0, 90)
        self.leg_2.set_angle(1, 60)
        self.leg_2.set_angle(2, 75)

        self.leg_3.set_angle(0, 90)
        self.leg_3.set_angle(1, 60)
        self.leg_3.set_angle(2, 75)

        self.leg_4.set_angle(0, 90)
        self.leg_4.set_angle(1, 60)
        self.leg_4.set_angle(2, 75)

        self.leg_5.set_angle(0, 90)
        self.leg_5.set_angle(1, 60)
        self.leg_5.set_angle(2, 75)

    def ik(self, to):
        temp_to = to-self.mount_position
        to[:, 0] = temp_to[:, 0] * \
            np.cos(self.mount_angle) + temp_to[:, 1] * np.sin(self.mount_angle)
        to[:, 1] = temp_to[:, 0] * \
            np.sin(self.mount_angle) - temp_to[:, 1] * np.cos(self.mount_angle)
        to[:, 2] = temp_to[:, 2]

        self.angles = np.zeros((6, 3))
        x = to[:, 0] - self.root_j1
        y = to[:, 1]

        self.angles[:, 0] = (np.arctan2(y, x) * 180 / np.pi)+90

        x = np.sqrt(x*x + y*y) - self.j1_j2
        y = to[:, 2]
        ar = np.arctan2(y, x)
        lr2 = x*x + y*y
        lr = np.sqrt(lr2)
        a1 = np.arccos((lr2 + self.j2_j3*self.j2_j3 -
                        self.j3_tip*self.j3_tip)/(2*self.j2_j3*lr))
        a2 = np.arccos((lr2 - self.j2_j3*self.j2_j3 +
                        self.j3_tip*self.j3_tip)/(2*self.j3_tip*lr))

        self.angles[:, 1] = 90-((ar + a1) * 180 / np.pi)
        self.angles[:, 2] = (90 - ((a1 + a2) * 180 / np.pi))+90


def main():

    hexapod = Hexapod()


if __name__ == '__main__':
    main()
