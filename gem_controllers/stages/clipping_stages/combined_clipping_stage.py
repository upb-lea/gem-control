import numpy as np
from typing import Tuple

import gem_controllers as gc
from . import ClippingStage


class CombinedClippingStage(ClippingStage):
    """This clipping stage combines the absolute clipping and the squared clipping."""

    @property
    def clipping_difference(self) -> np.ndarray:
        """Difference between the reference and the clipped reference"""
        return self._clipping_difference

    def __init__(self, control_task='CC'):
        self._action_range_absolute = np.array([]), np.array([])
        self._limit_squred_clipping = np.array([])
        self._clipping_difference = np.array([])
        self._control_task = control_task
        self._absolute_clipped_states = np.array([])
        self._squared_clipped_states = np.array([])
        self._margin = None

    def __call__(self, state, reference):
        clipped = np.zeros(np.size(self._squared_clipped_states) + np.size(self._absolute_clipped_states))
        relative_reference_length = np.sum((reference[self._squared_clipped_states]/self._limit_squred_clipping)**2)
        relative_maximum = 1 - self._margin
        clipped[self._squared_clipped_states] = reference[self._squared_clipped_states] \
            if relative_reference_length < relative_maximum**2 \
            else reference[self._squared_clipped_states] / relative_reference_length * relative_maximum

        clipped[self._absolute_clipped_states] = np.clip(reference[self._absolute_clipped_states],
                                                         self._action_range_absolute[0], self._action_range_absolute[1])
