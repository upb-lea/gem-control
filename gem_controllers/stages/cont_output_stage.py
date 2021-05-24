import numpy as np

from .stage import Stage
from ..tuner import parameter_reader as reader


class ContOutputStage(Stage):

    @property
    def voltage_limit(self):
        return self._voltage_limit

    @voltage_limit.setter
    def voltage_limit(self, value):
        self._voltage_limit = np.array(value, dtype=float)

    def __init__(self):
        super().__init__()
        self._voltage_limit = np.array([])

    def __call__(self, state, reference):
        return reference / self.voltage_limit

    def tune(self, env, motor_type, action_type, control_task):
        voltages = reader.get_output_voltages(motor_type, action_type)
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        self.voltage_limit = env.limits[voltage_indices]
