import numpy as np

import gem_controllers as gc


class SpeedController(gc.GemController):

    @property
    def output_stage(self):
        return self._output_stage

    @output_stage.setter
    def output_stage(self, value):
        assert isinstance(value, (gc.stages.ContOutputStage, gc.stages.DiscOutputStage))
        self._output_stage = value

    @property
    def input_stage(self):
        return self._input_stage

    @input_stage.setter
    def input_stage(self, value):
        assert isinstance(value, gc.stages.InputStage)
        self._input_stage = value

    @property
    def speed_control_stage(self):
        return self._speed_control_stage

    @speed_control_stage.setter
    def speed_control_stage(self, value):
        assert isinstance(value, gc.stages.BaseController)
        self._speed_control_stage = value

    @property
    def torque_controller(self):
        return self._torque_controller

    @torque_controller.setter
    def torque_controller(self, value):
        assert isinstance(value, gc.TorqueController)
        self._torque_controller = value

    @property
    def torque_reference(self):
        return self._torque_reference

    def __init__(self):
        super().__init__()
        self._input_stage = None
        self._output_stage = None
        self._speed_control_stage = None
        self._torque_controller = None
        self._torque_reference = np.array([])

    def design(self, action_type, motor_type, base_current_controller='PI', decoupling=True):
        self._input_stage = gc.stages.InputStage()
        if action_type == 'Finite':
            self._output_stage = gc.stages.DiscOutputStage()
        else:
            self._output_stage = gc.stages.ContOutputStage()
        self._speed_control_stage = gc.stages.base_controllers.PIController('SC')
        self._torque_controller = gc.TorqueController()
        self._torque_controller.design(action_type, motor_type, base_current_controller, decoupling)

    def tune(self, env, motor_type, action_type, control_task, a=4):
        self._torque_controller.tune(env, motor_type, action_type, control_task='TC', a=a)
        current_base_controller = self._torque_controller.current_controller.current_base_controller
        if hasattr(current_base_controller, 'p_gain') and hasattr(current_base_controller, 'i_gain'):
            t_n = max(current_base_controller.p_gain / current_base_controller.i_gain)
        else:
            t_n = None
        self._speed_control_stage.tune(env, motor_type, action_type, control_task, a, t_n)
        self._input_stage.tune(env, motor_type, action_type, control_task)
        self._output_stage.tune(env, motor_type, action_type, control_task)

    def speed_control(self, state, reference):
        self._torque_reference = self._speed_control_stage(state, reference)
        return self._torque_reference

    def control(self, state, reference):
        reference = self._input_stage(state, reference)
        reference = self.speed_control(state, reference)
        reference = self._torque_controller.torque_control(state, reference)
        reference = self._torque_controller.current_controller.current_control(state, reference)
        return self._output_stage(state, reference)

    def reset(self):
        self._torque_controller.reset()
        self._input_stage.reset()
        self._output_stage.reset()
        self._speed_control_stage.reset()
