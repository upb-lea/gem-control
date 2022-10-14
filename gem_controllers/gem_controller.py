import gym_electric_motor.core

import gem_controllers as gc
import numpy as np


class GemController:
    """The GemController is the base for all motor controllers in the gem-control package.

    A gem-controller consists of multiple stages that execute different control tasks like speed-control, a reference
    to current set point mapping or input and output processing.

    Furthermore, the GemController has got a `GemController.make` factory function that automatically designs and tunes
     a classical cascaded motor controller based on classic control techniques like th e proportional-integral (PI)
      controller to control a gym-electric-motor environment.
    """

    @property
    def signals(self):
        return []

    @property
    def signal_names(self):
        return []

    @classmethod
    def make(
        cls,
        env: gym_electric_motor.core.ElectricMotorEnvironment,
        env_id: str,
        decoupling: bool = True,
        current_safety_margin: float = 0.2,
        base_current_controller: str = 'PI',
        base_speed_controller: str = 'PI',
        a: int = 4,

        block_diagram: bool = True,
        save_block_diagram_as: (str, tuple) = None,
        plot_references: bool = True,
    ):
        """A factory function that generates (and parameterizes) a matching GemController for a given gym-electric-motor
        environment `env`.

        Args:
            env(ElectricMotorEnvironment): The GEM-Environment that the controller shall be created for.
            env_id(str): The corresponding environment-id to specify the concrete environment.
            decoupling(bool): Flag, if a EMF-Feedforward correction stage should be used in the pi current controller.
            current_safety_margin(float in [0..1]): The ratio between the maximum current set point
             the reference controller generates and the absolute current limit.
            base_speed_controller('PI'/'PID'/'P'/'ThreePoint'): Selection of the basic control algorithm for the
             speed controller.
            base_current_controller('PI'/'PID'/'P'/'ThreePoint'): Selection of the basic control algorithm for the
             current controller.
            a(float): Tuning parameter of the symmetrical optimum.
            block_diagram(bool): Selection whether the block diagram should be displayed
            save_block_diagram_as(str, tuple): Selection of whether the block diagram should be saved
            plot_references(bool): Flag, if the reference values of the underlying control circuits should be plotted

        Returns:
            GemController: An initialized (and tuned) instance of a controller that fits to the specified environment.
        """
        control_task = gc.utils.get_control_task(env_id)
        tuner_kwargs = dict()
        controller = gc.PICurrentController(
            env, env_id, base_current_controller=base_current_controller, decoupling=decoupling
        )
        tuner_kwargs['a'] = a
        tuner_kwargs['plot_references'] = plot_references
        if control_task in ['TC', 'SC']:
            controller = gc.TorqueController(env, env_id, current_controller=controller)
            tuner_kwargs['current_safety_margin'] = current_safety_margin
        if control_task == 'SC':
            controller = gc.PISpeedController(
                env, env_id, torque_controller=controller, base_speed_controller=base_speed_controller
            )
        # Wrap the controller with the adapter to map the inputs and outputs to the environment
        controller = gc.GymElectricMotorAdapter(env, env_id, controller)

        # Fit the controllers parameters to the environment
        controller.tune(env, env_id, **tuner_kwargs)

        if block_diagram:
            controller.build_block_diagram(env_id, save_block_diagram_as)

        return controller

    @property
    def stages(self):
        return self._stages

    def __init__(self):
        self._stages = []

    def get_signal_value(self, signal_name):
        return self.signals[self.signal_names.index(signal_name)]

    def control(self, state, reference):
        raise NotImplementedError

    def reset(self):
        for stage in self._stages:
            stage.reset()

    def tune(self, env, env_id, **kwargs):
        pass

    def control_environment(self, env, n_steps, max_episode_length=np.inf, render_env=False):
        state, reference = env.reset()
        if self.block_diagram:
            self.block_diagram.open()
        self.reset()
        current_episode_length = 0
        for _ in range(n_steps):
            if render_env:
                env.render()
            action = self.control(state, reference)
            (state, reference), _, done, _ = env.step(action)
            if done or current_episode_length >= max_episode_length:
                state, reference = env.reset()
                self.reset()
                current_episode_length = 0
            current_episode_length = current_episode_length + 1
        if self.block_diagram:
            self.block_diagram.close()
