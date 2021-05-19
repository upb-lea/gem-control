import numpy as np

from .p_controller import PController
from .i_controller import IController
from ...tuner import parameter_reader as reader
from .e_base_controller_task import EBaseControllerTask


class PIController(PController, IController):

    def __init__(self, control_task):
        PController.__init__(self, control_task=control_task)
        IController.__init__(self, control_task=control_task)

    def control(self, state, reference):
        filtered_state = state[self._state_indices]
        action = PController._control(self, filtered_state, reference) \
            + IController._control(self, filtered_state, reference)
        self.integrate(filtered_state, reference)
        return np.clip(action, self._action_range[0], self._action_range[1])

    def tune(self, env, motor_type, action_type, control_task, a=4):
        fct = self._get_tuning_function(motor_type, action_type, self._control_task)
        fct(env, motor_type, action_type, control_task, a)

    def _get_tuning_function(self, motor_type, _action_type, sub_control_task):
        if (motor_type in reader.dc_motors) and (sub_control_task == EBaseControllerTask.CC):
            fct = self._tune_dc_current_control
        elif (motor_type in reader.synchronous_motors) and sub_control_task == EBaseControllerTask.CC:
            fct = self._tune_foc_current_control
        elif motor_type in reader.dc_motors and sub_control_task == EBaseControllerTask.SC:
            fct = self._tune_dc_speed_control
        elif motor_type in reader.synchronous_motors and sub_control_task == EBaseControllerTask.SC:
            fct = self._tune_foc_speed_control
        else:
            raise Exception(
                f'No tuning method available for motor type {motor_type} and control_task {sub_control_task}'
            )
        return fct

    def _tune_dc_current_control(self, env, motor_type, action_type, control_task, a=4):
        PController._tune_dc_current_control(self, env, motor_type, action_type, control_task, a)
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

    def _tune_dc_speed_control(self, env, motor_type, action_type, control_task, a=4):
        PController._tune_dc_speed_control(self, env, motor_type, action_type, control_task, a)
        r_a = reader.r_reader[motor_type](env)[0]
        l_a = reader.l_reader[motor_type](env)[0]
        self.i_gain = self.p_gain / (a ** 2 * (l_a / r_a))
        self.tau = env.physical_system.tau_n
        speed_index = env.state_names.index('omega')
        self.state_indices = [speed_index]

    def _tune_foc_current_control(self, env, motor_type, action_type, control_task, a):
        raise NotImplementedError

    def _tune_foc_speed_control(self, env, motor_type, action_type, control_task, a):
        raise NotImplementedError
