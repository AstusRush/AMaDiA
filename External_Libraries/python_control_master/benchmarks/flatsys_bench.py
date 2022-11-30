# flatsys_bench.py - benchmarks for flat systems package
# RMM, 2 Mar 2021
#
# This benchmark tests the timing for the flat system module
# (control.flatsys) and is intended to be used for helping tune the
# performance of the functions used for optimization-based control.

import numpy as np
import math
import control as ct
import control.flatsys as flat
import control.optimal as opt

#
# System setup: vehicle steering (bicycle model)
#

# Vehicle steering dynamics
def vehicle_update(t, x, u, params):
    # Get the parameters for the model
    l = params.get('wheelbase', 3.)         # vehicle wheelbase
    phimax = params.get('maxsteer', 0.5)    # max steering angle (rad)

    # Saturate the steering input (use min/max instead of clip for speed)
    phi = max(-phimax, min(u[1], phimax))

    # Return the derivative of the state
    return np.array([
        math.cos(x[2]) * u[0],            # xdot = cos(theta) v
        math.sin(x[2]) * u[0],            # ydot = sin(theta) v
        (u[0] / l) * math.tan(phi)        # thdot = v/l tan(phi)
    ])

def vehicle_output(t, x, u, params):
    return x                            # return x, y, theta (full state)

# Flatness structure
def vehicle_forward(x, u, params={}):
    b = params.get('wheelbase', 3.)             # get parameter values
    zflag = [np.zeros(3), np.zeros(3)]          # list for flag arrays
    zflag[0][0] = x[0]                          # flat outputs
    zflag[1][0] = x[1]
    zflag[0][1] = u[0] * np.cos(x[2])           # first derivatives
    zflag[1][1] = u[0] * np.sin(x[2])
    thdot = (u[0]/b) * np.tan(u[1])             # dtheta/dt
    zflag[0][2] = -u[0] * thdot * np.sin(x[2])  # second derivatives
    zflag[1][2] =  u[0] * thdot * np.cos(x[2])
    return zflag

def vehicle_reverse(zflag, params={}):
    b = params.get('wheelbase', 3.)             # get parameter values
    x = np.zeros(3); u = np.zeros(2)            # vectors to store x, u
    x[0] = zflag[0][0]                          # x position
    x[1] = zflag[1][0]                          # y position
    x[2] = np.arctan2(zflag[1][1], zflag[0][1]) # angle
    u[0] = zflag[0][1] * np.cos(x[2]) + zflag[1][1] * np.sin(x[2])
    thdot_v = zflag[1][2] * np.cos(x[2]) - zflag[0][2] * np.sin(x[2])
    u[1] = np.arctan2(thdot_v, u[0]**2 / b)
    return x, u

vehicle = flat.FlatSystem(
    vehicle_forward, vehicle_reverse, vehicle_update,
    vehicle_output, inputs=('v', 'delta'), outputs=('x', 'y', 'theta'),
    states=('x', 'y', 'theta'))

# Initial and final conditions
x0 = [0., -2., 0.]; u0 = [10., 0.]
xf = [100., 2., 0.]; uf = [10., 0.]
Tf = 10

# Define the time points where the cost/constraints will be evaluated
timepts = np.linspace(0, Tf, 10, endpoint=True)

#
# Benchmark test parameters
#

basis_params = (['poly', 'bezier', 'bspline'], [8, 10, 12])
basis_param_names = ["basis", "size"]

def get_basis(name, size):
    if name == 'poly':
        basis = flat.PolyFamily(size, T=Tf)
    elif name == 'bezier':
        basis = flat.BezierFamily(size, T=Tf)
    elif name == 'bspline':
        basis = flat.BSplineFamily([0, Tf/2, Tf], size)
    return basis

#
# Benchmarks
#

def time_point_to_point(basis_name, basis_size):
    basis = get_basis(basis_name, basis_size)

    # Find trajectory between initial and final conditions
    traj = flat.point_to_point(vehicle, Tf, x0, u0, xf, uf, basis=basis)

    # Verify that the trajectory computation is correct
    x, u = traj.eval([0, Tf])
    np.testing.assert_array_almost_equal(x0, x[:, 0])
    np.testing.assert_array_almost_equal(u0, u[:, 0])
    np.testing.assert_array_almost_equal(xf, x[:, -1])
    np.testing.assert_array_almost_equal(uf, u[:, -1])

time_point_to_point.params = basis_params
time_point_to_point.param_names = basis_param_names


def time_point_to_point_with_cost(basis_name, basis_size):
    basis = get_basis(basis_name, basis_size)

    # Define cost and constraints
    traj_cost = opt.quadratic_cost(
        vehicle, None, np.diag([0.1, 1]), u0=uf)
    constraints = [
        opt.input_range_constraint(vehicle, [8, -0.1], [12, 0.1]) ]

    traj = flat.point_to_point(
        vehicle, timepts, x0, u0, xf, uf,
        cost=traj_cost, constraints=constraints, basis=basis,
    )

    # Verify that the trajectory computation is correct
    x, u = traj.eval([0, Tf])
    np.testing.assert_array_almost_equal(x0, x[:, 0])
    np.testing.assert_array_almost_equal(u0, u[:, 0])
    np.testing.assert_array_almost_equal(xf, x[:, -1])
    np.testing.assert_array_almost_equal(uf, u[:, -1])

time_point_to_point_with_cost.params = basis_params
time_point_to_point_with_cost.param_names = basis_param_names


def time_solve_flat_ocp_terminal_cost(method, basis_name, basis_size):
    basis = get_basis(basis_name, basis_size)

    # Define cost and constraints
    traj_cost = opt.quadratic_cost(
        vehicle, None, np.diag([0.1, 1]), u0=uf)
    term_cost = opt.quadratic_cost(
        vehicle, np.diag([1e3, 1e3, 1e3]), None, x0=xf)
    constraints = [
        opt.input_range_constraint(vehicle, [8, -0.1], [12, 0.1]) ]

    # Initial guess = straight line
    initial_guess = np.array(
        [x0[i] + (xf[i] - x0[i]) * timepts/Tf for i in (0, 1)])

    traj = flat.solve_flat_ocp(
        vehicle, timepts, x0, u0, basis=basis, initial_guess=initial_guess,
        trajectory_cost=traj_cost, constraints=constraints,
        terminal_cost=term_cost, minimize_method=method,
    )

    # Verify that the trajectory computation is correct
    x, u = traj.eval([0, Tf])
    np.testing.assert_array_almost_equal(x0, x[:, 0])
    np.testing.assert_array_almost_equal(xf, x[:, -1], decimal=2)

time_solve_flat_ocp_terminal_cost.params = tuple(
    [['slsqp', 'trust-constr']] + list(basis_params))
time_solve_flat_ocp_terminal_cost.param_names = tuple(
    ['method'] + basis_param_names)
