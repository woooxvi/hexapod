# -*- coding: utf-8 -*-

class Leg:
    def __init__(self,
                 id,
                 junction_servos,
                 correction=[0, 0, 0],
                 constraint=[[45, 135], [45, 165], [30, 150]]):
        self.id = id
        self.junction_servos = junction_servos
        self.correction = correction
        self.constraint = constraint

    def set_angle(self, junction, angle):
        set_angle = min(
            angle+self.correction[junction], self.constraint[junction][1])
        set_angle = max(set_angle, self.constraint[junction][0])
        self.junction_servos[junction].angle = set_angle

    def move_junctions(self, angles):
        self.set_angle(0, angles[0])
        self.set_angle(1, angles[1])
        self.set_angle(2, angles[2])

    def reset(self):
        self.set_angle(0, 90)
        self.set_angle(1, 90)
        self.set_angle(2, 90)
