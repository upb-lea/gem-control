from control_block_diagram.components import Point, Box, Connection, Circle
from control_block_diagram.predefined_components import DqToAlphaBetaTransformation, DqToAbcTransformation,\
     AbcToAlphaBetaTransformation, AlphaBetaToDqTransformation, Add, PIController, Multiply, Limit


def pmsm_cc(emf_feedforward):
    """
    Args:
        emf_feedforward: Boolean whether emf feedforward stage is included

    Returns:
        Function to build the PMSM Current Control Block
    """

    def cc_pmsm(start, control_task):
        """
        Function to build the PMSM Current Control Block
        Args:
            start:          Starting Point of the Block
            control_task:   Control task of the controller

        Returns:
            endpoint, inputs, outputs, connection to other lines, connections
        """

        # space to the previous block
        space = 1 if control_task == 'CC' else 1.5

        # Add blocks for the i_sd and i_sq references and states
        add_i_sd = Add(start.add_x(space))
        add_i_sq = Add(add_i_sd.position.sub(0.5, 1))

        if control_task == 'CC':
            # Connections at the inputs
            Connection.connect(add_i_sd.input_left[0].sub_x(space), add_i_sd.input_left[0],
                               text=r'$i^{*}_{\mathrm{sd}}$', text_position='start', text_align='left')
            Connection.connect(add_i_sq.input_left[0].sub_x(space - 0.5), add_i_sq.input_left[0],
                               text=r'$i^{*}_{\mathrm{sq}}$', text_position='start', text_align='left')

        # PI Controllers for the d and q component
        pi_i_sd = PIController(add_i_sd.position.add_x(1.2), size=(1, 0.8), input_number=1, output_number=1,
                               text='Current\nController')
        pi_i_sq = PIController(Point.merge(pi_i_sd.position, add_i_sq.position), size=(1, 0.8), input_number=1,
                               output_number=1)

        # Connection between the add blocks and the PI Controllers
        Connection.connect(add_i_sd.output_right, pi_i_sd.input_left)
        Connection.connect(add_i_sq.output_right, pi_i_sq.input_left)

        # Add blocks for the EMF Feedforward
        add_u_sd = Add(pi_i_sd.position.add_x(2))
        add_u_sq = Add(pi_i_sq.position.add_x(1.2))

        # Connections between the PI Controllers and the Add blocks
        Connection.connect(pi_i_sd.output_right[0], add_u_sd.input_left[0], text=r'$\Delta u^{*}_{\mathrm{sd}}$',
                           distance_y=0.28)
        Connection.connect(pi_i_sq.output_right[0], add_u_sq.input_left[0], text=r'$\Delta u^{*}_{\mathrm{sq}}$',
                           distance_y=0.4, move_text=(0.25, 0))

        # Coordinate transformation from DQ to Abc coordinates
        dq_to_abc = DqToAbcTransformation(Point.get_mid(add_u_sd.position, add_u_sq.position).add_x(2),
                                          input_space=1)

        # Connections between the add blocks and the coordinate transformation
        Connection.connect(add_u_sd.output_right[0], dq_to_abc.input_left[0], text=r'$u^{*}_{\mathrm{sd}}$',
                           distance_y=0.28)
        Connection.connect(add_u_sq.output_right[0], dq_to_abc.input_left[1], text=r'$u^{*}_{\mathrm{sq}}$',
                           distance_y=0.28, move_text=(0.4, 0))

        # Limit of the input voltages
        limit = Limit(dq_to_abc.position.add_x(1.8), size=(1, 1.2), inputs=dict(left=3, left_space=0.3),
                      outputs=dict(right=3, right_space=0.3))

        # Connection between the coordinate transformation and the limit block
        Connection.connect(dq_to_abc.output_right, limit.input_left)

        # Pulse width modulation block
        pwm = Box(limit.position.add_x(2.5), size=(1.5, 1.2), text='PWM', inputs=dict(left=3, left_space=0.3),
                  outputs=dict(right=3, right_space=0.3))

        # Connection between the limit and the PWM block
        Connection.connect(limit.output_right, pwm.input_left,
                           text=[r'$u^*_{\mathrm{s a,b,c}}$', '', ''], distance_y=0.25)

        # Coordinate transformation from ABC to AlphaBeta coordinates
        abc_to_alpha_beta = AbcToAlphaBetaTransformation(pwm.position.sub(1, 3.5), input='right', output='left')

        # Coordinate transformation from AlphaBeta to DQ coordinates
        alpha_beta_to_dq = AlphaBetaToDqTransformation(
            Point.merge(dq_to_abc.position, abc_to_alpha_beta.position), input='right', output='left')

        # Distance of the blocks in the EMF Feedforward path
        distance = (add_u_sq.position.y - alpha_beta_to_dq.output_left[0].y) / 4

        # Multiplications of the EMF Feedforward
        multiply_u_sq = Multiply(add_u_sq.position.sub_y(distance), outputs=dict(top=1))
        multiply_u_sd = Multiply(Point.merge(add_u_sd.position, multiply_u_sq.position), outputs=dict(top=1))

        # Connections between the multiplication and the add blocks
        Connection.connect(multiply_u_sq.output_top, add_u_sq.input_bottom)
        Connection.connect(multiply_u_sd.output_top, add_u_sd.input_bottom, text=r'-', text_position='end',
                           text_align='right', move_text=(-0.2, -0.2))

        # Add block for the permanent flux psi_p
        add_psi_p = Add(multiply_u_sq.position.sub_y(distance), outputs=dict(top=1))

        # Connections of the add block
        Connection.connect(add_psi_p.output_top, multiply_u_sq.input_bottom)
        Connection.connect(add_psi_p.input_left[0].sub_x(0.3), add_psi_p.input_left[0], text=r'$\Psi_{\mathrm{p}}$',
                           text_position='start', text_align='left', distance_x=0.25)

        # Multiplication with the inductances
        box_ls_1 = Box(add_psi_p.position.sub_y(distance), size=(0.6, 0.6), inputs=dict(bottom=1), outputs=dict(top=1),
                       text=r'$L_{\mathrm{d}}$')
        box_ls_2 = Box(Point.merge(multiply_u_sd.position, box_ls_1.position), size=(0.6, 0.6), inputs=dict(bottom=1),
                       outputs=dict(top=1), text=r'$L_{\mathrm{q}}$')

        # Connections from the multiplications
        Connection.connect(box_ls_1.output_top, add_psi_p.input_bottom)
        Connection.connect(multiply_u_sd.input_left[0].sub_x(0.3), multiply_u_sd.input_left[0])
        Connection.connect(box_ls_2.output_top, multiply_u_sd.input_bottom)

        # Connections between the coordinate transformation and the add blocks
        con_3 = Connection.connect(alpha_beta_to_dq.output_left[0], add_i_sd.input_bottom[0], text=r'-',
                                   text_position='end',
                                   text_align='right', move_text=(-0.2, -0.2))
        con_4 = Connection.connect(alpha_beta_to_dq.output_left[1], add_i_sq.input_bottom[0], text=r'-',
                                   text_position='end',
                                   text_align='right', move_text=(-0.2, -0.2))

        # Connections between the previous conncetions and the inductances blocks
        Connection.connect_to_line(con_3, box_ls_1.input_bottom[0])
        Connection.connect_to_line(con_4, box_ls_2.input_bottom[0])

        # Derivation of the angle
        box_d_dt = Box(Point.merge(alpha_beta_to_dq.position, start.sub_y(6.57020066645696)).sub_x(2), size=(1, 0.8),
                       text=r'$\mathrm{d} / \mathrm{d}t$', inputs=dict(right=1), outputs=dict(left=1))

        # Conncetion between the derivation and multiplication block
        con_omega = Connection.connect(box_d_dt.output_left, multiply_u_sq.input_left, space_y=1,
                                       text=r'$\omega_{\mathrm{el}}$', move_text=(0, 2), text_align='left',
                                       distance_x=0.3)

        if control_task == 'SC':
            # Connector at the previous connection
            Circle(con_omega[0].points[1], radius=0.05, fill='black')

        # Conncetion between the coordinate transformations
        Connection.connect(abc_to_alpha_beta.output, alpha_beta_to_dq.input_right,
                           text=[r'$i_{\mathrm{s} \upalpha}$', r'$i_{\mathrm{s} \upbeta}$'])

        # Add block for the advanced angle
        add = Add(Point.get_mid(dq_to_abc.position, alpha_beta_to_dq.position), inputs=dict(bottom=1, right=1),
                  outputs=dict(top=1))

        # Connections of the add block
        Connection.connect(alpha_beta_to_dq.output_top, add.input_bottom, text=r'$\varepsilon_{\mathrm{el}}$',
                           text_align='right', move_text=(0, -0.1))
        Connection.connect(add.output_top, dq_to_abc.input_bottom)

        # Calculate the advanced angle
        box_t_a = Box(add.position.add_x(1.5), size=(1, 0.8), text=r'$1.5 T_{\mathrm{s}}$', inputs=dict(right=1),
                      outputs=dict(left=1))

        # Connections of the advanced angle block
        Connection.connect(box_t_a.output, add.input_right, text=r'$\Delta \varepsilon$')
        Connection.connect(box_t_a.input[0].add_x(0.5), box_t_a.input[0], text=r'$\omega_{\mathrm{el}}$',
                           text_position='start', text_align='right', distance_x=0.3)

        start = pwm.position    # starting point of the next block
        # Inputs of the stage
        inputs = dict(i_d_ref=[add_i_sd.input_left[0], dict(text=r'$i^{*}_{\mathrm{sd}}$', distance_y=0.25)],
                      i_q_ref=[add_i_sq.input_left[0], dict(text=r'$i^{*}_{\mathrm{sq}}$', distance_y=0.25)],
                      epsilon=[box_d_dt.input_right[0], dict()])
        outputs = dict(S=pwm.output_right, omega=con_omega[0].points[1])    # Outputs of the stage
        # Connections to other lines
        connect_to_line = dict(epsilon=[alpha_beta_to_dq.input_bottom[0], dict(text=r'$\varepsilon_{\mathrm{el}}$',
                                                                               text_position='middle',
                                                                               text_align='right')],
                               i=[abc_to_alpha_beta.input_right, dict(radius=0.1, fill=False,
                                                                      text=[r'$\mathbf{i}_{\mathrm{s a,b,c}}$', '',
                                                                            ''])])
        connections = dict()    # Connections

        return start, inputs, outputs, connect_to_line, connections

    return cc_pmsm
