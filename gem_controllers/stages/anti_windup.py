import numpy as np

import gem_controllers as gc


class AntiWindup:

    def __init__(self, control_task='CC'):
        self._control_task = control_task
        self._state_indices = []
        self._tau = 0.0

    def tune(self, env, env_id):
        self._tau = env.physical_system.tau
        motor_type = gc.utils.get_motor_type(env_id)
        states = []
        if self._control_task == 'CC':
            states = gc.parameter_reader.currents[motor_type]
        elif self._control_task == 'TC':
            states = ['reference']
        elif self._control_task == 'SC':
            states = ['omega']
        self._state_indices = [env.state_names.index(state) for state in states]

    def __call__(self, state, reference, clipping_difference):
        """Limits the integrative part in the base-controllers.

        If any output of the controller was clipped, the integration on this path is stopped.

        Args:
             state(np.ndarray): The state of the environment.
             reference(np.ndarray): The reference that was input into the controller to limit.
             clipping_difference(np.ndarray): The amount of clipping that was put on the output action of the controller

        Returns:
             np.ndarray: The amount how much the integrator-value is altered.
        """
        # np.ndarray(bool): Indicates which actions have been clipped
        non_clipped = clipping_difference == 0
        error = reference - state[self._state_indices]
        return self._tau * error * non_clipped
