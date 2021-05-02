from .gem_controller import GemController


class FeedforwardController(GemController):

    def __init__(self):
        super().__init__()
        self._stages = []

    def reset(self):
        for stage in self._stages:
            stage.reset()

    def control(self, state, reference):
        for stage in self._stages:
            reference = stage(state, reference)
        return reference
