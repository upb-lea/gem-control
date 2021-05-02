from .feedforward_controller import FeedforwardController
from .stages.stage import Stage


class FieldOrientedCurrentController(FeedforwardController):

    @property
    def output_stage(self):
        return self._output_stage

    @output_stage.setter
    def output_stage(self, value):
        assert isinstance(value, Stage)
        self._output_stage = value

    @property
    def current_controller(self):
        return self._current_controller

    @property
    def feedforward(self):
        return self._feedforward

    def __init__(self):
        super().__init__()
        self._feedforward = None
        self._output_stage = None
        self._current_controller = None
