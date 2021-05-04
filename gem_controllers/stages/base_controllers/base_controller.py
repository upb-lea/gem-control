from enum import Enum

from ..stage import Stage


class EControlTask(Enum):
    CC = 0
    CurrentControl = 0
    TC = 1
    TorqueControl = 1
    SC = 2
    SpeedControl = 2


class BaseController(Stage):

    def __init__(self, control_task):
        self._control_task = control_task

    def __call__(self, stage, reference):
        raise NotImplementedError

    def tune(self, env, motor_type, action_type, control_task, a=5):
        pass
