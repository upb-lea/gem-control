import numpy as np

import gym_electric_motor as gem
import gem_controllers as gc
from gem_controllers.visualization import *


class TorqueController(gc.GemController):

    @property
    def torque_to_current_stage(self) -> gc.stages.OperationPointSelection:
        return self._operation_point_selection

    @torque_to_current_stage.setter
    def torque_to_current_stage(self, value: gc.stages.OperationPointSelection):
        self._operation_point_selection = value

    @property
    def current_controller(self) -> gc.CurrentController:
        return self._current_controller

    @current_controller.setter
    def current_controller(self, value: gc.CurrentController):
        self._current_controller = value

    @property
    def current_reference(self) -> np.ndarray:
        return self._current_reference

    @property
    def clipping_stage(self) -> gc.stages.clipping_stages.ClippingStage:
        return self._clipping_stage

    @clipping_stage.setter
    def clipping_stage(self, value: gc.stages.clipping_stages.ClippingStage):
        self._clipping_stage = value

    @property
    def t_n(self):
        return self._current_controller.t_n

    def __init__(
            self,
            env: (gem.core.ElectricMotorEnvironment, None) = None,
            env_id: (str, None) = None,
            current_controller: (gc.CurrentController, None) = None,
            torque_to_current_stage: (gc.stages.OperationPointSelection, None) = None,
            clipping_stage: (gc.stages.clipping_stages.ClippingStage, None) = None
    ):
        super().__init__()

        self._operation_point_selection = torque_to_current_stage
        if env_id is not None and torque_to_current_stage is None:
            self._operation_point_selection = gc.stages.torque_to_current_function[gc.utils.get_motor_type(env_id)]()
        self._current_controller = current_controller
        if env_id is not None and current_controller is None:
            self._current_controller = gc.PICurrentController(env, env_id)
        if env_id is not None and clipping_stage is None:
            if gc.utils.get_motor_type(env_id) in gc.parameter_reader.dc_motors:
                self._clipping_stage = gc.stages.clipping_stages.AbsoluteClippingStage('TC')
            else:  # motor in ac_motors
                self._clipping_stage = gc.stages.clipping_stages.SquaredClippingStage('TC')
        self._current_reference = np.array([])

    def tune(self, env, env_id, current_safety_margin=0.2, tune_current_controller=True, **kwargs):
        if tune_current_controller:
            self._current_controller.tune(env, env_id, **kwargs)
        self._clipping_stage.tune(env, env_id, margin=current_safety_margin)
        self._operation_point_selection.tune(env, env_id, current_safety_margin)

    def torque_control(self, state, reference):
        self._current_reference = self._operation_point_selection(state, reference)
        return self._current_reference

    def control(self, state, reference):
        self._current_reference = self.torque_control(state, reference)
        self._current_reference = self._clipping_stage(state, self._current_reference)
        reference = self._current_controller.current_control(state, self._current_reference)
        return reference

    def visualize(self, start: Point = Point(0, 0)):
        stage_box = StageBox('Torque')
        input_sb = start.input
        stage_box.append(input_sb)

        tb = TextBox(start, (2.5, 1.5), Text(['Torque', 'Controller']), fill='white', draw='black')
        stage_box.append(tb)

        circle = Circle(tb.end, 0.2, text=Text('+'))
        stage_box.append(circle)

        connection = Connection.connect(tb.right, circle.left)
        connection.add_text(text='test', text_position='middle', text_align='bottom')
        connection.add_text('+', 'end', 'top_left')
        stage_box.append(connection)

        tb_2 = TextBox(circle.end, (2.5, 1.5), Text(['Torque', 'Controller', '2']), fill='white', draw='black')
        stage_box.append(tb_2)

        con1 = Connection.connect(circle.right, tb_2.left)
        stage_box.append(con1)

        con = Connection.connect(tb_2.bottom, circle.bottom)
        con.add_text(text='-', text_position='end', text_align='right_bottom')
        con.add_text('$i_{sd}$', text_position='middle', text_align='bottom')
        stage_box.append(con)

        connection = Connection.connect(tb.top, tb_2.top, arrow=False)
        connection.add_text(text='Test 2', text_position='middle', text_align='top')
        stage_box.append(connection)
        connection = Connection.connect(tb_2.right, tb_2.end)
        stage_box.append(connection)

        return [stage_box] + self._current_controller.visualize(tb_2.end)

    def reset(self):
        self._current_controller.reset()
        self._operation_point_selection.reset()
        self._clipping_stage.reset()
