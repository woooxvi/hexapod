from lib import semicircle_generator
import numpy as np


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
