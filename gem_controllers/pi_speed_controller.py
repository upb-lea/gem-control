import numpy as np

import gym_electric_motor as gem
import gem_controllers as gc


class PISpeedController(gc.GemController):

    @property
    def speed_control_stage(self) -> gc.stages.BaseController:
        return self._speed_control_stage

    @speed_control_stage.setter
    def speed_control_stage(self, value: gc.stages.BaseController):
        self._speed_control_stage = value

    @property
    def torque_controller(self) -> gc.TorqueController:
        return self._torque_controller

    @torque_controller.setter
    def torque_controller(self, value: gc.TorqueController):
        self._torque_controller = value

    @property
    def torque_reference(self) -> np.ndarray:
        return self._torque_reference

    @property
    def anti_windup_stage(self):
        return self._anti_windup_stage

    @property
    def clipping_stage(self):
        return self._clipping_stage

    def __init__(
            self,
            _env: (gem.core.ElectricMotorEnvironment, None) = None,
            env_id: (str, None) = None,
            torque_controller: (gc.TorqueController, None) = None,
            base_speed_controller: str = 'PI'
    ):
        super().__init__()
        self._speed_control_stage = gc.stages.base_controllers.get(base_speed_controller)('SC')
        self._torque_controller = torque_controller
        if torque_controller is None:
            self._torque_controller = gc.TorqueController()
        self._torque_reference = np.array([])
        self._anti_windup_stage = gc.stages.AntiWindup('SC')
        self._clipping_stage = gc.stages.clipping_stages.AbsoluteClippingStage('SC')

    def tune(self, env, env_id, tune_torque_controller=True, a=4, **kwargs):
        if tune_torque_controller:
            self._torque_controller.tune(env, env_id, a=a, **kwargs)
        self._anti_windup_stage.tune(env, env_id)
        self._clipping_stage.tune(env, env_id)
        t_n = min(self._torque_controller.t_n)
        self._speed_control_stage.tune(env, env_id, t_n=t_n, a=a)

    def speed_control(self, state, reference):
        torque_reference = self._speed_control_stage(state, reference)
        self._torque_reference = self._clipping_stage(state, torque_reference)
        if hasattr(self._speed_control_stage, 'integrator'):
            delta = self._anti_windup_stage.__call__(state, reference, self._clipping_stage.clipping_difference)
            self._speed_control_stage.integrator += delta
        return self._torque_reference

    def control(self, state, reference):
        reference = self.speed_control(state, reference)
        reference = self._torque_controller.control(state, reference)
        return reference

    def reset(self):
        self._torque_controller.reset()
        self._speed_control_stage.reset()
