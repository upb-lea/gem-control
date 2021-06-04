import numpy as np

import gem_controllers as gc


class TorqueController(gc.GemController):

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
        assert isinstance(value, gc.PICurrentController)
        self._current_controller = value

    @property
    def current_reference(self):
        return self._current_reference

    def __init__(self):
        super().__init__()
        self._torque_to_current_stage = None
        self._current_controller = None
        self._current_reference = np.array([])

    def design(self, env, env_id, base_current_controller='PI', decoupling=True):
        self._torque_to_current_stage = gc.stages.torque_to_current_function[gc.utils.get_motor_type(env_id)]()
        self._current_controller = gc.PICurrentController()
        self._current_controller.design(env, env_id, base_current_controller, decoupling)

    def tune(self, env, env_id, current_safety_margin=0.2, **kwargs):
        self._torque_to_current_stage.tune(env, env_id, current_safety_margin)
        self._current_controller.tune(env, env_id, **kwargs)

    def torque_control(self, state, reference):
        self._current_reference = self._torque_to_current_stage(state, reference)
        return self._current_reference

    def control(self, state, reference):
        self._current_reference = self.torque_control(state, reference)
        reference = self._current_controller.current_control(state, self._current_reference)
        return reference

    def reset(self):
        self._current_controller.reset()
        self._torque_to_current_stage.reset()
