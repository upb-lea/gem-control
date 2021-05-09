from ..stage import Stage
from.e_base_controller_task import EBaseControllerTask


class BaseController(Stage):
    """The base controller is the base class for all dynamic control stages like the P-I-D Controllers or the
    Three-Point controller.

    In contrast to other stages, the base controllers can be used for multiple tasks e.g. a speed control with a torque
     as output or a current control with voltages as output.

    """

    def __init__(self, control_task):
        self._control_task = EBaseControllerTask.get_control_task(control_task)

    def __call__(self, stage, reference):
        raise NotImplementedError

    def tune(self, env, motor_type, action_type, control_task, **base_controller_kwargs):
        pass
