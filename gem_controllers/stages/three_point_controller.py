import numpy as np

from .stage import Stage


class ThreePointController(Stage):

    @property
    def high_action(self):
        return self._high_action

    @high_action.setter
    def high_action(self, value):
        self._high_action = np.array(value)

    @property
    def low_action(self):
        return self._low_action

    @low_action.setter
    def low_action(self, value):
        self._low_action = np.array(value)

    @property
    def idle_action(self):
        return self._idle_action

    @idle_action.setter
    def idle_action(self, value):
        self._idle_action = np.array(value)

    @property
    def referenced_state_indices(self):
        return self._referenced_state_indices

    @referenced_state_indices.setter
    def referenced_state_indices(self, value):
        self._referenced_state_indices = np.array(value)

    @property
    def hysteresis(self):
        return self._hysteresis

    @hysteresis.setter
    def hysteresis(self, value):
        self._hysteresis = np.array(value)

    def __init__(self):
        super().__init__()
        self._hysteresis = np.array([])
        self._referenced_state_indices = np.array([])
        self._idle_action = 0.0
        self._high_action = np.array([])
        self._low_action = np.array([])

    def __call__(self, state, reference):
        referenced_states = state[self._referenced_state_indices]
        high_actions = referenced_states + self._hysteresis < reference
        low_actions = referenced_states - self._hysteresis > reference
        return np.select([low_actions, high_actions], [self._low_action, self._high_action], default=self._idle_action)
