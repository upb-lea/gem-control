from gym_electric_motor.physical_systems import converters as cv
import numpy as np

from gem_controllers import stages
from gem_controllers.tuner import parameter_reader as reader

control_tasks_ = ['CC', 'TC', 'SC']
dc_actions = ['Finite', 'Cont']
ac_actions = ['Finite', 'DqCont', 'AbcCont']
dc_motors = ['PermExDc', 'ExtExDc', 'ShuntDc', 'SeriesDc']
ac_motors = ['PMSM', 'SynRM', 'DFIM', 'SCIM']
tuning_registry = dict()


def tune_controller(controller, env, action_type, motor, control_task, a=4, current_safety_margin=0.2):
    if motor in dc_motors:
        return tune_dc_controller(controller, env, motor, action_type, control_task, a, current_safety_margin)
    raise Exception(f'No Tuner available for motor type: {motor}')


def tune_dc_controller(controller, env, dc_motor, action_type, control_task, a=4, current_safety_margin=0.2):
    i = 0
    tune_input_stage(controller.stages[i], env, dc_motor, action_type, control_task)
    i += 1
    if control_task == 'SC':
        tune_dc_speed_controller(controller.stages[i], env, dc_motor, action_type, control_task, a)
        i += 1
    if control_task in ['SC', 'TC']:
        tune_torque_to_current(controller.stages[i], env, dc_motor, action_type, control_task, current_safety_margin)
        i += 1
    tune_dc_current_controller(controller.stages[i], env, dc_motor, action_type, control_task, a)
    i += 1
    if action_type == 'Cont':
        tune_feedforward(controller.stages[i], env, dc_motor, action_type, control_task)
        i += 1
        tune_cont_output_stage(controller.stages[i], env, dc_motor, action_type, control_task)
    else:
        raise NotImplementedError
    return controller


def tune_dc_speed_controller(control_stage, env, motor_type, action_type, control_task, a):
    if type(control_stage) is stages.PIController:
        tune_dc_speed_pi(control_stage, env,  motor_type, action_type, control_task, a)
    elif type(control_stage) is stages.ThreePointController:
        raise NotImplementedError
    elif type(control_stage) is stages.PIDController:
        raise NotImplementedError
    elif type(control_stage) is stages.PController:
        raise NotImplementedError
    else:
        raise Exception(f'No tuner for the speed controller of class {type(control_stage)} available.')


def tune_dc_current_controller(control_stage, env, motor_type, action_type, control_task, a):
    if type(control_stage) is stages.PIController:
        tune_dc_current_pi(control_stage, env,  motor_type, action_type, control_task, a)
    elif type(control_stage) is stages.ThreePointController:
        raise NotImplementedError
    elif type(control_stage) is stages.PIDController:
        raise NotImplementedError
    elif type(control_stage) is stages.PController:
        raise NotImplementedError
    else:
        raise Exception(f'No tuner for the speed controller of class {type(control_stage)} available.')


def tune_input_stage(input_stage, env, motor_type, action_type, control_task):
    reference_indices = [env.state_names.index(reference) for reference in env.reference_names]
    reference_limits = env.limits[reference_indices]
    state_limits = env.limits
    input_stage.reference_limits = reference_limits
    input_stage.state_limits = state_limits


def tune_feedforward(feedforward_stage, env, motor_type, action_type, control_task):
    omega_idx = env.state_names.index('omega')
    current_indices = [env.state_names.index(current) for current in reader.currents[motor_type]]
    feedforward_stage.omega_idx = omega_idx
    feedforward_stage.current_indices = current_indices
    feedforward_stage.inductance = -reader.l_reader[motor_type](env)
    feedforward_stage.psi = reader.psi_reader[motor_type](env)


def tune_torque_to_current(torque_to_current_stage, env, motor_type, action_type, control_task, current_safety_margin):
    ttc = reader.torque_to_current_function_factory[motor_type](env)
    currents = reader.currents[motor_type]
    current_indices = [env.state_names.index(current) for current in currents]
    state_space = env.observation_space[0]
    upper_limit = env.limits[current_indices] * state_space.high[current_indices] * (1-current_safety_margin)
    lower_limit = env.limits[current_indices] * state_space.low[current_indices] * (1-current_safety_margin)
    torque_to_current_stage.action_range = (lower_limit, upper_limit)
    torque_to_current_stage.conversion_function = ttc


