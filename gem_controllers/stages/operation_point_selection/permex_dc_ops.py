import numpy as np

import gem_controllers as gc
from .operation_point_selection import OperationPointSelection
from ... import parameter_reader as reader


class PermExDcOperationPointSelection(OperationPointSelection):

    @property
    def magnetic_flux(self):
        return self._magnetic_flux

    @magnetic_flux.setter
    def magnetic_flux(self, value):
        self._magnetic_flux = np.array(value, dtype=float)

    @property
    def voltage_limit(self):
        return self._voltage_limit

    @voltage_limit.setter
    def voltage_limit(self, value):
        self._voltage_limit = np.array(value, dtype=float)

    @property
    def omega_index(self):
        return self._omega_index

    @omega_index.setter
    def omega_index(self, value):
        self._omega_index = int(value)

    @property
    def resistance(self):
        return self._resistance

    @resistance.setter
    def resistance(self, value):
        self._resistance = np.array(value, dtype=float)

    def __init__(self):
        super().__init__()
        self._magnetic_flux = np.array([])
        self._voltage_limit = np.array([])
        self._resistance = np.array([])
        self._omega_index = 0

    def _select_operating_point(self, state, reference):
        if state[self._omega_index] > 0:
            return min(reference / self._magnetic_flux, self._max_current_per_speed(state))
        else:
            return max(reference / self._magnetic_flux, -self._max_current_per_speed(state))

    def _max_current_per_speed(self, state):
        return self._voltage_limit / (self._resistance + self._magnetic_flux * abs(state[self._omega_index]))

    def tune(self, env, env_id, current_safety_margin=0.2):
        super().tune(env, env_id, current_safety_margin=current_safety_margin)
        motor = gc.utils.get_motor_type(env_id)
        self._magnetic_flux = reader.psi_reader[motor](env)
        voltages = reader.voltages[motor]
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        self._voltage_limit = env.limits[voltage_indices]
        self._omega_index = env.state_names.index('omega')
