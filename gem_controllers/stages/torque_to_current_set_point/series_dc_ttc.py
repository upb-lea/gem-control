import numpy as np

import gem_controllers as gc
from .torque_to_current_set_point import TorqueToCurrentSetPoint
from ...tuner import parameter_reader as reader


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

    def tune(self, env, env_id, current_safety_margin=0.2):
        super().tune(env, env_id, current_safety_margin=current_safety_margin)
        motor = gc.utils.get_motor_type(env_id)
        self._cross_inductance = reader.l_prime_reader[motor](env)
