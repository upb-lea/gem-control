import numpy as np

from .stage import Stage
from ..utils import non_parameterized


class DiscOutputStage(Stage):

    @property
    def output_stage(self):
        return self._output_stage

    @output_stage.setter
    def output_stage(self, value):
        assert value in [self.to_b6_discrete, self.to_multi_discrete, self.to_discrete]
        self._output_stage = value

    def __init__(self):
        super().__init__()
        self.high_level = 0.0
        self.low_level = 0.0
        self.high_action = 0
        self.low_action = 0
        self.idle_action = 0
        self._output_stage = non_parameterized

    def __call__(self, state, reference):
        self._output_stage(self.to_action(state, reference))

    @staticmethod
    def to_discrete(multi_discrete_action):
        return multi_discrete_action[0]

    @staticmethod
    def to_b6_discrete(multi_discrete_action):
        raise NotImplementedError

    @staticmethod
    def to_multi_discrete(multi_discrete_action):
        return multi_discrete_action

    def to_action(self, state, reference):
        conditions = [reference <= self.low_level, reference >= self.high_level]
        return np.select(conditions, [self.low_action, self.high_action], default=self.idle_action)
