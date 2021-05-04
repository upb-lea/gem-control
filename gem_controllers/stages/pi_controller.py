import numpy as np

from .p_controller import PController
from .i_controller import IController
from ..tuner import parameter_reader as reader


class PIController(PController, IController):
    
    def control(self, state, reference):
        filtered_state = state[self._state_indices]
        action = PController._control(self, filtered_state, reference) \
            + IController._control(self, filtered_state, reference)
        self.integrate(filtered_state, reference)
        return np.clip(action, self._action_range[0], self._action_range[1])

    def tune(self, env, motor_type, action_type, control_task, sub_control_task='CC', a=4):
        fct = self._get_tuning_function(motor_type, action_type, sub_control_task)
        fct(env, motor_type, action_type, control_task, a)
    
    def _get_tuning_function(self, motor_type, action_type, sub_control_task):
        if (motor_type in reader.dc_motors) and (sub_control_task == 'CC'):
            fct = self.tune_dc_current_controller
        elif (motor_type in reader.synchronous_motors) and sub_control_task == 'CC':
            fct = self.tune_foc_current_controller
        elif motor_type in reader.dc_motors and sub_control_task == 'SC':
            fct = self.tune_dc_speed_controller
        elif motor_type in reader.synchronous_motors and sub_control_task == 'SC':
            fct = self.tune_foc_speed_controller
        else:
            raise Exception(
                f'No tuning method available for motor type {motor_type} and control_task {sub_control_task}'
            )
        return fct

    def tune_dc_current_controller(self, env, motor_type, action_type, control_task, a=4):
        l_ = reader.l_reader[motor_type](env)
        tau = env.physical_system.tau
        currents = reader.currents[motor_type]
        voltages = reader.voltages[motor_type]
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        current_indices = [env.state_names.index(current) for current in currents]
        voltage_limits = env.limits[voltage_indices]
        current_limits = env.limits[current_indices]
        p_gain = l_ / (tau * a) * current_limits / voltage_limits
        i_gain = p_gain / (tau * a ** 2)

        action_range = (
            env.observation_space[0].low[voltage_indices] * voltage_limits,
            env.observation_space[0].high[voltage_indices] * voltage_limits,
        )
        self.p_gain = p_gain
        self.i_gain = i_gain
        self.action_range = action_range
        self.tau = tau
        self.state_indices = current_indices

    def tune_dc_speed_controller(self, env, motor_type, action_type, control_task, a=4):
        j_total = env.physical_system.mechanical_load.j_total
        tau = env.physical_system.tau
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
        i_gain = p_gain / (a ** 2 * (l_a / r_a))
        self.p_gain = np.array([p_gain])
        self.i_gain = np.array([i_gain])
        self.tau = tau
        self.state_indices = [speed_index]
        self.action_range = torque_range

    def tune_foc_speed_controller(self, env, motor_type, action_type, control_task, a=4):
        raise NotImplementedError

    def tune_foc_current_controller(self, env, motor_type, action_type, control_task, a=4):
        raise NotImplementedError
