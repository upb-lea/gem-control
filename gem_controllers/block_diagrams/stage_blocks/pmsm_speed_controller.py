from control_block_diagram.components import Box, Connection
from control_block_diagram.predefined_components import Add, PIController


def pmsm_speed_controller(start, control_task):
    space = 1 if control_task == 'SC' else 1.5
    add_omega = Add(start.add_x(space))
    Connection.connect(add_omega.input_bottom[0].sub_y(1), add_omega.input_bottom[0], text=r'$\omega_{\mathrm{me}}$',
                       text_align='bottom', text_position='start')
    if control_task == 'SC':
        Connection.connect(start, add_omega.input_left[0], text=r'$\omega^{*}$', text_align='left',
                           text_position='start')
    pi_omega = PIController(add_omega.position.add_x(1.5), text='Speed\nController')
    Connection.connect(add_omega.output_right, pi_omega.input_left)

    start = pi_omega.output_right[0]
    inputs = dict(omega_ref=[add_omega.input_left[0], dict(text=r'$\omega^{*}$')])
    outputs = dict(t_ref=pi_omega.output_right[0])
    connect_to_lines = dict()
    connections = dict()

    return start, inputs, outputs, connect_to_lines, connections