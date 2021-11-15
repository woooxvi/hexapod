#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Libraries
# https://circuitpython.readthedocs.io/projects/servokit/en/latest/
from adafruit_servokit import ServoKit

import time

# Constants
nbPCAServo = 16


# Objects
pca1 = ServoKit(channels=16, address=0x40, frequency=120)
pca2 = ServoKit(channels=16, address=0x41, frequency=120)

# function init


def init():
    print('Init')

    # for i in range(nbPCAServo):
    #     pca1.servo[i].set_pulse_width_range(MIN_IMP[i] , MAX_IMP[i])
    #     pca2.servo[i].set_pulse_width_range(MIN_IMP[i] , MAX_IMP[i])

# function main


def main():

    pcaScenario()


# function pcaScenario
def pcaScenario():
    """Scenario to test servo"""
    for i in range(nbPCAServo):
        pca1.servo[i].angle = 90
        pca2.servo[i].angle = 90
        # for j in range(MIN_ANG[i], MAX_ANG[i], 1):
        #     print("Send angle {} to Servo {}".format(j, i))
        #     pca.servo[i].angle = j
        #     time.sleep(0.01)
        # for j in range(MAX_ANG[i], MIN_ANG[i], -1):
        #     print("Send angle {} to Servo {}".format(j, i))
        #     pca.servo[i].angle = j
        #     time.sleep(0.01)
        # pca.servo[i].angle = None  # disable channel
    time.sleep(0.5)


if __name__ == '__main__':
    init()
    main()
