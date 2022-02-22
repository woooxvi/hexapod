#!python
#
# 2021  Zhengyu Peng
# Website: https://zpeng.me
#
# `                      `
# -:.                  -#:
# -//:.              -###:
# -////:.          -#####:
# -/:.://:.      -###++##:
# ..   `://:-  -###+. :##:
#        `:/+####+.   :##:
# .::::::::/+###.     :##:
# .////-----+##:    `:###:
#  `-//:.   :##:  `:###/.
#    `-//:. :##:`:###/.
#      `-//:+######/.
#        `-/+####/.
#          `+##+.
#           :##:
#           :##:
#           :##:
#           :##:
#           :##:
#            .+:

# Libraries
# https://circuitpython.readthedocs.io/projects/servokit/en/latest/
from adafruit_servokit import ServoKit

from leg import Leg

from queue import Queue, Empty

# python3-numpy
import numpy as np
import time
import json
from path_generator import gen_forward_path, gen_backward_path
from path_generator import gen_fastforward_path, gen_fastbackward_path
from path_generator import gen_leftturn_path, gen_rightturn_path
from path_generator import gen_shiftleft_path, gen_shiftright_path
from path_generator import gen_climb_path
from path_generator import gen_rotatex_path, gen_rotatey_path, gen_rotatez_path
from path_generator import gen_twist_path

from threading import Thread

from tcpserver import TCPServer
from btserver import BluetoothServer