def tune_cont_output_stage(cont_output_stage, env, motor_type, action_type, control_task):
    voltages = reader.voltages[motor_type]
    voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
    cont_output_stage.voltage_limit = env.limits[voltage_indices]


def tune_disc_output_stage(disc_output_stage, env, motor_type, action_type, control_task):
    voltages = reader.voltages[motor_type]
    converter = env.physical_system.converter

    high_idle_low = {
        cv.FiniteOneQuadrantConverter: [1, 0, 0],
        cv.FiniteTwoQuadrantConverter: [1, 0, 2],
        cv.FiniteFourQuadrantConverter: [1, 0, 2],
        cv.FiniteB6BridgeConverter: [[1, 1, 1], [0, 0, 0], [2, 2, 2]]
    }

    if type(converter) is cv.FiniteMultiConverter:
        subconverters = converter.subconverters
    raise NotImplementedError


def tune_pi_speed_controller(pi_controller, env, motor_type, action_type, control_task, a=4):
    if motor_type in dc_motors:
        tune_dc_speed_pi(pi_controller, env, motor_type, action_type, control_task, a)
    else:
        tune_foc_speed_pi(pi_controller, env, motor_type, action_type, control_task, a)


def tune_dc_speed_pi(pi_controller, env, motor_type, _action_type, __control_task, a=4):
    j_total = env.physical_system.mechanical_load.j_total
    tau = env.physical_system.tau
    r_a = reader.r_reader[motor_type](env)[0]
    l_a = reader.l_reader[motor_type](env)[0]
    torque_index = env.state_names.index('torque')
    speed_index = env.state_names.index('omega')
    torque_limit = env.limits[torque_index]
    speed_limit = env.limits[speed_index]
    torque_range = (
        np.array([env.observation_space[0].low[torque_index] * torque_limit]),
        np.array([env.observation_space[0].high[torque_index] * torque_limit])
    )
    p_gain = j_total / (a * (l_a / r_a)) * speed_limit / torque_limit
    i_gain = p_gain / (a ** 2 * (l_a / r_a))
    pi_controller.p_gain = np.array([p_gain])
    pi_controller.i_gain = np.array([i_gain])
    pi_controller.tau = tau
    pi_controller.state_indices = [speed_index]
    pi_controller.action_range = torque_range


def tune_foc_speed_pi(pi_controller, env, motor_type, _action_type, _control_task, a=4):
    raise NotImplementedError


def tune_pi_current_controller(pi_controller, env, motor_type, action_type, control_task, a=4):
    if motor_type in dc_motors:
        tune_dc_current_pi(pi_controller, env, motor_type, action_type, control_task, a)
    else:
        tune_foc_current_pi(pi_controller, env, motor_type, action_type, control_task, a)


def tune_foc_current_pi(pi_controller, env, motor_type, action_type, control_task, a):
    raise NotImplementedError


def tune_dc_current_pi(pi_controller, env, motor_type, _, __, a):
    l_ = reader.l_reader[motor_type](env)
    tau = env.physical_system.tau
    currents = reader.currents[motor_type]
    voltages = reader.voltages[motor_type]
    voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
    current_indices = [env.state_names.index(current) for current in currents]
    voltage_limits = env.limits[voltage_indices]
    current_limits = env.limits[current_indices]
    p_gain = l_ / (tau * a) * current_limits / voltage_limits
    i_gain = p_gain / (tau * a ** 2)

    action_range = (
        env.observation_space[0].low[voltage_indices] * voltage_limits,
        env.observation_space[0].high[voltage_indices] * voltage_limits,
    )

    pi_controller.p_gain = p_gain
    pi_controller.i_gain = i_gain

    pi_controller.action_range = action_range
    pi_controller.tau = tau
    pi_controller.state_indices = current_indices
