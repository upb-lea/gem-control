from .emf_feedforward import EMFFeedforward


class EMFFeedforwardInd(EMFFeedforward):
    def __init__(self):
        super().__init__()

    def __call__(self, state, reference):
        return super().__call__(state, reference)

    def tune(self, env, env_id, **_):
        super().tune(env, env_id, **_)

    def reset(self):
        super().reset()
