import numpy as np

from .base_controller import BaseController, EBaseControllerTask
from ... import parameter_reader as reader
import gem_controllers as gc


class PController(BaseController):

    @property
    def p_gain(self):
        return self._p_gain

    @p_gain.setter
    def p_gain(self, value):
        self._p_gain = value

    @property
    def state_indices(self):
        return self._state_indices

    @state_indices.setter
    def state_indices(self, value):
        self._state_indices = np.array(value)

    @property
    def action_range(self):
        return self._action_range

    @action_range.setter
    def action_range(self, value):
        self._action_range = value

    def __call__(self, state, reference):
        return self.control(state, reference)

    def __init__(self, control_task, p_gain=np.array([0.0]), action_range=(np.array([0.0]), np.array([0.0]))):
        BaseController.__init__(self, control_task)
        self._p_gain = p_gain
        self._action_range = action_range
        self._state_indices = np.array([])

    def _control(self, state, reference):
        return self._p_gain * (reference - state)

    def control(self, state, reference):
        return self._control(state[self._state_indices], reference)

    def tune(self, env, env_id, a=4):
        if self._control_task == EBaseControllerTask.CurrentControl:
            self._tune_current_controller(env, env_id, a)
        elif self._control_task == EBaseControllerTask.SpeedControl:
            self._tune_speed_controller(env, env_id, a)
        else:
            raise Exception(f'No Tuner available for control task{self._control_task}.')

    def _tune_current_controller(self, env, env_id, a):
        action_type, control_task, motor_type = gc.utils.split_env_id(env_id)
        l_ = reader.l_reader[motor_type](env)
        tau = env.physical_system.tau
        currents = reader.currents[motor_type]
        voltages = reader.voltages[motor_type]
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        current_indices = [env.state_names.index(current) for current in currents]
        voltage_limits = env.limits[voltage_indices]
        current_limits = env.limits[current_indices]
        self.p_gain = l_ / (tau * a) * current_limits / voltage_limits
        self.action_range = (
            env.observation_space[0].low[voltage_indices] * voltage_limits,
            env.observation_space[0].high[voltage_indices] * voltage_limits,
        )
        self.state_indices = current_indices

    def _tune_speed_controller(self, env, env_id, a=4, t_n=None):
        if t_n is None:
            t_n = env.physical_system.tau
        j_total = env.physical_system.mechanical_load.j_total
        torque_index = env.state_names.index('torque')
        speed_index = env.state_names.index('omega')
        torque_limit = env.limits[torque_index]
        speed_limit = env.limits[speed_index]
        p_gain = j_total / (a * t_n) * speed_limit / torque_limit
        self.p_gain = np.array([p_gain])
        self.state_indices = [speed_index]
        self.action_range = (
            env.observation_space[0].low[[torque_index]] * np.array([torque_limit]),
            env.observation_space[0].high[[torque_index]] * np.array([torque_limit])
        )
