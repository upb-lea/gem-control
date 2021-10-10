import gym_electric_motor.core
import numpy as np

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

    def tune(self, env: gym_electric_motor.core.ElectricMotorEnvironment, env_id: str, margin: float = 0.0):
        pass
