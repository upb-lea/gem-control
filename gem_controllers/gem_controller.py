import numpy as np

from gem_controllers.designer.designer import design_controller
from gem_controllers.tuner.tuner import tune_controller


class GemController:
    """The GemController is the base for all motor controllers in the gem-control package.

    A gem-controller consists of multiple stages that execute different control tasks like speed-control, a torque
    to current set point mapping or input and output processing.

    Furthermore, the GemController has got a `GemController.make` factory function that automatically designs and tunes
     a classical cascaded motor controller based on classic control techniques like th e proportional-integral (PI)
      controller to control a gym-electric-motor environment.
    """

    @classmethod
    def make(cls, env, env_id, tune=True, designer_kwargs=None, tuner_kwargs=None):
        """A factory function that generates (and parameterizes) a matching GemController for a given gym-electric-motor
        environment `env`.

        Args:
            env(ElectricMotorEnvironment): The GEM-Environment that the controller shall be created for.
            env_id(str): The corresponding environment-id to specify the concrete environment.
            tune(bool)=True: Flag, if the controller shall be parameterized automatically.
            designer_kwargs(dict): Dictionary for additional parameters that are passed to the controller designer.
                Specific entries can be looked up here. #ToDo Add Link to designer
            tuner_kwargs(dict): Dictionary for additional parameters that are passed to the controller tuner.
                Specific entries can be looked up here. #ToDo Add Link to designer
        Returns:
            GemController: An initialized (and tuned) instance of a controller that fits to the specified environment.
        """

        action_type, control_task, motor_type, _ = env_id.split('-')

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
