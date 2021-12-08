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

        with open('./config.json', 'r') as read_file:
            self.config = json.load(read_file)

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

        self.leg_0.reset()
        self.leg_1.reset()
        self.leg_2.reset()
        self.leg_3.reset()
        self.leg_4.reset()
        self.leg_5.reset()

    def standby(self):
        self.standby_coordinate = np.zeros((6, 3))
        self.standby_coordinate[:, 2] = self.config['legJoint3ToTip'] * \
            COS15 - self.config['legJoint2ToJoint3']*SIN30
        self.standby_coordinate[:, 0] = np.array(self.config['legMountX'])+(self.config['legRootToJoint1']+self.config['legJoint1ToJoint2']+(
            self.config['legJoint2ToJoint3']*COS30)+self.config['legJoint3ToTip']*SIN15)*COS45
        self.standby_coordinate[:, 1] = np.array(self.config['legMountY']) + (self.config['legRootToJoint1']+self.config['legJoint1ToJoint2']+(
            self.config['legJoint2ToJoint3']*COS30)+self.config['legJoint3ToTip']*SIN15)*SIN45


def main():

    hexapod = Hexapod()


if __name__ == '__main__':
    main()
