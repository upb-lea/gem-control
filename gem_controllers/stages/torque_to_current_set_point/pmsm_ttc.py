from .torque_to_current_set_point import TorqueToCurrentSetPoint


class PMSMTorqueToCurrent(TorqueToCurrentSetPoint):

    def _torque_to_current(self, state, reference):
        pass