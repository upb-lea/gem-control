import numpy as np

from gem_controllers.designer.designer import design_controller
from gem_controllers.tuner.tuner import tune_controller


class GemController:

    @classmethod
    def make(
        cls, env, env_id='', action_type='', motor_type='', control_task='', tune=True, designer_kwargs=None,
        tuner_kwargs=None
    ):
        """
        Args:
            env(ElectricMotorEnvironment): The GEM-Environment for which the controller shall be created.
            env_id(str): The corresponding environment-id to specify the concrete environment
            action_type('Finite'/'Cont'): Specification
        Returns:
            GemController: An initialized (and tuned) instance of a controller that fits to the specified environment.
        """
        if env_id is not '':
            action_type_, control_task_, motor_type_, _ = env_id.split('-')
            if action_type == '':
                action_type = action_type_
            if motor_type == '':
                motor_type = motor_type_
            if control_task == '':
                control_task = control_task_
        assert action_type is not '', 'action_type is unset. Pass either the env-id or an explicit action_type.'
        assert motor_type is not '', 'motor_type is unset. Pass either the env-id or an explicit motor_type.'
        assert control_task is not '', 'control_task is unset. Pass either the env-id or an explicit control_task.'

        designer_kwargs = designer_kwargs if designer_kwargs is not None else {}
        tuner_kwargs = tuner_kwargs if tuner_kwargs is not None else {}
        controller = design_controller(env, action_type, motor_type, control_task, **designer_kwargs)
        if tune:
            tune_controller(controller, env, action_type, motor_type, control_task, **tuner_kwargs)
        return controller

    @property
    def stages(self):
        return self._stages

    def __init__(self):
        self._stages = []

    def control(self, state, reference):
        raise NotImplementedError

    def reset(self):
        for stage in self._stages:
            stage.reset()
