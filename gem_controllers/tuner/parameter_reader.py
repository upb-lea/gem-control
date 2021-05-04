from gym_electric_motor.physical_systems import converters as cv

import numpy as np

dc_motors = ['SeriesDc', 'ShuntDc', 'PermExDc', 'ExtExDc']
synchronous_motors = ['PMSM', 'SynRM']
induction_motors = ['DFIM', 'SCIM']
ac_motors = synchronous_motors + induction_motors

control_tasks_ = ['CC', 'TC', 'SC']
dc_actions = ['Finite', 'Cont']
ac_actions = ['Finite', 'DqCont', 'AbcCont']


psi_reader = {
    'SeriesDc': lambda env: np.array([0.0]),
    'ShuntDc': lambda env: np.array([0.0]),
    'PermExDc': lambda env: np.array([env.physical_system.electrical_motor.motor_parameter['psi_e']]),
    'ExtExDc': lambda env: np.array([0.0, 0.0]),
    'PMSM': lambda env: np.array([env.physical_system.electrical_motor.motor_parameter['psi_p'], 0.0]),
    'SynRM': lambda env: np.array([0.0, 0.0]),
}

l_reader = {
    'SeriesDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_a']
        + env.physical_system.electrical_motor.motor_parameter['l_e']
    ]),
    'ShuntDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_a'],
    ]),
    'ExtExDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_a'],
        env.physical_system.electrical_motor.motor_parameter['l_e']
    ]),
    'PermExDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_a'],
    ]),
    'PMSM': lambda env: np.array([
        env.physical_system.electric_motor.motor_parameter['l_sd'],
        - env.physical_system.electric_motor.motor_parameter['l_sq']
    ]),
    'SynRM': lambda env: np.array([
        env.physical_system.electric_motor.motor_parameter['l_sd'],
        - env.physical_system.electric_motor.motor_parameter['l_sq']
    ]),
}

r_reader = {
    'SeriesDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['r_a']
        + env.physical_system.electrical_motor.motor_parameter['r_e']
    ]),
    'ShuntDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['r_a'],
    ]),
    'ExtExDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['r_a'],
        env.physical_system.electrical_motor.motor_parameter['r_e']
    ]),
    'PermExDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['r_a'],
    ]),
    'PMSM': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['r_s'],
        env.physical_system.electrical_motor.motor_parameter['r_s']
    ]),
    'SynRM': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['r_s'],
        env.physical_system.electrical_motor.motor_parameter['r_s']
    ]),
}


currents = {
    'SeriesDc': ['i'],
    'ShuntDc': ['i_a'],
    'ExtExDc': ['i_a', 'i_e'],
    'PermExDc': ['i'],
    'PMSM': ['i_sd', 'i_sq'],
    'SynRM': ['i_sd', 'i_sq']
}

voltages = {
    'SeriesDc': ['u'],
    'ShuntDc': ['u'],
    'ExtExDc': ['u_a', 'u_e'],
    'PermExDc': ['u'],
    'PMSM': ['u_a', 'u_b', 'u_c'],
    'SynRM': ['u_a', 'u_b', 'u_c'],
}

l_prime_reader = {
    'SeriesDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_e_prime']
    ]),
    'ShuntDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_e_prime']
    ]),
    'ExtExDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_e_prime']
    ]),
    'PermExDc': lambda env: np.array([0.0]),
    'PMSM': lambda env: np.array([0.0, 0.0]),
    'SynRM': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_sd']
        - env.physical_system.electrical_motor.motor_parameter['l_sq']
    ]),
}


def series_torque_to_current_factory(env):
    cross_inductance = l_prime_reader['SeriesDc'](env)

    def series_torque_to_current(state, reference):
        return np.sqrt(reference / cross_inductance)

    return series_torque_to_current


def shunt_torque_to_current_factory(env, i_e_margin=0.2):
    cross_inductance = l_prime_reader['ShuntDc'](env)
    i_e_idx = env.state_names.index('i_e')
    i_a_idx = env.state_names.index('i_a')
    i_a_limit = env.limits[i_a_idx] * (1 - i_e_margin)
    i_e_limit = env.limits[i_e_idx] * (1 - i_e_margin)

    def shunt_torque_to_current(state, reference):
        # If i_e is too high, set torque reference to 0.
        if abs(state[i_e_idx]) > i_e_limit:
            return np.zeros(1, dtype=float)
        return reference / cross_inductance / max(state[i_e_idx], 1e-3 * i_e_limit)

    return shunt_torque_to_current


def extex_torque_to_current_factory(env):
    cross_inductance = l_prime_reader['ExtExDc'](env)
    i_e_idx = env.state_names.index('i_e')
    i_a_idx = env.state_names.index('i_a')

    def i_e_policy(state, reference):
        # Try to keep i_e = abs(i_a)
        return abs(state[i_a_idx]) * 0.5

    def extex_torque_to_current(state, reference):
        i_e_ref = i_e_policy(state, reference)
        i_a_ref = reference[0] / cross_inductance[0] / max(state[i_e_idx], 1.0)
        return np.array([i_a_ref, i_e_ref])

    return extex_torque_to_current


def permex_torque_to_current_factory(env):
    psi = psi_reader['PermExDc'](env)

    def permex_torque_to_current(state, reference):
        return reference / psi

    return permex_torque_to_current


def pmsm_torque_to_current_factory(env, i_sd_policy=None):
    i_sd_idx = env.state_names.index('i_sd')
    p = env.physical_system.electric_motor.motor_parameter['p']
    psi = psi_reader['PMSM'](env)[0]
    inductances = np.sum(l_reader['PMSM'](env))

    def i_sd_policy_default(state, reference):
        return 0.0

    if i_sd_policy is None:
        i_sd_policy = i_sd_policy_default

    def pmsm_torque_to_current(state, reference):
        i_sq_ref = reference[0] / 1.5 * p * (psi + inductances * state[i_sd_idx])
        return np.array([i_sd_policy(state, reference), i_sq_ref])

    return pmsm_torque_to_current


torque_to_current_function_factory = {
    'SeriesDc': series_torque_to_current_factory,
    'ShuntDc': shunt_torque_to_current_factory,
    'PermExDc': permex_torque_to_current_factory,
    'ExtExDc': extex_torque_to_current_factory,
    'PMSM': pmsm_torque_to_current_factory,
    'SynRM': pmsm_torque_to_current_factory,
}


converter_high_idle_low_action = {
    cv.FiniteFourQuadrantConverter: (1, 0, 2),
    cv.FiniteTwoQuadrantConverter: (1, 0, 2),
    cv.FiniteOneQuadrantConverter: (1, 0, 0),
    cv.FiniteB6BridgeConverter: ((1, 0, 2),) * 3,
}
