import numpy as np

from .torque_to_current_set_point import TorqueToCurrentSetPoint
from ...tuner.parameter_reader import l_prime_reader


class ShuntDcTorqueToCurrent(TorqueToCurrentSetPoint):

    @property
    def cross_inductance(self):
        return self._cross_inductance

    @cross_inductance.setter
    def cross_inductance(self, value):
        self._cross_inductance = np.array(value, dtype=float)

    @property
    def i_e_idx(self):
        return self._i_e_idx

    @i_e_idx.setter
    def i_e_idx(self, value):
        self._i_e_idx = int(value)

    @property
    def i_a_idx(self):
        return self._i_a_idx

    @i_a_idx.setter
    def i_a_idx(self, value):
        self._i_a_idx = int(value)

    @property
    def i_a_limit(self):
        return self._i_a_limit

    @i_a_limit.setter
    def i_a_limit(self, value):
        self._i_a_limit = np.array(value, dtype=float)

    @property
    def i_e_limit(self):
        return self._i_e_limit

    @i_e_limit.setter
    def i_e_limit(self, value):
        self._i_e_limit = np.array(value, dtype=float)

    def __init__(self):
        super().__init__()
        self._cross_inductance = np.array([])
        self._i_e_idx = None
        self._i_a_idx = None
        self._i_a_limit = np.array([])
        self._i_e_limit = np.array([])

    def _torque_to_current(self, state, reference):
        # If i_e is too high, set i_a reference to 0 to also lower i_e again.
        if state[self._i_e_idx] > self._i_e_limit:
            return -self._i_a_limit
        if state[self._i_e_idx] < -self._i_e_limit:
            return self._i_a_limit

        # avoid division by zero
        i_e = max(state[self._i_e_idx], 1e-3 * self._i_e_limit)
        return reference / self._cross_inductance / i_e

    def tune(self, env, motor, action_type, control_task, current_safety_margin=0.2):
        self._cross_inductance = l_prime_reader['ShuntDc'](env)
        self._i_e_idx = env.state_names.index('i_e')
        self._i_a_idx = env.state_names.index('i_a')
        self._i_a_limit = env.limits[self._i_a_idx] * (1 - current_safety_margin)
        self._i_e_limit = env.limits[self._i_e_idx] * (1 - current_safety_margin)
