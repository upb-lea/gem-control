import numpy as np

import gem_controllers as gc


class TorqueController(gc.GemController):

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
    def torque_to_current_stage(self):
        return self._torque_to_current_stage

    @torque_to_current_stage.setter
    def torque_to_current_stage(self, value):
        assert isinstance(value, gc.stages.TorqueToCurrentSetPoint)
        self._torque_to_current_stage = value

    @property
    def current_controller(self):
        return self._current_controller

    @current_controller.setter
    def current_controller(self, value):
        assert isinstance(value, gc.CurrentController)
        self._current_controller = value

    @property
    def current_reference(self):
        return self._current_reference

    def __init__(self):
        super().__init__()
        self._input_stage = None
        self._output_stage = None
        self._torque_to_current_stage = None
        self._current_controller = None
        self._current_reference = np.array([])

    def design(self, action_type, motor_type, base_current_controller='PI', decoupling=True):
        self._input_stage = gc.stages.InputStage()
        if action_type == 'Finite':
            self._output_stage = gc.stages.DiscOutputStage()
        else:
            self._output_stage = gc.stages.ContOutputStage()
        self._torque_to_current_stage = gc.stages.torque_to_current_function[motor_type]()
        self._current_controller = gc.CurrentController()
        self._current_controller.design(action_type, motor_type, base_current_controller, decoupling)

    def tune(self, env, motor_type, action_type, control_task, a=4):
        self._torque_to_current_stage.tune(env, motor_type, action_type, control_task)
        self._current_controller.tune(env, motor_type, action_type, control_task='CC', a=a)
        self._input_stage.tune(env, motor_type, action_type, control_task)
        self._output_stage.tune(env, motor_type, action_type, control_task)

    def torque_control(self, state, reference):
        self._current_reference = self._torque_to_current_stage(state, reference)
        return self._current_reference

    def control(self, state, reference):
        reference = self._input_stage(state, reference)
        reference = self.torque_control(state, reference)
        reference = self._current_controller.current_control(state, reference)
        return self._output_stage(state, reference)

    def reset(self):
        self._current_controller.reset()
        self._input_stage.reset()
        self._output_stage.reset()
        self._torque_to_current_stage.reset()