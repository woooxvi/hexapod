from collections import deque
import math
import numpy as np


def semicircle_generator(radius, steps, reverse=False):
    assert (steps % 4) == 0
    halfsteps = int(steps/2)

    step_angle = np.pi / halfsteps

    result = np.zeros((steps, 3))
    halfsteps_array = np.arange(halfsteps)

    # first half, move backward (only y change)
    result[:halfsteps, 1] = radius - halfsteps_array*radius*2/(halfsteps)

    # second half, move forward in semicircle shape (y, z change)
    angle = np.pi - step_angle*halfsteps_array
    y = radius * np.cos(angle)
    z = radius * np.sin(angle)
    result[halfsteps:, 1] = y
    result[halfsteps:, 2] = z

    result = np.roll(result, int(steps/4), axis=0)

    if reverse:
        result = np.flip(result, axis=0)
        result = np.roll(result, 1, axis=0)

    return result


def semicircle2_generator(steps, y_radius, z_radius, x_radius, reverse=False):
    assert (steps % 4) == 0
    halfsteps = int(steps/2)

    step_angle = np.pi / halfsteps

    result = np.zeros((steps, 3))
    halfsteps_array = np.arange(halfsteps)

    # first half, move backward (only y change)
    result[:halfsteps, 1] = y_radius - halfsteps_array*y_radius*2/(halfsteps)

    # second half, move forward in semicircle shape (y, z change)
    angle = np.pi - step_angle*halfsteps_array
    y = y_radius * np.cos(angle)
    z = z_radius * np.sin(angle)
    x = x_radius * np.sin(angle)
    result[halfsteps:, 0] = x
    result[halfsteps:, 1] = y
    result[halfsteps:, 2] = z

    result = np.roll(result, int(steps/4), axis=0)

    if reverse:
        result = np.flip(result, axis=0)
        result = np.roll(result, 1, axis=0)

    return result


def get_rotate_x_matrix(angle):
    angle = angle * np.pi / 180
    return np.matrix([
        [1, 0, 0, 0],
        [0, math.cos(angle), -math.sin(angle), 0],
        [0, math.sin(angle), math.cos(angle), 0],
        [0, 0, 0, 1],
    ])


def get_rotate_y_matrix(angle):
    angle = angle * np.pi / 180
    return np.matrix([
        [math.cos(angle), 0, math.sin(angle), 0],
        [0, 1, 0, 0],
        [-math.sin(angle), 0, math.cos(angle), 0],
        [0, 0, 0, 1],
    ])


def get_rotate_z_matrix(angle):
    angle = angle * np.pi / 180
    return np.matrix([
        [math.cos(angle), -math.sin(angle), 0, 0],
        [math.sin(angle), math.cos(angle), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ])


def matrix_mul(m, pt):
    ptx = list(pt) + [1]
    return list((m * np.matrix(ptx).T).T.flat)[:-1]


def point_rotate_x(pt, angle):
    ptx = list(pt) + [1]
    return list((get_rotate_x_matrix(angle) * np.matrix(ptx).T).T.flat)[:-1]


def point_rotate_y(pt, angle):
    ptx = list(pt) + [1]
    return list((get_rotate_y_matrix(angle) * np.matrix(ptx).T).T.flat)[:-1]


def point_rotate_z(pt, angle):
    ptx = list(pt) + [1]
    return list((get_rotate_z_matrix(angle) * np.matrix(ptx).T).T.flat)[:-1]


def path_rotate_x(path, angle):
    return [point_rotate_x(p, angle) for p in path]


def path_rotate_y(path, angle):
    return [point_rotate_y(p, angle) for p in path]


def path_rotate_z(path, angle):
    return [point_rotate_z(p, angle) for p in path]


if __name__ == '__main__':
    pt = [0, 1, 0]
    print(point_rotate_z(pt, 270))
