import gem_controllers as gc


class CurrentController(gc.FeedforwardController):

    @property
    def output_stage(self):
        return self._output_stage

    @output_stage.setter
    def output_stage(self, value):
        assert isinstance(value, (gc.stages.ContOutputStage, gc.stages.DiscOutputStage))
        self._output_stage = value

    @property
    def current_base_controller(self):
        return self._current_base_controller

    @current_base_controller.setter
    def current_base_controller(self, value):
        assert isinstance(value, gc.stages.BaseController)
        self._current_base_controller = value

    @property
    def emf_feedforward(self):
        return self._emf_feedforward

    @emf_feedforward.setter
    def emf_feedforward(self, value):
        assert isinstance(value, gc.stages.EMFFeedforward)
        self._emf_feedforward = value

    @property
    def tau(self):
        return self._tau_current_control_loop

    def __init__(self):
        super().__init__()
        self._output_stage = None
        self._current_base_controller = None
        self._emf_feedforward = None
        self._abc_transformation = None
        self._tau_current_control_loop = 0.0
        self._current_control = lambda state, reference: 0

    def tune(self, env, motor_type, action_type, control_task):
        pass

    def _dc_cont_current_control(self, state, reference):
        voltage_reference = self._current_base_controller(state, reference)
        ff_voltage = self._emf_feedforward(state, voltage_reference)
        return ff_voltage

    def control(self, state, reference):
        voltage_set_point = self._current_control(state, reference)
        return self._output_stage(state, voltage_set_point)