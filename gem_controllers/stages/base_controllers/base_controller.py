from ..stage import Stage
from.e_base_controller_task import EBaseControllerTask


class BaseController(Stage):

    def __init__(self, control_task):
        self._control_task = EBaseControllerTask.get_control_task(control_task)

    def __call__(self, stage, reference):
        raise NotImplementedError

    def tune(self, env, motor_type, action_type, control_task, **base_controller_kwargs):
        pass
