from gem_controllers.stages.stage import Stage


class OperationPointSelection(Stage):

    def __call__(self, state, reference):
        return self._select_operating_point(state, reference)

    def _select_operating_point(self, state, reference):
        raise NotImplementedError

    def tune(self, env, env_id, current_safety_margin=0.2, **_):
        pass
