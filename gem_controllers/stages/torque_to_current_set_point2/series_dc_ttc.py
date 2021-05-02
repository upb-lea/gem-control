import numpy as np

from .torque_to_current_set_point import TorqueToCurrentSetPoint
from ...tuner.parameter_reader import l_prime_reader


class SeriesDcTorqueToCurrent(TorqueToCurrentSetPoint):

    @property
    def cross_inductance(self):
        return self._cross_inductance

    @cross_inductance.setter
    def cross_inductance(self, value):
        self._cross_inductance = np.array(value, dtype=float)

    def __init__(self):
        super().__init__()
        self._cross_inductance = np.array([])

    def _torque_to_current(self, state, reference):
        return np.sqrt(reference / self._cross_inductance)

    def tune(self, env, motor, action_type, control_task):
        self._cross_inductance = l_prime_reader[motor](env)
