from .emf_feedforward import EMFFeedforward
from .. import parameter_reader as reader
import gem_controllers as gc
import numpy as np


class EMFFeedforwardEESM(EMFFeedforward):
    """
    This class extends the functions of the EMFFeedforward class to decouple the dq-components of the induction motor.
    """
    def __init__(self):
        super().__init__()
        self._l_e = None
        self._i_e_idx = None

    def __call__(self, state, reference):
        self.psi = np.array([self._l_e * state[self._i_e_idx], 0, 0])
        return super().__call__(state, reference)

    def tune(self, env, env_id, **_):
        super().tune(env, env_id, **_)
        motor_type = gc.utils.get_motor_type(env_id)
        self._l_e = reader.l_reader[motor_type](env)[2]
        self._i_e_idx = env.state_names.index('i_e')
