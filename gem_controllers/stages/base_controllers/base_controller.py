from enum import Enum

from ..stage import Stage


class EControlTask:
    CC = 'CC'
    CurrentControl = 'CC'
    TC = 'TC'
    TorqueControl = 'TC'
    SC = 'SC'
    SpeedControl = 'SC'


class BaseController(Stage):

    def __init__(self, control_task):
        self._control_task = control_task

    def __call__(self, stage, reference):
        raise NotImplementedError

    def tune(self, env, motor_type, action_type, control_task, **base_controller_kwargs):
        pass
