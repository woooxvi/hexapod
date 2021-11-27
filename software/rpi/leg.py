# -*- coding: utf-8 -*-

class Leg:
    def __init__(self,
                 id,
                 junction_servos,
                 correction=[0, 0, 0],
                 constraint=[0, 180]):
        self.id = id
        self.junction_servos = junction_servos
        self.correction = correction
        self.constraint = constraint

    def set_angle(self, junction, angle):
        set_angle = min(angle+self.correction[junction], self.constraint[1])
        set_angle = max(set_angle, self.constraint[0])
        self.junction_servos[junction].angle = set_angle
