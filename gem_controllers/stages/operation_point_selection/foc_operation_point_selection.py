from .operation_point_selection import OperationPointSelection
import numpy as np


class FieldOrientedControllerOperationPointSelection(OperationPointSelection):
    def __init__(self, max_modulation_level: float = 2 / np.sqrt(3), modulation_damping: float = 1.2):
        self.mp = None
        self.limit = None
        self.nominal_value = None
        self.i_sq_limit = None
        self.i_sd_limit = None
        self.p = None

        self.t_count = None
        self.psi_count = None

        self.omega_idx = None
        self.u_sd_idx = None
        self.u_sq_idx = None
        self.u_a_idx = None
        self.torque_idx = None
        self.epsilon_idx = None
        self.i_sd_idx = None
        self.i_sq_idx = None
        self.tau = None

        self.modulation_damping = modulation_damping
        self.a_max = max_modulation_level
        self.alpha = None
        self.i_gain = None
        self.k_ = None
        self.limited = None
        self.u_dc = None
        self.integrated = 0
        self.psi_high = None
        self.psi_low = None
        self.integrated_reset = None

    def tune(self, env, env_id, current_safety_margin=0.2):
        super().tune(env, env_id, current_safety_margin)
        self.mp = env.physical_system.electrical_motor.motor_parameter
        self.limit = env.physical_system.limits
        self.nominal_value = env.physical_system.nominal_state

        self.omega_idx = env.state_names.index('omega')
        self.u_sd_idx = env.state_names.index('u_sd')
        self.u_sq_idx = env.state_names.index('u_sq')
        self.torque_idx = env.state_names.index('torque')
        self.epsilon_idx = env.state_names.index('epsilon')
        self.i_sd_idx = env.state_names.index('i_sd')
        self.i_sq_idx = env.state_names.index('i_sq')
        u_a = 'u_a' if 'u_a' in env.state_names else 'u_sa'
        self.u_a_idx = env.state_names.index(u_a)

        self.i_sd_limit = self.limit[self.i_sd_idx] * (1 - current_safety_margin)
        self.i_sq_limit = self.limit[self.i_sq_idx] * (1 - current_safety_margin)

        self.p = self.mp['p']
        self.tau = env.physical_system.tau

        self.alpha = self.modulation_damping / (self.modulation_damping - np.sqrt(self.modulation_damping ** 2 - 1))
        self.limited = False
        self.u_dc = np.sqrt(3) * self.limit[self.u_a_idx]
        self.integrated = 0

    def _select_operating_point(self, state, reference):
        pass

    def modulation_control(self, state):
        """
        To ensure the functionality of the current control, a small dynamic manipulated variable reserve to the
        voltage limitation must be kept available. This control is performed by this modulation controller. Further
        information can be found at https://ieeexplore.ieee.org/document/7409195.
        """

        a = 2 * np.sqrt(state[self.u_sd_idx] ** 2 + state[self.u_sq_idx] ** 2) / self.u_dc

        if a > 1.1 * self.a_max:
            self.integrated = self.integrated_reset

        a_delta = self.k_ * self.a_max - a
        omega = max(np.abs(state[self.omega_idx]), 0.0001)
        psi_max_ = self.u_dc / (np.sqrt(3) * omega * self.p)
        k_i = 2 * omega * self.p / self.u_dc

        i_gain = self.i_gain / k_i
        psi_delta = i_gain * (a_delta * self.tau + self.integrated)

        if self.psi_low <= psi_delta <= self.psi_high:
            if self.limited:
                self.integrated = self.integrated_reset
                self.limited = False
            self.integrated += a_delta * self.tau

        else:
            psi_delta = np.clip(psi_delta, self.psi_low, self.psi_high)
            self.limited = True

        psi = psi_max_ + psi_delta

        return psi

    def reset(self):
        self.integrated = self.integrated_reset
