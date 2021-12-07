#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Libraries
# https://circuitpython.readthedocs.io/projects/servokit/en/latest/
from adafruit_servokit import ServoKit

from leg import Leg

import time


class Hexapod:

    def __init__(self):
        # Objects
        self.pca_right = ServoKit(channels=16, address=0x40, frequency=120)
        self.pca_left = ServoKit(channels=16, address=0x41, frequency=120)

        # rear right
        self.leg_0 = Leg('rr',
                         [self.pca_left.servo[15], self.pca_left.servo[2],
                             self.pca_left.servo[1]],
                         correction=[0, 0, 0],
                         constraint=[0, 180])
        # center right
        self.leg_1 = Leg('cr',
                         [self.pca_left.servo[7], self.pca_left.servo[8],
                             self.pca_left.servo[6]],
                         correction=[0, 0, 0],
                         constraint=[0, 180])
        # front right
        self.leg_2 = Leg('fr',
                         [self.pca_left.servo[0], self.pca_left.servo[14],
                             self.pca_left.servo[13]],
                         correction=[0, 0, 0],
                         constraint=[0, 180])
        # front left
        self.leg_3 = Leg('fl',
                         [self.pca_right.servo[15], self.pca_right.servo[1],
                             self.pca_right.servo[2]],
                         correction=[0, 0, 0],
                         constraint=[0, 180])
        # center left
        self.leg_4 = Leg('cl',
                         [self.pca_right.servo[7], self.pca_right.servo[6],
                             self.pca_right.servo[8]],
                         correction=[0, 0, 0],
                         constraint=[0, 180])
        # rear left
        self.leg_5 = Leg('rl',
                         [self.pca_right.servo[0], self.pca_right.servo[13],
                             self.pca_right.servo[14]],
                         correction=[0, 0, 0],
                         constraint=[0, 180])

        self.leg_0.set_angle(0, 90)
        self.leg_0.set_angle(1, 90)
        self.leg_0.set_angle(2, 90)

        self.leg_1.set_angle(0, 90)
        self.leg_1.set_angle(1, 90)
        self.leg_1.set_angle(2, 90)

        self.leg_2.set_angle(0, 90)
        self.leg_2.set_angle(1, 90)
        self.leg_2.set_angle(2, 90)

        self.leg_3.set_angle(0, 90)
        self.leg_3.set_angle(1, 90)
        self.leg_3.set_angle(2, 90)

        self.leg_4.set_angle(0, 90)
        self.leg_4.set_angle(1, 90)
        self.leg_4.set_angle(2, 90)

        self.leg_5.set_angle(0, 90)
        self.leg_5.set_angle(1, 90)
        self.leg_5.set_angle(2, 90)


def main():

    hexapod = Hexapod()


if __name__ == '__main__':
    main()
