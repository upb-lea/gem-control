from .p_controller import PController
from .i_controller import IController
from ... import parameter_reader as reader
from .e_base_controller_task import EBaseControllerTask
import gem_controllers as gc
import numpy as np


class PIController(PController, IController):

    def __init__(self, control_task):
        PController.__init__(self, control_task=control_task)
        IController.__init__(self, control_task=control_task)

    def control(self, state, reference):
        filtered_state = state[self._state_indices]
        action = PController._control(self, filtered_state, reference) \
            + IController._control(self, filtered_state, reference)
        return action

    def tune(self, env, env_id, a=4, t_n=None, **_):
        if self._control_task == EBaseControllerTask.CC:
            self._tune_current_controller(env, env_id, a)
        elif self._control_task == EBaseControllerTask.SC:
            self._tune_speed_controller(env, env_id, a, t_n)
        elif self._control_task == EBaseControllerTask.FC:
            self._tune_flux_controller(env, env_id, a, t_n)
        else:
            raise Exception(f'No tuning method available.')

    def _tune_current_controller(self, env, env_id, a=4):
        action_type, control_task, motor_type = gc.utils.split_env_id(env_id)
        PController._tune_current_controller(self, env, env_id, a)
        l_ = reader.l_reader[motor_type](env)
        tau = env.physical_system.tau
        currents = reader.currents[motor_type]
        voltages = reader.voltages[motor_type]
        voltage_indices = [env.state_names.index(voltage) for voltage in voltages]
        current_indices = [env.state_names.index(current) for current in currents]
        voltage_limits = env.limits[voltage_indices]
        i_gain = self.p_gain / (tau * a ** 2)

        action_range = (
            env.observation_space[0].low[voltage_indices] * voltage_limits,
            env.observation_space[0].high[voltage_indices] * voltage_limits,
        )
        self.i_gain = i_gain
        self.action_range = action_range
        self.tau = tau
        self.state_indices = current_indices

    def _tune_speed_controller(self, env, env_id, a=4, t_n=None):
        PController._tune_speed_controller(self, env, env_id, a, t_n)
        self.i_gain = self.p_gain / (a * t_n)
        self.tau = env.physical_system.tau
        speed_index = env.state_names.index('omega')
        self.state_indices = [speed_index]

    def _tune_flux_controller(self, env, env_id, a=4, t_n=None):
        self.tau = env.physical_system.tau
        self.p_gain = np.array([a * t_n ** 2])
        self.i_gain = self.p_gain / self.tau
        self.state_indices = [0]
