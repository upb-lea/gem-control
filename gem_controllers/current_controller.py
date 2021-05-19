import numpy as np

import gem_controllers as gc


class CurrentController(gc.GemController):

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
    def transformation_stage(self):
        return self._transformation_stage

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
    def voltage_reference(self):
        return self._voltage_reference

    def __init__(self):
        super().__init__()
        self._input_stage = None
        self._output_stage = None
        self._current_base_controller = None
        self._emf_feedforward = None
        self._transformation_stage = None
        self._tau_n_cc_loop = 0.0
        self._coordinate_transformation_required = False
        self._decoupling = True
        self._voltage_reference = np.array([])

    def design(self, action_type, motor_type, base_current_controller='PI', decoupling=True):
        self._input_stage = gc.stages.InputStage()
        if action_type == 'Finite':
            self._output_stage = gc.stages.DiscOutputStage()
        else:
            self._output_stage = gc.stages.ContOutputStage()
        if action_type in ['Finite', 'AbcCont'] and motor_type in gc.tuner.parameter_reader.ac_motors:
            self._coordinate_transformation_required = True
        self._transformation_stage = gc.stages.AbcTransformation()
        if decoupling:
            self._decoupling = True
        self._emf_feedforward = gc.stages.EMFFeedforward()
        self._current_base_controller = gc.designer.designer.controller_registry[base_current_controller]('CC')
        self._stages = [
            self._input_stage, self._current_base_controller, self._emf_feedforward, self._transformation_stage,
            self._output_stage
        ]

    def tune(self, env, motor_type, action_type, control_task, a=4):
        self._input_stage.tune(env, motor_type, action_type, control_task)
        if self._coordinate_transformation_required:
            self._transformation_stage.tune(env, motor_type, action_type, control_task)
        self._emf_feedforward.tune(env, motor_type, action_type, control_task)
        self._current_base_controller.tune(env, motor_type, action_type, control_task, a)
        self._output_stage.tune(env, motor_type, action_type, control_task)
        self._voltage_reference = np.zeros(len(gc.tuner.parameter_reader.voltages[motor_type]), dtype=float)

    def current_control(self, state, current_reference):
        voltage_reference = self._current_base_controller(state, current_reference)
        if self._decoupling:
            voltage_reference = self._emf_feedforward(state, voltage_reference)
        self._voltage_reference = voltage_reference
        if self._coordinate_transformation_required:
            voltage_reference = self._transformation_stage(state, voltage_reference)
        return voltage_reference

    def control(self, state, reference):
        reference = self._input_stage(state, reference)
        voltage_set_point = self.current_control(state, reference)
        return self._output_stage(state, voltage_set_point)

    def reset(self):
        for stage in self._stages:
            stage.reset()