class Hexapod(Thread):

    def __init__(self, in_cmd_queue):
        Thread.__init__(self)

        self.cmd_queue = in_cmd_queue
        self.interval = 0.005
        # x -> right
        # y -> front
        # z -> up
        # origin is the center of the body
        # roots are the positions of the bottom screws
        # length units are in mm
        # time units are in ms

        with open('/home/pi/hexapod/software/raspberry pi/config.json', 'r') as read_file:
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
                         correction=[4, 6, 2])
        # center right
        self.leg_1 = Leg(1,
                         [self.pca_left.servo[7], self.pca_left.servo[8],
                             self.pca_left.servo[6]],
                         correction=[0, 8, -6])
        # rear right
        self.leg_2 = Leg(2,
                         [self.pca_left.servo[0], self.pca_left.servo[14],
                             self.pca_left.servo[13]],
                         correction=[2, 8, -1])
        # rear left
        self.leg_3 = Leg(3,
                         [self.pca_right.servo[15], self.pca_right.servo[1],
                             self.pca_right.servo[2]],
                         correction=[-3, 10, -8])
        # center left
        self.leg_4 = Leg(4,
                         [self.pca_right.servo[7], self.pca_right.servo[6],
                             self.pca_right.servo[8]],
                         correction=[-6, 2, -4])
        # front left
        self.leg_5 = Leg(5,
                         [self.pca_right.servo[0], self.pca_right.servo[13],
                             self.pca_right.servo[14]],
                         correction=[0, 0, -10])

        # self.leg_0.reset(True)
        # self.leg_1.reset(True)
        # self.leg_2.reset(True)
        # self.leg_3.reset(True)
        # self.leg_4.reset(True)
        # self.leg_5.reset(True)

        self.standby_coordinate = self.calculate_standby_coordinate(60, 75)
        self.laydown_coordinate = self.calculate_standby_coordinate(0, 15)
        self.forward_path = gen_forward_path(self.standby_coordinate)
        self.backward_path = gen_backward_path(self.standby_coordinate)
        self.fastforward_path = gen_fastforward_path(self.standby_coordinate)
        self.fastbackward_path = gen_fastbackward_path(self.standby_coordinate)

        self.leftturn_path = gen_leftturn_path(self.standby_coordinate)
        self.rightturn_path = gen_rightturn_path(self.standby_coordinate)

        self.shiftleft_path = gen_shiftleft_path(self.standby_coordinate)
        self.shiftright_path = gen_shiftright_path(self.standby_coordinate)

        self.climb_path = gen_climb_path(self.standby_coordinate)

        self.rotatex_path = gen_rotatex_path(self.standby_coordinate)
        self.rotatey_path = gen_rotatey_path(self.standby_coordinate)
        self.rotatez_path = gen_rotatez_path(self.standby_coordinate)
        self.twist_path = gen_twist_path(self.standby_coordinate)

        self.current_motion = None

        self.standby()
        # self.laydown()
        time.sleep(1)

        # self.leg_0.set_angle(1, 30)

        # for mm in range(0, 10):
        # self.move(self.forward_path)
        # for mm in range(0, 10):
        #     self.move(self.backward_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.fastforward_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.fastbackward_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.leftturn_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.rightturn_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.shiftleft_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.shiftright_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.climb_path, 0.005)

        # for mm in range(0, 10):
        #     self.move(self.rotatex_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.rotatey_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.rotatez_path, 0.005)
        # for mm in range(0, 10):
        #     self.move(self.twist_path, 0.005)

        # time.sleep(1)
        # self.standby()

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

    def calculate_laydown_coordinate(self, standby_coordinate):
        laydown_coordinate = np.zeros_like(standby_coordinate)
        laydown_coordinate[:, 0:2] = standby_coordinate[:, 0:2]
        return laydown_coordinate

    def move(self, path):
        for p_idx in range(0, np.shape(path)[0]):
            dest = path[p_idx, :, :]
            angles = self.inverse_kinematics(dest)

            self.leg_0.move_junctions(angles[0, :])
            self.leg_5.move_junctions(angles[5, :])

            self.leg_1.move_junctions(angles[1, :])
            self.leg_4.move_junctions(angles[4, :])

            self.leg_2.move_junctions(angles[2, :])
            self.leg_3.move_junctions(angles[3, :])

            time.sleep(self.interval)

    def move_routine(self, path):
        for p_idx in range(0, np.shape(path)[0]):
            dest = path[p_idx, :, :]
            angles = self.inverse_kinematics(dest)

            self.leg_0.move_junctions(angles[0, :])
            self.leg_5.move_junctions(angles[5, :])

            self.leg_1.move_junctions(angles[1, :])
            self.leg_4.move_junctions(angles[4, :])

            self.leg_2.move_junctions(angles[2, :])
            self.leg_3.move_junctions(angles[3, :])

            try:
                data = self.cmd_queue.get(block=False)
                print('interrput')
                print(data)
            except Empty:
                time.sleep(self.interval)
                pass
            else:
                if data == 'standby':
                    self.current_motion = None
                    self.standby()
                elif data == 'forward':
                    self.current_motion = self.forward_path
                elif data == 'backward':
                    self.current_motion = self.backward_path
                elif data == 'fastforward':
                    self.current_motion = self.fastforward_path
                elif data == 'fastbackward':
                    self.current_motion = self.fastbackward_path
                elif data == 'leftturn':
                    self.current_motion = self.leftturn_path
                elif data == 'rightturn':
                    self.current_motion = self.rightturn_path
                elif data == 'shiftleft':
                    self.current_motion = self.shiftleft_path
                elif data == 'shiftright':
                    self.current_motion = self.shiftright_path
                elif data == 'climb':
                    self.current_motion = self.climb_path
                elif data == 'rotatex':
                    self.current_motion = self.rotatex_path
                elif data == 'rotatey':
                    self.current_motion = self.rotatey_path
                elif data == 'rotatez':
                    self.current_motion = self.rotatez_path
                elif data == 'twist':
                    self.current_motion = self.twist_path
                else:
                    self.current_motion = None
                self.cmd_queue.task_done()
                break

    def standby(self):
        dest = self.standby_coordinate
        angles = self.inverse_kinematics(dest)

        self.leg_0.move_junctions(angles[0, :])
        self.leg_5.move_junctions(angles[5, :])

        self.leg_1.move_junctions(angles[1, :])
        self.leg_4.move_junctions(angles[4, :])

        self.leg_2.move_junctions(angles[2, :])
        self.leg_3.move_junctions(angles[3, :])

    def laydown(self):
        dest = self.laydown_coordinate
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

    def run(self):
        while True:
            if self.current_motion is None:
                try:
                    data = self.cmd_queue.get(block=False)
                    print(data)
                except Empty:
                    time.sleep(self.interval)
                    pass
                else:
                    if data == 'standby':
                        self.current_motion = None
                        self.standby()
                    elif data == 'forward':
                        self.current_motion = self.forward_path
                    elif data == 'backward':
                        self.current_motion = self.backward_path
                    elif data == 'fastforward':
                        self.current_motion = self.fastforward_path
                    elif data == 'fastbackward':
                        self.current_motion = self.fastbackward_path
                    elif data == 'leftturn':
                        self.current_motion = self.leftturn_path
                    elif data == 'rightturn':
                        self.current_motion = self.rightturn_path
                    elif data == 'shiftleft':
                        self.current_motion = self.shiftleft_path
                    elif data == 'shiftright':
                        self.current_motion = self.shiftright_path
                    elif data == 'climb':
                        self.current_motion = self.climb_path
                    elif data == 'rotatex':
                        self.current_motion = self.rotatex_path
                    elif data == 'rotatey':
                        self.current_motion = self.rotatey_path
                    elif data == 'rotatez':
                        self.current_motion = self.rotatez_path
                    elif data == 'twist':
                        self.current_motion = self.twist_path
                    else:
                        self.current_motion = None
                    self.cmd_queue.task_done()

            if self.current_motion is not None:
                self.move_routine(self.current_motion)


def main():
    q = Queue()
    tcp_server = TCPServer(q)
    tcp_server.start()

    bt_server = BluetoothServer(q)
    bt_server.start()

    hexapod = Hexapod(q)
    hexapod.start()


if __name__ == '__main__':
    main()
