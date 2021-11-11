import numpy as np
l_emf_reader = {
    'SeriesDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_e_prime']
    ]),
    'ShuntDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_e_prime'],
    ]),
    'ExtExDc': lambda env: np.array([
        env.physical_system.electrical_motor.motor_parameter['l_e_prime'],
        0.0
    ]),
    'PermExDc': lambda env: np.array([0.0]),
    'PMSM': lambda env: np.array([
        - env.physical_system.electrical_motor.motor_parameter['l_q'],
        env.physical_system.electrical_motor.motor_parameter['l_d'],
    ]),
    'SynRM': lambda env: np.array([
        - env.physical_system.electrical_motor.motor_parameter['l_q'],
        env.physical_system.electrical_motor.motor_parameter['l_d'],
    ]),
}

class MotorConfiguration:

    currents = []
    emf_currents = []
    voltages = []
    output_voltages = []
    resistance_names = []
    inductance_names = []
    cross_inductance_names = []
    emf_inductance_names = []

    @property
    def current_indices(self):
        return self._current_indices

    @property
    def voltage_indices(self):
        return self._voltage_indices

    @property
    def omega_index(self):
        return self._omega_index

    @property
    def inductances(self):
        return self._inductances

    @property
    def cross_inductances(self):
        return self._cross_inductances

    @property
    def inductance_emf(self):
        return self._inductance_emf

    @property
    def resistances(self):
        return self._resistances

    @property
    def tau_current_loop(self):
        raise NotImplementedError

    @property
    def tau_n(self):
        raise NotImplementedError

    def __init__(self, env):
        mp = env.physical_system.electric_motor
        self._l = np.array([mp[l_name] for l_name in self.inductance_names])
        self._l_emf = np.array([mp[l_name] for l_name in self.cross_inductance_names])
        self._tau_current_loop = np.array([])
        self._r = np.array([mp[r_name] for r_name in self.resistance_names])
        self._tau_n = np.array([])
        self._l_prime = np.array([])
        self._inductances = np.array([])

    def psi(self, state):
        raise NotImplementedError