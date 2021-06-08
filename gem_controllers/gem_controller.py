import numpy as np

import gem_controllers as gc
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
    def make(
        cls, env, env_id, decoupling=True, current_safety_margin=0.2, base_current_controller='PI',
        base_speed_controller='PI', a=4
    ):
        """A factory function that generates (and parameterizes) a matching GemController for a given gym-electric-motor
        environment `env`.

        Args:
            env(ElectricMotorEnvironment): The GEM-Environment that the controller shall be created for.
            env_id(str): The corresponding environment-id to specify the concrete environment.
            decoupling(bool): Flag, if a EMF-Feedforward correction stage should be used in the pi current controller.
            current_safety_margin(float in [0..1]): The ratio between the maximum current set point
             the torque controller generates and the absolute current limit.
            base_speed_controller('PI'/'PID'/'P'/'ThreePoint'): Selection of the basic control algorithm for the
             speed controller.
            base_current_controller('PI'/'PID'/'P'/'ThreePoint'): Selection of the basic control algorithm for the
             current controller.
            a(float):
        Returns:
            GemController: An initialized (and tuned) instance of a controller that fits to the specified environment.
        """
        control_task = gc.utils.get_control_task(env_id)
        tuner_kwargs = dict()
        controller = gc.PICurrentController(
            env, env_id, base_current_controller=base_current_controller, decoupling=decoupling
        )
        tuner_kwargs['a'] = a
        if control_task in ['TC', 'SC']:
            controller = gc.TorqueController(env, env_id, current_controller=controller)
            tuner_kwargs['current_safety_margin'] = current_safety_margin
        if control_task == 'SC':
            controller = gc.PISpeedController(
                env, env_id, torque_controller=controller, base_speed_controller=base_speed_controller
            )
        controller = gc.GymElectricMotorAdapter(env, env_id, controller)
        controller.tune(env, env_id, **tuner_kwargs)
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

    def tune(self, env, env_id, **kwargs):
        pass

    def control_environment(self, env, n_steps, render_env=False):
        state, reference = env.reset()
        self.reset()
        for _ in range(n_steps):
            if render_env:
                env.render()
            action = self.control(state, reference)
            (state, reference), _, done, _ = env.step(action)
            if done:
                state, reference = env.reset()
                self.reset()
