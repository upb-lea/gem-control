import numpy as np

import gym_electric_motor as gem
import gem_controllers as gc


class TorqueController(gc.GemController):

    @property
    def torque_to_current_stage(self) -> gc.stages.OperationPointSelection:
        return self._operation_point_selection

    @torque_to_current_stage.setter
    def torque_to_current_stage(self, value: gc.stages.OperationPointSelection):
        self._operation_point_selection = value

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
    def clipping_stage(self) -> gc.stages.clipping_stages.ClippingStage:
        return self._clipping_stage

    @clipping_stage.setter
    def clipping_stage(self, value: gc.stages.clipping_stages.ClippingStage):
        self._clipping_stage = value

    @property
    def t_n(self):
        return self._current_controller.t_n

    @property
    def references(self):
        refs = self._current_controller.references
        refs.update(dict(zip(self._referenced_currents, self._current_reference)))
        return refs

    @property
    def referenced_states(self):
        return np.append(self._current_controller.referenced_states, self._referenced_currents)

    def __init__(
            self,
            env: (gem.core.ElectricMotorEnvironment, None) = None,
            env_id: (str, None) = None,
            current_controller: (gc.CurrentController, None) = None,
            torque_to_current_stage: (gc.stages.OperationPointSelection, None) = None,
            clipping_stage: (gc.stages.clipping_stages.ClippingStage, None) = None
    ):
        super().__init__()

        self._operation_point_selection = torque_to_current_stage
        if env_id is not None and torque_to_current_stage is None:
            self._operation_point_selection = gc.stages.torque_to_current_function[gc.utils.get_motor_type(env_id)]()
        self._current_controller = current_controller
        if env_id is not None and current_controller is None:
            self._current_controller = gc.PICurrentController(env, env_id)
        if env_id is not None and clipping_stage is None:
            if gc.utils.get_motor_type(env_id) in gc.parameter_reader.dc_motors:
                self._clipping_stage = gc.stages.clipping_stages.AbsoluteClippingStage('TC')
            elif gc.utils.get_motor_type(env_id) == 'EESM':
                self._clipping_stage = gc.stages.clipping_stages.CombinedClippingStage('TC')
            else:  # motor in ac_motors
                self._clipping_stage = gc.stages.clipping_stages.SquaredClippingStage('TC')
        self._current_reference = np.array([])
        self._referenced_currents = np.array([])

    def tune(self, env, env_id, current_safety_margin=0.2, tune_current_controller=True, **kwargs):
        if tune_current_controller:
            self._current_controller.tune(env, env_id, **kwargs)
        self._clipping_stage.tune(env, env_id, margin=current_safety_margin)
        self._operation_point_selection.tune(env, env_id, current_safety_margin)
        self._referenced_currents = gc.parameter_reader.currents[gc.utils.get_motor_type(env_id)]

    def torque_control(self, state, reference):
        self._current_reference = self._operation_point_selection(state, reference)
        return self._current_reference

    def control(self, state, reference):
        self._current_reference = self.torque_control(state, reference)
        self._current_reference = self._clipping_stage(state, self._current_reference)
        reference = self._current_controller.current_control(state, self._current_reference)
        return reference

    def reset(self):
        self._current_controller.reset()
        self._operation_point_selection.reset()
        self._clipping_stage.reset()
