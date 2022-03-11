from control_block_diagram.components import Point, Box, Connection
from control_block_diagram.predefined_components import DqToAlphaBetaTransformation,\
     AbcToAlphaBetaTransformation, AlphaBetaToDqTransformation, Add, PIController, Multiply


def pmsm_cc(emf_feedforward):
    def cc_pmsm(start, control_task):
        space = 1 if control_task == 'CC' else 3
        add_i_sd = Add(start.add_x(space))
        add_i_sq = Add(add_i_sd.position.sub(0.5, 1))

        if control_task == 'CC':
            Connection.connect(add_i_sd.input_left[0].sub_x(space), add_i_sd.input_left[0],
                               text=r'$i^{*}_{\mathrm{sd}}$', text_position='start', text_align='left')
            Connection.connect(add_i_sq.input_left[0].sub_x(space - 0.5), add_i_sq.input_left[0],
                               text=r'$i^{*}_{\mathrm{sq}}$', text_position='start', text_align='left')

        pi_i_sd = PIController(add_i_sd.position.add_x(1.2), size=(1, 0.8), input_number=1, output_number=1)
        pi_i_sq = PIController(Point.merge(pi_i_sd.position, add_i_sq.position), size=(1, 0.8), input_number=1,
                               output_number=1)

        Connection.connect(add_i_sd.output_right, pi_i_sd.input_left)
        Connection.connect(add_i_sq.output_right, pi_i_sq.input_left)

        add_u_sd = Add(pi_i_sd.position.add_x(2))
        add_u_sq = Add(pi_i_sq.position.add_x(1.2))

        Connection.connect(pi_i_sd.output_right[0], add_u_sd.input_left[0], text=r'$\Delta u^{*}_{\mathrm{sd}}$',
                           distance_y=0.28)
        Connection.connect(pi_i_sq.output_right[0], add_u_sq.input_left[0], text=r'$\Delta u^{*}_{\mathrm{sq}}$',
                           distance_y=0.4, move_text=(0.25, 0))

        dq_to_alpha_beta = DqToAlphaBetaTransformation(Point.get_mid(add_u_sd.position, add_u_sq.position).add_x(2),
                                                       input_space=1)

        Connection.connect(add_u_sd.output_right[0], dq_to_alpha_beta.input_left[0], text=r'$u^{*}_{\mathrm{sd}}$',
                           distance_y=0.28)
        Connection.connect(add_u_sq.output_right[0], dq_to_alpha_beta.input_left[1], text=r'$u^{*}_{\mathrm{sq}}$',
                           distance_y=0.28, move_text=(0.4, 0))

        pwm = Box(dq_to_alpha_beta.position.add_x(2.5), size=(1.5, 1.2), text='PWM',
                  inputs=dict(left=2, left_space=0.6),
                  outputs=dict(right=3, right_space=0.3))

        Connection.connect(dq_to_alpha_beta.output_right, pwm.input_left,
                           text=[r'$u^*_{\mathrm{s} \upalpha}$', r'$u^*_{\mathrm{s} \upbeta}$'], distance_y=0.25)

        abc_to_alpha_beta = AbcToAlphaBetaTransformation(pwm.position.sub_y(3.5), input='right', output='left')

        alpha_beta_to_dq = AlphaBetaToDqTransformation(
            Point.merge(dq_to_alpha_beta.position, abc_to_alpha_beta.position), input='right', output='left')

        distance = (add_u_sq.position.y - alpha_beta_to_dq.output_left[0].y) / 4

        multiply_u_sq = Multiply(add_u_sq.position.sub_y(distance), outputs=dict(top=1))
        Connection.connect(multiply_u_sq.output_top, add_u_sq.input_bottom)

        add_psi_p = Add(multiply_u_sq.position.sub_y(distance), outputs=dict(top=1))
        Connection.connect(add_psi_p.output_top, multiply_u_sq.input_bottom)
        Connection.connect(add_psi_p.input_left[0].sub_x(0.3), add_psi_p.input_left[0], text=r'$\Psi_{\mathrm{p}}$',
                           text_position='start', text_align='left', distance_x=0.25)

        box_ls_1 = Box(add_psi_p.position.sub_y(distance), size=(0.6, 0.6), inputs=dict(bottom=1), outputs=dict(top=1),
                       text=r'$L_{\mathrm{s}}$')
        Connection.connect(box_ls_1.output_top, add_psi_p.input_bottom)

        multiply_u_sd = Multiply(Point.merge(add_u_sd.position, multiply_u_sq.position), outputs=dict(top=1))
        Connection.connect(multiply_u_sd.output_top, add_u_sd.input_bottom, text=r'-', text_position='end',
                           text_align='right', move_text=(-0.2, -0.2))
        Connection.connect(multiply_u_sd.input_left[0].sub_x(0.3), multiply_u_sd.input_left[0])

        box_ls_2 = Box(Point.merge(multiply_u_sd.position, box_ls_1.position), size=(0.6, 0.6), inputs=dict(bottom=1),
                       outputs=dict(top=1), text=r'$L_{\mathrm{s}}$')
        Connection.connect(box_ls_2.output_top, multiply_u_sd.input_bottom)

        con_3 = Connection.connect(alpha_beta_to_dq.output_left[0], add_i_sd.input_bottom[0], text=r'-',
                                   text_position='end',
                                   text_align='right', move_text=(-0.2, -0.2))
        Connection.connect_to_line(con_3, box_ls_1.input_bottom[0])

        con_4 = Connection.connect(alpha_beta_to_dq.output_left[1], add_i_sq.input_bottom[0], text=r'-',
                                   text_position='end',
                                   text_align='right', move_text=(-0.2, -0.2))
        Connection.connect_to_line(con_4, box_ls_2.input_bottom[0])

        box_d_dt = Box(Point.merge(alpha_beta_to_dq.position, start.sub_y(6.57020066645696)).sub_x(2), size=(1, 0.8),
                       text=r'$\mathrm{d} / \mathrm{d}t$', inputs=dict(right=1), outputs=dict(left=1))

        Connection.connect(box_d_dt.output_left, multiply_u_sq.input_left, space_y=1, text=r'$\omega_{\mathrm{el}}$',
                           move_text=(0, 2), text_align='left', distance_x=0.3)

        Connection.connect(abc_to_alpha_beta.output, alpha_beta_to_dq.input_right,
                           text=[r'$i_{\mathrm{s} \upalpha}$', r'$i_{\mathrm{s} \upbeta}$'])

        add = Add(Point.get_mid(dq_to_alpha_beta.position, alpha_beta_to_dq.position), inputs=dict(bottom=1, right=1),
                  outputs=dict(top=1))

        Connection.connect(alpha_beta_to_dq.output_top, add.input_bottom, text=r'$\varepsilon_{\mathrm{el}}$',
                           text_align='right', move_text=(0, -0.1))
        Connection.connect(add.output_top, dq_to_alpha_beta.input_bottom)

        box_t_a = Box(add.position.add_x(1.5), size=(1, 0.8), text=r'$1.5 T_{\mathrm{s}}$', inputs=dict(right=1),
                      outputs=dict(left=1))

        Connection.connect(box_t_a.output, add.input_right, text=r'$\Delta \varepsilon$')
        Connection.connect(box_t_a.input[0].add_x(0.5), box_t_a.input[0], text=r'$\omega_{\mathrm{el}}$',
                           text_position='start', text_align='right', distance_x=0.3)

        start = pwm.position
        inputs = dict(i_sd=[add_i_sd.input_left[0], dict(text=r'$i^{*}_{\mathrm{sd}}$')],
                      i_sq=[add_i_sq.input_left[0], dict(text=r'$i^{*}_{\mathrm{sq}}$')],
                      epsilon=[box_d_dt.input_right[0], dict()])

        outputs = dict(S=pwm.output_right)
        connect_to_line = dict(epsilon=[alpha_beta_to_dq.input_bottom[0], dict(text=r'$\varepsilon_{\mathrm{el}}$',
                                                                               text_position='middle',
                                                                               text_align='right')],
                               i=[abc_to_alpha_beta.input_right, dict(draw=0.1, fill=False,
                                                                      text=[r'$\mathbf{i}_{\mathrm{s a,b,c}}$', '', ''])])
        connections = dict()

        return start, inputs, outputs, connect_to_line, connections

    return cc_pmsm
