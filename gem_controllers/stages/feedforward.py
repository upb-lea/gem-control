import numpy as np

from .stage import Stage
from ..tuner import parameter_reader as reader


class Feedforward(Stage):

    @property
    def inductance(self):
        return self._inductance

    @inductance.setter
    def inductance(self, value):
        self._inductance = np.array(value)

    @property
    def psi(self):
        return self._psi

    @psi.setter
    def psi(self, value):
        self._psi = np.array(value)

    @property
    def current_indices(self):
        return self._current_indices

    @current_indices.setter
    def current_indices(self, value):
        self._current_indices = np.array(value)

    @property
    def omega_idx(self):
        return self._omega_idx

    @omega_idx.setter
    def omega_idx(self, value):
        self._omega_idx = int(value)

    def __init__(self):
        super().__init__()
        self._inductance = np.array([])
        self._psi = np.array([])
        self._current_indices = np.array([])
        self._omega_idx = None

    def __call__(self, state, reference):
        return reference + (self._inductance * state[self._current_indices] + self._psi) * state[self._omega_idx]

    def tune(self, env, motor_type, action_type, control_task):
        omega_idx = env.state_names.index('omega')
        current_indices = [env.state_names.index(current) for current in reader.currents[motor_type]]
        self.omega_idx = omega_idx
        self.current_indices = current_indices
        self.inductance = -reader.l_reader[motor_type](env)
        self.psi = reader.psi_reader[motor_type](env)
