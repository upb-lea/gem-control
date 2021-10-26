import gym_electric_motor as gem
import numpy as np
import scipy.interpolate as sp_interpolate

from .operation_point_selection import OperationPointSelection


class PMSMOperationPointSelection(OperationPointSelection):

    def __init__(
            self, torque_control='analytical', max_modulation_level: float = 2 / np.sqrt(3),
            modulation_damping: float = 1.2
    ):
        super().__init__()
        self.torque_control_type = torque_control
        self.mp = None
        self.limit = None
        self.i_sq_limit = 0.0
        self.i_sd_limit = 0.0
        self._modulation_damping = modulation_damping
        self.l_d = 0.0
        self.l_q = 0.0
        self.p = 0
        self.psi_p = 0.0
        self.a_max = max_modulation_level
        self.k_ = 0.95

        self.t_count = 250
        self.psi_count = 250
        self.i_count = 500

        self.torque_list = []
        self.psi_list = []
        self.k_list = []
        self.i_d_list = []
        self.i_q_list = []

        self.omega_idx = None
        self.u_sd_idx = None
        self.u_sq_idx = None
        self.torque_idx = None
        self.epsilon_idx = None
        self.i_sd_idx = None
        self.i_sq_idx = None
        self.max_torque = None
        self.invert = None
        self.tau = None

    def _get_mtpc_lookup_table(self):

        def i_q_(i_d__, torque_, controller):
            return torque_ / (i_d__ * (controller.l_d - controller.l_q) + controller.psi_p) / (1.5 * controller.p)

        def i_d_(i_q__, torque_, controller):
            return -np.abs(torque_ / (1.5 * controller.p * (controller.l_d - controller.l_q) * i_q__))

        # calculate the maximum reference
        self.max_torque = max(
            1.5 * self.p * (self.psi_p + (self.l_d - self.l_q) * (-self.i_sd_limit)) * self.i_sq_limit,
            self.limit[self.torque_idx]
        )
        torque = np.linspace(-self.max_torque, self.max_torque, self.t_count)
        characteristic = []

        for t in torque:
            if self.psi_p != 0:
                if self.l_d == self.l_q:
                    i_d = 0
                else:
                    i_d = np.linspace(-2.5 * self.limit[self.i_sd_idx], 0, self.i_count)
                i_q = i_q_(i_d, t, self)
            else:
                i_q = np.linspace(-2.5 * self.limit[self.i_sq_idx], 2.5 * self.limit[self.i_sq_idx], self.i_count)
                if self.l_d == self.l_q:
                    i_d = 0
                else:
                    i_d = i_d_(i_q, t, self)

            # Different current vectors are determined for each reference and the smallest magnitude is selected
            i = np.power(i_d, 2) + np.power(i_q, 2)
            min_idx = np.where(i == np.amin(i))[0][0]
            if self.l_d == self.l_q:
                i_q_ret = i_q
                i_d_ret = i_d
            else:
                i_q_ret = np.sign((self.l_q - self.l_d) * t) * np.abs(i_q[min_idx])
                i_d_ret = i_d[min_idx]

            # The flow is finally calculated from the currents
            psi = np.sqrt((self.psi_p + self.l_d * i_d_ret) ** 2 + (self.l_q * i_q_ret) ** 2)
            characteristic.append([t, i_d_ret, i_q_ret, psi])
        return np.array(characteristic)

    def get_mtpf_lookup_table(self):
        # maximum flux is calculated
        self.psi_max_mtpf = np.sqrt(
            (self.psi_p + self.l_d * self.i_sd_limit) ** 2
            + (self.l_q * self.i_sq_limit) ** 2
        )
        psi = np.linspace(0, self.psi_max_mtpf, self.psi_count)
        i_d = np.linspace(-self.i_sd_limit, 0, self.i_count)
        i_d_best = 0
        i_q_best = 0
        psi_i_d_q = []

        # Iterates through all flux values to determine the maximum reference
        for psi_ in psi:
            if psi_ == 0:
                i_d_ = -self.psi_p / self.l_d
                i_q = 0
                t = 0
                psi_i_d_q.append([psi_, t, i_d_, i_q])

            else:
                if self.psi_p == 0:
                    i_q_best = psi_ / np.sqrt(self.l_d ** 2 + self.l_q ** 2)
                    i_d_best = -i_q_best
                    t = 1.5 * self.p * (self.psi_p + (self.l_d - self.l_q) * i_d_best) * i_q_best
                else:
                    i_d_idx = np.where(psi_ ** 2 - np.power(self.psi_p + self.l_d * i_d, 2) >= 0)
                    i_d_ = i_d[i_d_idx]

                    # calculate all possible i_q currents for i_d currents
                    i_q = np.sqrt(psi_ ** 2 - np.power(self.psi_p + self.l_d * i_d_, 2)) / self.l_q
                    i_idx = np.where(np.sqrt(np.power(i_q / self.i_sq_limit, 2) + np.power(
                        i_d_ / self.i_sd_limit, 2)) <= 1)
                    i_d_ = i_d_[i_idx]
                    i_q = i_q[i_idx]
                    torque = 1.5 * self.p * (self.psi_p + (self.l_d - self.l_q) * i_d_) * i_q

                    # choose the maximum reference
                    if np.size(torque) > 0:
                        t = np.amax(torque)
                        i_idx = np.where(torque == t)[0][0]
                        i_d_best = i_d_[i_idx]
                        i_q_best = i_q[i_idx]
                if np.sqrt(i_d_best ** 2 + i_q_best ** 2) <= self.i_sq_limit:
                    psi_i_d_q.append([psi_, t, i_d_best, i_q_best])

        psi_i_d_q = np.array(psi_i_d_q)
        self.psi_max_mtpf = np.max(psi_i_d_q[:, 0])
        psi_i_d_q_neg = np.rot90(np.array([psi_i_d_q[:, 0], -psi_i_d_q[:, 1], psi_i_d_q[:, 2], -psi_i_d_q[:, 3]]))
        psi_i_d_q = np.append(psi_i_d_q_neg, psi_i_d_q, axis=0)

        return np.array(psi_i_d_q)

    def tune(self, env: gem.core.ElectricMotorEnvironment, env_id: str, current_safety_margin: float = 0.2):
        super().tune(env, env_id, current_safety_margin)
        self.mp = env.physical_system.electrical_motor.motor_parameter
        self.limit = env.physical_system.limits
        self.omega_idx = env.state_names.index('omega')
        self.u_sd_idx = env.state_names.index('u_sd')
        self.u_sq_idx = env.state_names.index('u_sq')
        self.torque_idx = env.state_names.index('torque')
        self.epsilon_idx = env.state_names.index('epsilon')
        self.i_sd_idx = env.state_names.index('i_sd')
        self.i_sq_idx = env.state_names.index('i_sq')

        self.i_sd_limit = self.limit[self.i_sd_idx] * (1 - current_safety_margin)
        self.i_sq_limit = self.limit[self.i_sq_idx] * (1 - current_safety_margin)
        self.l_d = self.mp['l_d']
        self.l_q = self.mp['l_q']
        self.p = self.mp['p']
        self.psi_p = self.mp.get('psi_p', 0)
        self.invert = -1 if (self.psi_p == 0 and self.l_q < self.l_d) else 1
        self.tau = env.physical_system.tau

        alpha = self._modulation_damping / (self._modulation_damping - np.sqrt(self._modulation_damping ** 2 - 1))
        self.i_gain = 1 / (self.mp['l_q'] / (1.25 * self.mp['r_s'])) * (alpha - 1) / alpha ** 2
        self.u_a_idx = env.state_names.index('u_a')
        self.u_dc = np.sqrt(3) * self.limit[self.u_a_idx]
        self.limited = False
        self.integrated = 0
        self.psi_high = 0.2 * np.sqrt(
            (self.psi_p + self.l_d * self.i_sd_limit) ** 2
            + (self.l_q * self.i_sq_limit) ** 2
        )
        self.psi_low = -self.psi_high
        self.integrated_reset = 0.01 * self.psi_low  # Reset value of the modulation controller
        self.max_torque = max(
            1.5 * self.p * (self.psi_p + (self.l_d - self.l_q) * (-self.limit[self.i_sd_idx]))
            * self.i_sq_limit,
            self.limit[self.torque_idx]
        )
        self.psi_max_mtpf = 0.0
        self.mtpc = self._get_mtpc_lookup_table()
        self.mtpf = self.get_mtpf_lookup_table()

        self.psi_t = np.sqrt(
            np.power(self.psi_p + self.l_d * self.mtpc[:, 1], 2) + np.power(self.l_q * self.mtpc[:, 2], 2)
        )

        self.psi_t = np.array([self.mtpc[:, 0], self.psi_t])

        self.i_q_max = np.linspace(
            -self.i_sq_limit,
            self.i_sq_limit,
            self.i_count
        )

        self.i_d_max = -np.sqrt(self.i_sq_limit ** 2 - np.power(self.i_q_max, 2))
        i_count_mgrid = 200j
        i_d, i_q = np.mgrid[
            -self.limit[self.i_sd_idx]: 0: i_count_mgrid,
            -self.limit[self.i_sq_idx]: self.limit[self.i_sq_idx]: i_count_mgrid / 2
        ]
        i_d = i_d.flatten()
        i_q = i_q.flatten()
        if self.l_d != self.l_q:
            idx = np.where(
                np.sign(self.psi_p + i_d * self.l_d) * np.power(self.psi_p + i_d * self.l_d, 2)
                + np.power(i_q * self.l_q, 2)
                > 0
            )
        else:
            idx = np.where(self.psi_p + i_d * self.l_d > 0)
        i_d = i_d[idx]
        i_q = i_q[idx]

        t = self.p * 1.5 * (self.psi_p + (self.l_d - self.l_q) * i_d) * i_q
        psi = np.sqrt(np.power(self.l_d * i_d + self.psi_p, 2) + np.power(self.l_q * i_q, 2))
        self.t_min = np.amin(t)
        self.t_max = np.amax(t)

        self.psi_min = np.amin(psi)
        self.psi_max = np.amax(psi)

        if self.torque_control_type == 'analytical':
            res = []
            for psi in np.linspace(self.psi_min, self.psi_max, self.psi_count):
                ret = []
                for T in np.linspace(self.t_min, self.t_max, self.t_count):
                    i_d_, i_q_ = self.solve_analytical(T, psi)
                    ret.append([T, psi, i_d_, i_q_])
                res.append(ret)
            res = np.array(res)
            self.t_grid = res[:, :, 0]
            self.psi_grid = res[:, :, 1]
            self.i_d_inter = res[:, :, 2].T
            self.i_q_inter = res[:, :, 3].T

        elif self.torque_control_type == 'interpolate':
            self.t_grid, self.psi_grid = np.mgrid[
                np.amin(t): np.amax(t): np.complex(0, self.t_count),
                self.psi_min: self.psi_max: np.complex(self.psi_count)
            ]
            self.i_q_inter = sp_interpolate.griddata((t, psi), i_q, (self.t_grid, self.psi_grid), method='linear')
            self.i_d_inter = sp_interpolate.griddata((t, psi), i_d, (self.t_grid, self.psi_grid), method='linear')

        elif self.torque_control_type != 'online':
            raise NotImplementedError

        self.k = 0

    def solve_analytical(self, torque, psi):
        """
           Assuming linear magnetization characteristics, the optimal currents for given reference and flux can be obtained
           by solving the reference and flux equations. These lead to a fourth degree polynomial which can be solved
           analytically.  There are two ways to use this analytical solution for control. On the one hand, the currents
           can be determined in advance as in the case of interpolation for different torques and fluxes and stored in a
           LUT (torque_control='analytical'). On the other hand, the solution can be calculated at runtime with the
           given reference and flux (torque_control='online').
        """

        poly = [
            self.l_d ** 2 * (self.l_d - self.l_q) ** 2,

            2 * self.l_d ** 2 * (self.l_d - self.l_q) * self.psi_p
            + 2 * self.l_d * self.psi_p * (self.l_d - self.l_q) ** 2,

            self.l_d ** 2 * self.psi_p ** 2
            + 4 * self.l_d * self.psi_p ** 2 * (self.l_d - self.l_q)
            + (self.psi_p ** 2 - psi ** 2) * (self.l_d - self.l_q) ** 2,

            2 * self.l_q * self.psi_p ** 3
            + 2 * (self.psi_p ** 2 - psi ** 2) * self.psi_p * (self.l_d - self.l_q),

            (self.psi_p ** 2 - psi ** 2) * self.psi_p ** 2
            + (self.l_q * 2 * torque / (3 * self.p)) ** 2
        ]

        sol = np.roots(poly)
        i_d = np.real(sol[-1])
        i_q = 2 * torque / (3 * self.p * (self.psi_p + (self.l_d - self.l_q) * i_d))
        return i_d, i_q

    def get_i_d_q(self, torque, psi, psi_idx):
        i_d, i_q = self.solve_analytical(torque, psi)
        if i_d > self.mtpc[psi_idx, 1]:
            i_d = self.mtpc[psi_idx, 1]
            i_q = self.mtpc[psi_idx, 2]
        return i_d, i_q

    def get_t_idx(self, torque):
        torque = np.clip(torque, self.t_min, self.t_max)
        return int(round((torque[0] - self.t_min) / (self.t_max - self.t_min) * (self.t_count - 1)))

    def get_psi_idx(self, psi):
        psi = np.clip(psi, self.psi_min, self.psi_max)
        return int(round((psi - self.psi_min) / (self.psi_max - self.psi_min) * (self.psi_count - 1)))

    def get_psi_idx_mtpf(self, psi):
        return np.clip(
            int((self.psi_count - 1) - round(psi / self.psi_max_mtpf * (self.psi_count - 1))),
            0,
            self.psi_count
        )

    def get_t_idx_mtpc(self, torque):
        return np.clip(
            int(round((torque[0] + self.max_torque) / (2 * self.max_torque) * (self.t_count - 1))),
            0,
            self.t_count
        )

    def _select_operating_point(self, state, reference):
        """
            This main method is called by the CascadedFieldOrientedController to calculate reference values for the i_d
            and i_q currents from a given reference reference.
        """

        # get the optimal psi for a given reference from the mtpc characteristic
        psi_idx_ = self.get_t_idx_mtpc(reference)
        psi_opt = self.mtpc[psi_idx_, 3]

        # limit the flux to keep the voltage limit using the modulation controller
        psi_max_ = self.modulation_control(state)
        psi_max = min(psi_opt, psi_max_)

        # get the maximum reference for a given flux from the mtpf characteristic
        psi_max_idx = self.get_psi_idx_mtpf(psi_max)
        t_max = np.abs(self.mtpf[psi_max_idx, 1])
        if np.abs(reference) > t_max:
            reference = np.sign(reference) * t_max

        # calculate the currents online
        if self.torque_control_type == 'online':
            i_d, i_q = self.get_i_d_q(reference[0], psi_max, psi_idx_)

        # get the currents from a LUT
        else:
            t_idx = self.get_t_idx(reference)
            psi_idx = self.get_psi_idx(psi_max)

            if self.i_d_inter[t_idx, psi_idx] <= self.mtpf[psi_max_idx, 2]:
                i_d = self.mtpf[psi_max_idx, 2]
                i_q = np.sign(reference[0]) * np.abs(self.mtpf[psi_max_idx, 3])
                reference = np.sign(reference[0]) * t_max
            else:
                i_d = self.i_d_inter[t_idx, psi_idx]
                i_q = self.i_q_inter[t_idx, psi_idx]
                if i_d > self.mtpc[psi_idx_, 1]:
                    i_d = self.mtpc[psi_idx_, 1]
                    i_q = np.sign(reference[0]) * np.abs(self.mtpc[psi_idx_, 2])

        # ensure that the mtpf characteristic curve is observed
        if i_d < self.mtpf[psi_max_idx, 2]:
            i_d = self.mtpf[psi_max_idx, 2]
            i_q = np.sign(reference[0]) * np.abs(self.mtpf[psi_max_idx, 3])

        # invert the i_q if necessary
        i_q = self.invert * i_q

        self.k += 1

        return np.array([i_d, i_q])

    def modulation_control(self, state):
        """
            To ensure the functionality of the current control, a small dynamic manipulated variable reserve to the
            voltage limitation must be kept available. This control is performed by this modulation controller. Further
            information can be found at https://ieeexplore.ieee.org/document/7409195.
        """

        a = 2 * np.sqrt(
            (state[self.u_sd_idx] * self.limit[self.u_sd_idx]) ** 2
            + (state[self.u_sq_idx] * self.limit[self.u_sq_idx]) ** 2
        ) / self.u_dc

        if a > 1.1 * self.a_max:
            self.integrated = self.integrated_reset

        a_delta = self.k_ * self.a_max - a
        omega = max(np.abs(state[self.omega_idx]) * self.limit[self.omega_idx], 0.0001)
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
