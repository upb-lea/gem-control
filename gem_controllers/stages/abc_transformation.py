from gym_electric_motor.physical_systems.electric_motors import SynchronousMotor
import gem_controllers as gc
from .stage import Stage
import numpy as np


class AbcTransformation(Stage):

    @property
    def advance_factor(self):
        return self._advance_factor

    @advance_factor.setter
    def advance_factor(self, value):
        self._advance_factor = float(value)

    @property
    def tau(self):
        return self._tau

    @tau.setter
    def tau(self, value):
        self._tau = float(value)

    def __init__(self):
        super().__init__()
        self._tau = 1e-4
        self._advance_factor = 0.5
        self.omega_idx = None
        self.angle_idx = None

    def __call__(self, state, reference):
        epsilon_adv = self._angle_advance(state)
        return np.append(SynchronousMotor.t_32(SynchronousMotor.q(reference[0:2], epsilon_adv)), reference[2:])

    def _angle_advance(self, state):
        return state[self.angle_idx] + self._advance_factor * self.tau * state[self.omega_idx]

    def tune(self, env, env_id, **_):
        if gc.utils.get_motor_type(env_id) in gc.parameter_reader.induction_motors:
            self.angle_idx = env.state_names.index('psi_angle')
        else:
            self.angle_idx = env.state_names.index('epsilon')
        self.omega_idx = env.state_names.index('omega')
        if hasattr(env.physical_system.converter, 'dead_time'):
            self._advance_factor = 1.5 if env.physical_system.converter.dead_time else 0.5
        else:
            self._advance_factor = 0.5

