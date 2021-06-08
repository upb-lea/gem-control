import numpy as np

from .stage import Stage
from ..tuner import parameter_reader as reader
import gem_controllers as gc


class EMFFeedforward(Stage):

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

    @property
    def action_range(self):
        return self._action_range

    def __init__(self):
        super().__init__()
        self._inductance = np.array([])
        self._psi = np.array([])
        self._current_indices = np.array([])
        self._omega_idx = None
        self._action_range = np.array([]), np.array([])

    def __call__(self, state, reference):
        action = reference + (self._inductance * state[self._current_indices] + self._psi) * state[self._omega_idx]
        return action

    def tune(self, env, env_id, **_):
        motor_type = gc.utils.get_motor_type(env_id)
        omega_idx = env.state_names.index('omega')
        current_indices = [env.state_names.index(current) for current in reader.emf_currents[motor_type]]
        self.omega_idx = omega_idx
        self.current_indices = current_indices
        self.inductance = reader.l_emf_reader[motor_type](env)
        self.psi = reader.psi_reader[motor_type](env)
        voltages = reader.voltages[motor_type]
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        voltage_limits = env.limits[voltage_indices]
        self._action_range = (
            env.observation_space[0].low[voltage_indices] * voltage_limits,
            env.observation_space[0].high[voltage_indices] * voltage_limits,
        )
