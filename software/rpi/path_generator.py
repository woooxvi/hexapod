from lib import semicircle_generator, semicircle2_generator
from lib import path_rotate_z
import numpy as np
from collections import deque


def gen_forward_path():
    # assert (g_steps % 4) == 0
    g_steps = 20
    g_radius = 25
    halfsteps = int(g_steps/2)

    path = np.zeros((g_steps, 6, 3))

    path[:, 0, :] = semicircle_generator(g_radius, g_steps)

    mir_path = np.roll(path[:, 0, :], halfsteps, axis=0)
    path[:, 2, :] = path[:, 0, :]
    path[:, 4, :] = path[:, 0, :]
    path[:, 1, :] = mir_path
    path[:, 3, :] = mir_path
    path[:, 5, :] = mir_path

    return path


def gen_backward_path():
    # assert (g_steps % 4) == 0
    g_steps = 20
    g_radius = 25
    halfsteps = int(g_steps/2)

    path = np.zeros((g_steps, 6, 3))

    path[:, 0, :] = semicircle_generator(g_radius, g_steps, reverse=True)

    mir_path = np.roll(path[:, 0, :], halfsteps, axis=0)
    path[:, 2, :] = path[:, 0, :]
    path[:, 4, :] = path[:, 0, :]
    path[:, 1, :] = mir_path
    path[:, 3, :] = mir_path
    path[:, 5, :] = mir_path

    return path


def gen_fastforward_path():
    g_steps = 20
    y_radius = 50
    z_radius = 30
    x_radius = 10

    halfsteps = int(g_steps/2)

    path = np.zeros((g_steps, 6, 3))
    path[:, 0, :] = semicircle2_generator(
        g_steps, y_radius, z_radius, x_radius)
    path[:, 4, :] = semicircle2_generator(
        g_steps, y_radius, z_radius, -x_radius)

    mir_rpath = np.roll(path[:, 0, :], halfsteps, axis=0)
    path[:, 1, :] = mir_rpath
    path[:, 2, :] = path[:, 0, :]

    mir_lpath = np.roll(path[:, 4, :], halfsteps, axis=0)
    path[:, 3, :] = mir_lpath
    path[:, 5, :] = mir_lpath

    return path


def gen_fastbackward_path():
    g_steps = 20
    y_radius = 50
    z_radius = 30
    x_radius = 10

    halfsteps = int(g_steps/2)

    path = np.zeros((g_steps, 6, 3))
    path[:, 0, :] = semicircle2_generator(
        g_steps, y_radius, z_radius, x_radius, reverse=True)
    path[:, 4, :] = semicircle2_generator(
        g_steps, y_radius, z_radius, -x_radius, reverse=True)

    mir_rpath = np.roll(path[:, 0, :], halfsteps, axis=0)
    path[:, 1, :] = mir_rpath
    path[:, 2, :] = path[:, 0, :]

    mir_lpath = np.roll(path[:, 4, :], halfsteps, axis=0)
    path[:, 3, :] = mir_lpath
    path[:, 5, :] = mir_lpath

    return path


def gen_leftturn_path():
    g_steps = 20
    g_radius = 25
    assert (g_steps % 4) == 0
    halfsteps = int(g_steps/2)

    path = semicircle_generator(g_radius, g_steps)
    mir_path = np.roll(path, halfsteps, axis=0)

    leftturn = np.zeros((g_steps, 6, 3))
    leftturn[:, 0, :] = np.array(path_rotate_z(path, 45))
    leftturn[:, 1, :] = np.array(path_rotate_z(mir_path, 0))
    leftturn[:, 2, :] = np.array(path_rotate_z(path, 315))
    leftturn[:, 3, :] = np.array(path_rotate_z(mir_path, 225))
    leftturn[:, 4, :] = np.array(path_rotate_z(path, 180))
    leftturn[:, 5, :] = np.array(path_rotate_z(mir_path, 135))

    return leftturn
