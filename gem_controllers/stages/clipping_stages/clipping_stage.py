import numpy as np

import gem_controllers as gc
from ..stage import Stage


class ClippingStage(Stage):

    @property
    def clipping_difference(self) -> np.ndarray:
        raise NotImplementedError

    @property
    def clipped(self) -> np.ndarray:
        return self.clipping_difference != 0.0

    def __call__(self, state: np.ndarray, reference: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def tune(self, env, env_id, margin=0.0):
        pass
