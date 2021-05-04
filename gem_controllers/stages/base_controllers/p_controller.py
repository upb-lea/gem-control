import numpy as np

from .base_controller import BaseController, EControlTask
from gem_controllers.tuner import parameter_reader as reader


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
        super().__init__(control_task)
        self._p_gain = p_gain
        self._action_range = action_range
        self._state_indices = np.array([])

    def _control(self, state, reference):
        return self._p_gain * (reference - state)

    def _clip(self, action):
        return np.clip(action, self._action_range[0], self._action_range[1])

    def control(self, state, reference):
        return self._clip(self._control(state[self._state_indices], reference))

    def tune(self, env, motor_type, action_type, control_task, a=4):
        if self._control_task == EControlTask.CurrentControl and motor_type in reader.dc_motors:
            self._tune_dc_current_control(env, motor_type, action_type, control_task, a)
        elif self._control_task == EControlTask.CurrentControl and motor_type in reader.synchronous_motors:
            self._tune_foc_current_control(env, motor_type, action_type, control_task, a)
        elif self._control_task == EControlTask.SpeedControl and motor_type in reader.dc_motors:
            self._tune_dc_speed_control(env, motor_type, action_type, control_task, a)
        elif self._control_task == EControlTask.SpeedControl and motor_type in reader.synchronous_motors:
            self._tune_foc_speed_control(env, motor_type, action_type, control_task, a)

    def _tune_dc_current_control(self, env, motor_type, _action_type, _control_task, a):
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

    def _tune_dc_speed_control(self, env, motor_type, _action_range, _control_task, a=4):
        j_total = env.physical_system.mechanical_load.j_total
        r_a = reader.r_reader[motor_type](env)[0]
        l_a = reader.l_reader[motor_type](env)[0]
        torque_index = env.state_names.index('torque')
        speed_index = env.state_names.index('omega')
        torque_limit = env.limits[torque_index]
        speed_limit = env.limits[speed_index]
        torque_range = (
            np.array([env.observation_space[0].low[torque_index] * torque_limit]),
            np.array([env.observation_space[0].high[torque_index] * torque_limit])
        )
        p_gain = j_total / (a * (l_a / r_a)) * speed_limit / torque_limit
        self.p_gain = np.array([p_gain])

        self.state_indices = [speed_index]
        self._action_range = torque_range

    def _tune_foc_speed_control(self, env, motor_type, action_type, control_task, a):
        raise NotImplementedError

    def _tune_foc_current_control(self, env, motor_type, action_type, control_task, a):
        raise NotImplementedError
