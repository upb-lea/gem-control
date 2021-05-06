from gym_electric_motor.physical_systems import converters as cv
import numpy as np

from gem_controllers import stages
from gem_controllers.tuner import parameter_reader as reader


def tune_controller(controller, env, action_type, motor, control_task, a=4, current_safety_margin=0.2):
    if motor in reader.dc_motors:
        return tune_dc_controller(controller, env, motor, action_type, control_task, a, current_safety_margin)
    raise Exception(f'No Tuner available for motor type: {motor}')


def tune_dc_controller(controller, env, dc_motor, action_type, control_task, a=4, current_safety_margin=0.2):
    i = 0
    controller.stages[i].tune(env, dc_motor, action_type, control_task)
    i += 1
    if control_task == 'SC':
        controller.stages[i].tune(env, dc_motor, action_type, control_task, a=a)
        i += 1
    if control_task in ['SC', 'TC']:
        controller.stages[i].tune(env, dc_motor, action_type, control_task, current_safety_margin)
        i += 1
    controller.stages[i].tune(env, dc_motor, action_type, control_task, a=a)
    i += 1
    if action_type == 'Cont':
        controller.stages[i].tune(env, dc_motor, action_type, control_task)
        i += 1
    controller.stages[i].tune(env, dc_motor, action_type, control_task)
    return controller
