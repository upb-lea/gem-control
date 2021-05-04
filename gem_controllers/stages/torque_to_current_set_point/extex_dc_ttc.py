import numpy as np

from .torque_to_current_set_point import TorqueToCurrentSetPoint
from ...tuner.parameter_reader import l_prime_reader


class ExtExDcTorqueToCurrent(TorqueToCurrentSetPoint):

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
    def i_e_policy(self):
        return self._i_e_policy

    @i_e_policy.setter
    def i_e_policy(self, value):
        assert callable(value), 'The i_e_policy has to be a callable function.'
        self._i_e_policy = value

    def __init__(self):
        super().__init__()
        self._cross_inductance = np.array([])
        self._i_e_idx = None
        self._i_a_idx = None
        self._i_e_policy = self.__i_e_policy

    def __i_e_policy(self, state, reference):
        """The policy for the exciting current that is used per default.

        It aims to keep i_e = 0.5 * abs(i_a)
        """
        return abs(state[self._i_a_idx]) * 0.5

    def _torque_to_current(self, state, reference):
        i_e_ref = self._i_e_policy(state, reference)
        i_a_ref = reference[0] / self._cross_inductance[0] / max(state[self._i_e_idx], 1e-4)
        return np.array([i_a_ref, i_e_ref])

    def tune(self, env, motor, action_type, control_task, current_safety_margin=0.2):
        super().tune(env, motor,action_type, control_task, current_safety_margin)
        self._i_e_idx = env.state_names.index('i_e')
        self._i_a_idx = env.state_names.index('i_a')
        self._cross_inductance = l_prime_reader[motor](env)
