import numpy as np

from .p_controller import PController
from .i_controller import IController


class PIController(PController, IController):

    def control(self, state, reference):
        filtered_state = state[self._state_indices]
        action = PController._control(self, filtered_state, reference) \
            + IController._control(self, filtered_state, reference)
        self.integrate(filtered_state, reference)
        return np.clip(action, self._action_range[0], self._action_range[1])

    def tune(self, env, motor_type, action_type, control_task, sub_control_task='CC'):
        pass
