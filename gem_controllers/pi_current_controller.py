import numpy as np

import gem_controllers as gc


class PICurrentController(gc.CurrentController):

    @property
    def signal_names(self):
        return ['u_PI', 'u_ff', 'u_out']

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
    def stages(self):
        stages_ = [self._current_base_controller]
        if self._decoupling:
            stages_.append(self._emf_feedforward)
        if self._coordinate_transformation_required:
            stages_.append(self._transformation_stage)
        stages_.append(self._clipping_stage)
        return stages_

    @property
    def voltage_reference(self) -> np.ndarray:
        return self._voltage_reference

    @property
    def clipping_stage(self):
        return self._clipping_stage

    @property
    def t_n(self):
        if hasattr(self._current_base_controller, 'p_gain') \
          and hasattr(self._current_base_controller, 'i_gain'):
            return self._current_base_controller.p_gain / self._current_base_controller.i_gain
        else:
            return self._tau_current_loop

    def __init__(self, env, env_id, base_current_controller='PI', decoupling=True):
        super().__init__()
        self._current_base_controller = None
        self._emf_feedforward = None
        self._transformation_stage = None
        self._tau_current_loop = np.array([0.0])
        self._coordinate_transformation_required = False
        self._decoupling = decoupling
        self._voltage_reference = np.array([])
        self._transformation_stage = gc.stages.AbcTransformation()
        if gc.utils.get_motor_type(env_id) in gc.parameter_reader.induction_motors:
            self._emf_feedforward = gc.stages.EMFFeedforwardInd()
        else:
            self._emf_feedforward = gc.stages.EMFFeedforward()
        if gc.utils.get_motor_type(env_id) in gc.parameter_reader.ac_motors:
            self._clipping_stage = gc.stages.clipping_stages.SquaredClippingStage('CC')
        else:
            self._clipping_stage = gc.stages.clipping_stages.AbsoluteClippingStage('CC')
        self._anti_windup_stage = gc.stages.AntiWindup('CC')
        self._current_base_controller = gc.stages.base_controllers.get(base_current_controller)('CC')

    def tune(self, env, env_id, a=4):
        action_type = gc.utils.get_action_type(env_id)
        motor_type = gc.utils.get_motor_type(env_id)
        if action_type in ['Finite', 'Cont'] and motor_type in gc.parameter_reader.ac_motors:
            self._coordinate_transformation_required = True
        if self._coordinate_transformation_required:
            self._transformation_stage.tune(env, env_id)
        self._emf_feedforward.tune(env, env_id)
        self._current_base_controller.tune(env, env_id, a)
        self._anti_windup_stage.tune(env, env_id)
        self._clipping_stage.tune(env, env_id)
        self._voltage_reference = np.zeros(
            len(gc.parameter_reader.voltages[gc.utils.get_motor_type(env_id)]), dtype=float
        )
        self._tau_current_loop = gc.parameter_reader.tau_current_loop_reader[motor_type](env)

    def current_control(self, state, current_reference):
        voltage_reference = self._current_base_controller(state, current_reference)
        if self._decoupling:
            voltage_reference = self._emf_feedforward(state, voltage_reference)
        self._voltage_reference = self._clipping_stage(state, voltage_reference)
        if self._coordinate_transformation_required:
            voltage_reference = self._transformation_stage(state, voltage_reference)
        if hasattr(self._current_base_controller, 'integrator'):
            delta = self._anti_windup_stage.__call__(
                state, current_reference, self._clipping_stage.clipping_difference
            )
            self._current_base_controller.integrator += delta
        return voltage_reference

    def control(self, state, reference):
        self._voltage_reference = self.current_control(state, reference)
        return self._voltage_reference


    def reset(self):
        for stage in self.stages:
            stage.reset()
