import numpy as np
import gym_electric_motor as gem

import gem_controllers as gc


class CurrentController(gc.GemController):

    def control(self, state, reference):
        raise NotImplementedError

    def tune(self, env, env_id):
        raise NotImplementedError

    @property
    def voltage_reference(self) -> np.ndarray:
        raise NotImplementedError

    @property
    def t_n(self) -> np.ndarray:
        raise NotImplementedError
