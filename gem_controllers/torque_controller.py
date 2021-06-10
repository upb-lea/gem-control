import numpy as np

import gym_electric_motor as gem
import gem_controllers as gc


class TorqueController(gc.GemController):

    @property
    def torque_to_current_stage(self) -> gc.stages.OperationPointSelection:
        return self._torque_to_current_stage

    @torque_to_current_stage.setter
    def torque_to_current_stage(self, value: gc.stages.OperationPointSelection):
        self._torque_to_current_stage = value

    @property
    def current_controller(self) -> gc.CurrentController:
        return self._current_controller

    @current_controller.setter
    def current_controller(self, value: gc.CurrentController):
        self._current_controller = value

    @property
    def current_reference(self) -> np.ndarray:
        return self._current_reference

    @property
    def t_n(self):
        return self._current_controller.t_n

    def __init__(
            self,
            env: (gem.core.ElectricMotorEnvironment, None) = None,
            env_id: (str, None) = None,
            current_controller: (gc.CurrentController, None) = None,
            torque_to_current_stage: (gc.stages.OperationPointSelection, None) = None
    ):
        super().__init__()

        self._torque_to_current_stage = torque_to_current_stage
        if env_id is not None and torque_to_current_stage is None:
            self._torque_to_current_stage = gc.stages.torque_to_current_function[gc.utils.get_motor_type(env_id)]()
        self._current_controller = current_controller
        if env_id is not None and current_controller is None:
            self._current_controller = gc.PICurrentController(env, env_id)
        self._current_reference = np.array([])

    def tune(self, env, env_id, current_safety_margin=0.2, tune_current_controller=True, **kwargs):
        if tune_current_controller:
            self._current_controller.tune(env, env_id, **kwargs)
        self._torque_to_current_stage.tune(env, env_id, current_safety_margin)

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
