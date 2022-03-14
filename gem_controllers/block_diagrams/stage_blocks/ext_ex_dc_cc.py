from control_block_diagram.components import Box, Connection, Point
from control_block_diagram.predefined_components import Add, PIController


def ext_ex_dc_cc(emf_feedforward):
    def cc_ext_ex_dc(start, control_task):
        space = 1
        add_i_e = Add(start.add_x(space))
        start_i_a = start.sub_y(2)
        add_i_a = Add(start_i_a.add_x(space))

        if control_task == 'CC':
            Connection.connect(start, add_i_e.input_left[0], text=r'$i^{*}_{\mathrm{e}}$', text_align='left',
                               text_position='start')
            Connection.connect(start_i_a, add_i_a.input_left[0], text=r'$i^{*}_{\mathrm{a}}$', text_align='left',
                               text_position='start')
        pi_i_e = PIController(add_i_e.position.add_x(1.5), text='Current\nController')
        Connection.connect(add_i_e.output_right, pi_i_e.input_left)

        pi_i_a = PIController(add_i_a.position.add_x(1.5))
        Connection.connect(add_i_a.output_right, pi_i_a.input_left)

        inputs = dict(i_e_ref=[add_i_e.input_left[0], dict(text=r'$i^{*}_{\mathrm{e}}$', move_text=(-0.1, 0.1))],
                      i_a_ref=[add_i_a.input_left[0], dict(text=r'$i^{*}_{\mathrm{a}}$', move_text=(-0.1, 0.1))],
                      i_a=[add_i_a.input_bottom[0], dict(text=r'-', move_text=(-0.2, -0.2), text_position='end',
                                                         text_align='right')],
                      i_e=[add_i_e.input_bottom[0], dict(text=r'-', move_text=(-0.2, -0.2), text_position='end',
                                                         text_align='right')])
        connect_to_lines = dict()

        if emf_feedforward:
            add_psi = Add(pi_i_a.position.add_x(2))
            Connection.connect(pi_i_a.output_right, add_psi.input_left, text=r'$\Delta u_{\mathrm{a}}$',
                               distance_y=0.25)
            box_psi = Box(add_psi.position.sub_y(2), size=(0.8, 0.8), text=r"$\Psi'_{\mathrm{e}}$",
                          inputs=dict(bottom=1), outputs=dict(top=1))
            Connection.connect(box_psi.output_top, add_psi.input_bottom, text=r'$u_0$', text_position='end',
                               text_align='right', move_text=(0.1, -0.2))
            pwm_a = Box(add_psi.position.add_x(1.8), size=(1.2, 0.8), text='PWM')
            Connection.connect(add_psi.output_right, pwm_a.input_left, text=r'$u_{\mathrm{a}}$', distance_y=0.25)
            if control_task in ['CC', 'TC']:
                inputs['omega'] = [box_psi.input_bottom[0], dict()]
            elif control_task == 'SC':
                connect_to_lines['omega'] = [box_psi.input_bottom[0], dict(section=0)]
        else:
            pwm_a = Box(pi_i_a.position.add_x(2), size=(1.2, 0.8), text='PWM')
            Connection.connect(pi_i_e.output_right, pwm_a.input_left, text=r'$u_{\mathrm{a}}$', distance_y=0.25)

        pwm_e = Box(Point.merge(pwm_a.position, pi_i_e.position), size=(1.2, 0.8), text='PWM')
        Connection.connect(pi_i_e.output_right, pwm_e.input_left, text=r'$u_{\mathrm{e}}$', distance_y=0.25)

        start = pwm_e.position
        outputs = dict(u_e=pwm_e.output_right[0], u_a=pwm_a.output_right[0])

        connections = dict()

        return start, inputs, outputs, connect_to_lines, connections
    return cc_ext_ex_dc
