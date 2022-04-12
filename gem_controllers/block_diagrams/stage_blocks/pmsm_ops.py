from control_block_diagram.components import Box, Connection, Text, Point, Circle, Path
from control_block_diagram.predefined_components import Add, Divide, IController, Limit


class PsiOptBox(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bx = 0.1
        by = 0.15
        Connection.connect(self.bottom_left.add(self._size_x * bx, self._size_y * by),
                           self.bottom_right.add(-self._size_x * bx, self._size_y * by))
        Connection.connect(self.bottom.add_y(self._size_y * by), self.top.sub_y(self._size_y * by))
        Path([self.top_left.add(self._size_x * bx, -self._size_y * (0.1 + by)),
              self.bottom.add_y(self._size_y * (0.2 + by)),
              self.top_right.sub(self._size_x * bx, self._size_y * (0.1 + by))],
             angles=[{'in': 180, 'out': 0}, {'in': 180, 'out': 0}], arrow=False)


class TMaxPsiBox(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bx = 0.1 * self._size_x
        by = 0.15 * self._size_y
        scale = 1.5

        Connection.connect(self.bottom_left.add(bx, by), self.top_left.add(bx, -by))
        Connection.connect(self.left.add_x(bx), self.right.sub_x(bx))
        Path([self.left.add_x(bx), self.top_right.sub(scale * bx, scale * by)], arrow=False,
             angles=[{'in': 180, 'out': 35}])
        Path([self.left.add_x(bx), self.bottom_right.add(-scale * bx, scale * by)], arrow=False,
             angles=[{'in': 180, 'out': -35}])


def pmsm_ops(start, control_task):

    # Torque Controller
    if control_task == 'TC':
        Connection.connect(start, start.add_x(1), text='$T^{*}$', text_position='start', text_align='left', arrow=False)

    box_limit = Limit(start.add_x(6), inputs=dict(left=1, bottom=1), size=(1, 1))
    box_psi_opt = PsiOptBox(start.add(2, -1.7), size=(1.2, 1))
    Text(position=box_psi_opt.top.add_y(0.25), text=r'$\Psi^{*}_{\mathrm{opt}}(T^{*})$')
    box_min = Box(box_psi_opt.position.add(1.5, -1.3), inputs=dict(left=2, left_space=0.5), size=(0.8, 1), text='min')
    box_t_max = TMaxPsiBox(box_psi_opt.position.add_x(3.1), size=(1.2, 1))
    Text(position=box_t_max.top.add_y(0.25), text=r'$T_{\mathrm{max}}(\Psi)$')
    con_torque = Connection.connect(start.add_x(1), box_limit.input_left[0])
    Connection.connect(start.add_x(1), box_psi_opt.input_left[0], start_direction='south')
    Circle(start.add_x(1), radius=0.05, fill='black')
    Connection.connect(box_psi_opt.output_right[0], box_min.input_left[0])
    Connection.connect(box_min.output_right[0].add_x(0.3), box_t_max.input_left[0], start_direction='north')
    Circle(box_min.output_right[0].add_x(0.3), radius=0.05, fill='black')
    Connection.connect(box_t_max.output_right[0], box_limit.input_bottom[0])
    box_f_psi_t = Box(box_limit.position.add(2.2, -1.5), size=(1.3, 3.5), inputs=dict(left=2, left_space=3),
                      outputs=dict(right=3, right_space=1), text=r'\textbf{f}($\Psi$, $T$)')

    Connection.connect(box_min.output_right[0], box_f_psi_t.input_left[1], text=r'$\Psi^{*}_{\mathrm{lim}}$')
    Connection.connect(box_limit.output_right[0], box_f_psi_t.input_left[0], text=r'$T^{*}_{\mathrm{lim}}$')

    # Moulation Controller
    add_psi = Add(box_min.input_left[1].sub_x(1))
    Connection.connect(add_psi.output_right[0], box_min.input_left[1], text=r'$\Psi_{\mathrm{lim}}$', text_align='top',
                       distance_y=0.25)
    limit_modulation = Limit(add_psi.input_left[0].sub_x(1.5), size=(1, 1))
    i_controller = IController(limit_modulation.input_left[0].sub_x(1), size=(1.2, 1), text='Modulation\nController')
    Connection.connect(i_controller.output_right, limit_modulation.input_left)
    Connection.connect(limit_modulation.output_right[0], add_psi.input_left[0], text=r'$\Delta \Psi$', distance_y=0.25)
    add_a = Add(i_controller.position.sub_x(1.5))
    Connection.connect(add_a.output_right[0], i_controller.input_left[0])
    box_a_max = Box(add_a.input_left[0].sub_x(1.3), size=(1.5, 0.8), text=r'$a_{\mathrm{max}} \cdot k$')
    Connection.connect(box_a_max.output_right[0], add_a.input_left[0], text='$a^{*}$')
    box_abs = Box(add_a.position.sub_y(1.2), size=(0.8, 0.8), text=r'|\textbf{x}|', inputs=dict(bottom=1),
                  outputs=dict(top=1))
    con_a = Connection.connect(box_abs.output_top[0], add_a.input_bottom[0], text='$-$', text_align='right',
                               text_position='end', move_text=(-0.1, -0.2))
    Text(position=Point.get_mid(*con_a.points).sub_x(0.25), text='$a$')

    div_a = Divide(box_abs.input_bottom[0].sub_y(1), size=(1, 0.5), inputs='bottom', input_space=0.5)
    Connection.connect(div_a.input_bottom[0].sub_y(0.7), div_a.input_bottom[0], text=r'$\mathbf{u^{*}_{\mathrm{dq}}}$',
                       text_position='start', text_align='bottom')
    Connection.connect(div_a.input_bottom[1].sub_y(0.7), div_a.input_bottom[1],
                       text=r'$\frac{u_{\mathrm{\mbox{\fontsize{3}{4}\selectfont DC}}}}{2}$', text_position='start',
                       text_align='bottom')
    Connection.connect(div_a.output_top[0], box_abs.input_bottom[0])

    div_psi = Divide(add_psi.input_bottom[0].sub_y(2), size=(1, 0.5), inputs='bottom', input_space=0.5)
    Connection.connect(div_psi.output_top[0], add_psi.input_bottom[0], text=r'$\Psi_{\mathrm{max}}$',
                       text_align='right', distance_x=0.5)
    Connection.connect(div_psi.input_bottom[0].sub_y(0.7), div_psi.input_bottom[0],
                       text=r'$\frac{u_{\mathrm{\mbox{\fontsize{3}{4}\selectfont DC}}}}{\sqrt{3}}$',
                       text_position='start', text_align='bottom')

    limit = Limit(Point.get_mid(box_f_psi_t.output_right[0], box_f_psi_t.output_right[1]).add_x(1), size=(1, 1.5),
                  inputs=dict(left=2, left_space=1), outputs=dict(right=2, right_space=1))
    Connection.connect(box_f_psi_t.output_right, limit.input_left)

    # In-/ Outputs
    inputs = dict(t_ref=[con_torque.start, dict(arrow=False, text=r'$T^{*}$')],
                  omega=[div_psi.input_bottom[1], dict(text=r'$\omega_{\mathrm{el}}$', move_text=(3, 0))])
    outputs = dict(i_d_ref=limit.output_right[0], i_q_ref=limit.output_right[1])
    connect_to_lines = dict()
    connections = dict()
    start = limit.output_right[0]

    return start, inputs, outputs, connect_to_lines, connections
