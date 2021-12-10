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
from path_generator import gen_forward_path, gen_backward_path
from path_generator import gen_fastforward_path, gen_fastbackward_path
from path_generator import gen_leftturn_path, gen_rightturn_path
from path_generator import gen_shiftleft_path, gen_shiftright_path
from path_generator import gen_climb_path
from path_generator import gen_rotatex_path


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

        self.standby_coordinate = self.calculate_standby_coordinate(60, 75)
        self.forward_path = gen_forward_path()
        self.backward_path = gen_backward_path()
        self.fastforward_path = gen_fastforward_path()
        self.fastbackward_path = gen_fastbackward_path()

        self.leftturn_path = gen_leftturn_path()
        self.rightturn_path = gen_rightturn_path()

        self.shiftleft_path = gen_shiftleft_path()
        self.shiftright_path = gen_shiftright_path()

        self.climb_path = gen_climb_path()

        self.rotatex_path = gen_rotatex_path(self.standby_coordinate)

        self.standby()
        time.sleep(1)

        # for mm in range(0, 20):
        #     self.move(self.forward_path, 0.005)

        # for mm in range(0, 20):
        #     self.move(self.backward_path, 0.005)

        # for mm in range(0, 20):
        #     self.move(self.fastforward_path, 0.005)

        # for mm in range(0, 20):
        #     self.move(self.fastbackward_path, 0.005)

        # for mm in range(0, 20):
        #     self.move(self.leftturn_path, 0.005)

        # for mm in range(0, 20):
        #     self.move(self.rightturn_path, 0.005)

        # for mm in range(0, 20):
        #     self.move(self.shiftleft_path, 0.005)

        # for mm in range(0, 20):
        #     self.move(self.shiftright_path, 0.005)

        # for mm in range(0, 20):
        #     self.move(self.climb_path, 0.005)


        self.move(self.rotatex_path, 0.005)

        time.sleep(1)
        self.standby()

    def calculate_standby_coordinate(self, j2_angle, j3_angle):
        j2_rad = j2_angle/180*np.pi
        j3_rad = j3_angle/180*np.pi
        standby_coordinate = np.zeros((6, 3))

        standby_coordinate[:, 0] = self.mount_x+(self.root_j1+self.j1_j2+(
            self.j2_j3*np.sin(j2_rad))+self.j3_tip*np.cos(j3_rad))*np.cos(self.mount_angle)
        standby_coordinate[:, 1] = self.mount_y + (self.root_j1+self.j1_j2+(
            self.j2_j3*np.sin(j2_rad))+self.j3_tip*np.cos(j3_rad))*np.sin(self.mount_angle)
        standby_coordinate[:, 2] = self.j2_j3 * \
            np.cos(j2_rad) - self.j3_tip * \
            np.sin(j3_rad)
        return standby_coordinate

    def move(self, path, interval):
        for p_idx in range(0, np.shape(path)[0]):
            # dest = path[p_idx, :, :]+self.standby_coordinate
            dest = path[p_idx, :, :]
            angles = self.inverse_kinematics(dest)

            self.leg_0.move_junctions(angles[0, :])
            self.leg_5.move_junctions(angles[5, :])

            self.leg_1.move_junctions(angles[1, :])
            self.leg_4.move_junctions(angles[4, :])

            self.leg_2.move_junctions(angles[2, :])
            self.leg_3.move_junctions(angles[3, :])

            time.sleep(interval)

    def standby(self):
        dest = self.standby_coordinate
        angles = self.inverse_kinematics(dest)

        self.leg_0.move_junctions(angles[0, :])
        self.leg_5.move_junctions(angles[5, :])

        self.leg_1.move_junctions(angles[1, :])
        self.leg_4.move_junctions(angles[4, :])

        self.leg_2.move_junctions(angles[2, :])
        self.leg_3.move_junctions(angles[3, :])

    def inverse_kinematics(self, dest):
        temp_dest = dest-self.mount_position
        local_dest = np.zeros_like(dest)
        local_dest[:, 0] = temp_dest[:, 0] * \
            np.cos(self.mount_angle) + \
            temp_dest[:, 1] * np.sin(self.mount_angle)
        local_dest[:, 1] = temp_dest[:, 0] * \
            np.sin(self.mount_angle) - \
            temp_dest[:, 1] * np.cos(self.mount_angle)
        local_dest[:, 2] = temp_dest[:, 2]

        angles = np.zeros((6, 3))
        x = local_dest[:, 0] - self.root_j1
        y = local_dest[:, 1]

        angles[:, 0] = -(np.arctan2(y, x) * 180 / np.pi)+90

        x = np.sqrt(x*x + y*y) - self.j1_j2
        y = local_dest[:, 2]
        ar = np.arctan2(y, x)
        lr2 = x*x + y*y
        lr = np.sqrt(lr2)
        a1 = np.arccos((lr2 + self.j2_j3*self.j2_j3 -
                        self.j3_tip*self.j3_tip)/(2*self.j2_j3*lr))
        a2 = np.arccos((lr2 - self.j2_j3*self.j2_j3 +
                        self.j3_tip*self.j3_tip)/(2*self.j3_tip*lr))

        angles[:, 1] = 90-((ar + a1) * 180 / np.pi)
        angles[:, 2] = (90 - ((a1 + a2) * 180 / np.pi))+90

        return angles


def main():

    hexapod = Hexapod()


if __name__ == '__main__':
    main()
