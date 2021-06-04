import numpy as np

import gem_controllers as gc


class PICurrentController(gc.CurrentController):

    @property
    def transformation_stage(self):
        return self._transformation_stage

    @property
    def current_base_controller(self) -> gc.stages.BaseController:
        return self._current_base_controller

    @current_base_controller.setter
    def current_base_controller(self, value: gc.stages.BaseController):
        assert isinstance(value, gc.stages.BaseController)
        self._current_base_controller = value

    @property
    def emf_feedforward(self) -> gc.stages.EMFFeedforward:
        return self._emf_feedforward

    @emf_feedforward.setter
    def emf_feedforward(self, value: gc.stages.EMFFeedforward):
        assert isinstance(value, gc.stages.EMFFeedforward)
        self._emf_feedforward = value

    @property
    def voltage_reference(self) -> np.ndarray:
        return self._voltage_reference

    @property
    def t_n(self):
        if hasattr(self._current_base_controller, 'p_gain') \
        and hasattr(self._current_base_controller, 'i_gain'):
            return self._current_base_controller.p_gain / self._current_base_controller.i_gain
        else:
            return self._tau_current_loop

    def __init__(self):
        super().__init__()
        self._current_base_controller = None
        self._emf_feedforward = None
        self._transformation_stage = None
        self._tau_current_loop = np.array([0.0])
        self._coordinate_transformation_required = False
        self._decoupling = True
        self._voltage_reference = np.array([])
        self._stages = []

    def design(self, action_type, motor_type, base_current_controller='PI', decoupling=True):
        if action_type in ['Finite', 'AbcCont'] and motor_type in gc.tuner.parameter_reader.ac_motors:
            self._coordinate_transformation_required = True
        self._transformation_stage = gc.stages.AbcTransformation()
        if decoupling:
            self._decoupling = True
        self._emf_feedforward = gc.stages.EMFFeedforward()
        self._current_base_controller = gc.stages.base_controllers.get(base_current_controller)('CC')
        self._stages = [self._current_base_controller, self._emf_feedforward, self._transformation_stage]

    def tune(self, env, env_id, a=4):
        if self._coordinate_transformation_required:
            self._transformation_stage.tune(env, env_id)
        self._emf_feedforward.tune(env, env_id)
        self._current_base_controller.tune(env, env_id, a)
        self._voltage_reference = np.zeros(
            len(gc.tuner.parameter_reader.voltages[gc.utils.get_motor_type(env_id)]), dtype=float
        )
        motor = gc.utils.get_motor_type(env_id)
        self._tau_current_loop = gc.tuner.parameter_reader.tau_current_loop_reader[motor]

    def current_control(self, state, current_reference):
        voltage_reference = self._current_base_controller(state, current_reference)
        if self._decoupling:
            voltage_reference = self._emf_feedforward(state, voltage_reference)
        self._voltage_reference = voltage_reference
        if self._coordinate_transformation_required:
            voltage_reference = self._transformation_stage(state, voltage_reference)
        return voltage_reference

    def control(self, state, reference):
        self._voltage_reference = self.current_control(state, reference)
        return self._voltage_reference

    def reset(self):
        for stage in self._stages:
            stage.reset()
