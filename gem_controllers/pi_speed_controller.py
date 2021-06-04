import numpy as np

import gem_controllers as gc


class PISpeedController(gc.GemController):

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
        self._speed_control_stage = None
        self._torque_controller = None
        self._torque_reference = np.array([])

    def design(self, env, env_id, base_current_controller='PI', decoupling=True):
        self._speed_control_stage = gc.stages.base_controllers.PIController('SC')

        if self._torque_controller is None:
            self._torque_controller = gc.TorqueController()
            self._torque_controller.design(env, env_id, base_current_controller, decoupling)

    def tune(self, env, env_id, **kwargs):
        self._torque_controller.tune(env, env_id, **kwargs)
        current_base_controller = self._torque_controller.current_controller.current_base_controller
        if hasattr(current_base_controller, 'p_gain') and hasattr(current_base_controller, 'i_gain'):
            t_n = max(current_base_controller.p_gain / current_base_controller.i_gain)
        else:
            t_n = None
        self._speed_control_stage.tune(env, env_id, t_n=t_n)

    def speed_control(self, state, reference):
        self._torque_reference = self._speed_control_stage(state, reference)
        return self._torque_reference

    def control(self, state, reference):
        reference = self.speed_control(state, reference)
        reference = self._torque_controller.torque_control(state, reference)
        reference = self._torque_controller.current_controller.current_control(state, reference)
        return reference

    def reset(self):
        self._torque_controller.reset()
        self._speed_control_stage.reset()
