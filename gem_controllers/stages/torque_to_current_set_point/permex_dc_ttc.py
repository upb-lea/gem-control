import numpy as np

from .torque_to_current_set_point import TorqueToCurrentSetPoint
from ...tuner.parameter_reader import psi_reader


class PermExDcTorqueToCurrent(TorqueToCurrentSetPoint):

    @property
    def magnetic_flux(self):
        return self._magnetic_flux

    @magnetic_flux.setter
    def magnetic_flux(self, value):
        self._magnetic_flux = np.array(value, dtype=float)

    def __init__(self):
        super().__init__()
        self._magnetic_flux = np.array([])

    def _torque_to_current(self, state, reference):
        return np.sqrt(reference / self._magnetic_flux)

    def tune(self, env, motor, action_type, control_task, current_safety_margin=0.2):
        super().tune(env, motor, action_type, control_task, current_safety_margin)
        self._magnetic_flux = psi_reader[motor](env)
