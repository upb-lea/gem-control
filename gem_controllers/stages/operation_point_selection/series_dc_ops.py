import numpy as np

import gem_controllers as gc
from .operation_point_selection import OperationPointSelection
from ... import parameter_reader as reader


class SeriesDcOperationPointSelection(OperationPointSelection):
    """This class computes the current operation point of a SeriesDc Motor for a given torque reference value."""

    @property
    def cross_inductance(self):
        return self._cross_inductance

    @cross_inductance.setter
    def cross_inductance(self, value):
        self._cross_inductance = np.array(value, dtype=float)

    def __init__(self):
        super().__init__()
        self._cross_inductance = np.array([])

    def _select_operating_point(self, state, reference):
        """Calculate the current reference for a given torque reference."""
        return np.sqrt(reference / self._cross_inductance)

    def tune(self, env, env_id, current_safety_margin=0.2):
        """Set the indices, limits and motor parameters for the operation point selection."""
        super().tune(env, env_id, current_safety_margin=current_safety_margin)
        motor = gc.utils.get_motor_type(env_id)
        self._cross_inductance = reader.l_prime_reader[motor](env)
