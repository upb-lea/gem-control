import gym_electric_motor as gem
import gem_controllers as gc


class GymElectricMotorAdapter(gc.GemController):

    @property
    def input_stage(self):
        return self._input_stage

    @input_stage.setter
    def input_stage(self, value):
        self._input_stage = value

    @property
    def output_stage(self):
        return self._output_stage

    @output_stage.setter
    def output_stage(self, value):
        self._output_stage = value

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, value):
        self._controller = value

    def __init__(
            self,
            controller: gc.GemController,
            env: (gem.core.ElectricMotorEnvironment, None) = None,
            env_id: (str, None) = None
    ):
        super().__init__()
        self._input_stage = None
        self._output_stage = None
        assert isinstance(controller, gc.GemController)
        self._controller = controller
        if env is not None and env_id is not None:
            self.design(env, env_id)
            self.tune(env, env_id)

    def control(self, state, reference):
        denormalized_ref = self._input_stage(state, reference)
        voltage_set_point = self._controller.control(state, denormalized_ref)
        action = self._output_stage(state, voltage_set_point)
        return action

    def design(self, env, env_id, **design_kwargs):
        self._input_stage = gc.stages.InputStage()
        action_type = gc.utils.get_action_type(env_id)
        if action_type == 'Finite':
            self._output_stage = gc.stages.DiscOutputStage()
        else:
            self._output_stage = gc.stages.ContOutputStage()
        self._controller.design(env, env_id, **design_kwargs)

    def tune(self, env, env_id, **kwargs):
        self._input_stage.tune(env, env_id)
        self._output_stage.tune(env, env_id)
        self._controller.tune(env, env_id, **kwargs)

    def reset(self):
        self._input_stage.reset()
        self._controller.reset()
        self._output_stage.reset()
