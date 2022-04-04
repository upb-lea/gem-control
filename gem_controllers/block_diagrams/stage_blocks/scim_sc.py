from control_block_diagram.components import Box, Connection
from control_block_diagram.predefined_components import Add, PIController, Limit


def scim_speed_controller(start, control_task):
    space = 1 if control_task == 'SC' else 1.5
    add_omega = Add(start.add_x(space))
    if control_task == 'SC':
        Connection.connect(start, add_omega.input_left[0], text=r'$\omega^{*}$', text_align='left',
                           text_position='start')

    pi_omega = PIController(add_omega.position.add_x(1.5), text='Speed\nController')
    Connection.connect(add_omega.output_right, pi_omega.input_left)

    limit = Limit(pi_omega.output_right[0].add_x(1.5), size=(1, 1))
    Connection.connect(pi_omega.output_right[0], limit.input_left[0])

    start = limit.output_right[0].add(0.5, 2)
    inputs = dict(omega_ref=[add_omega.input_left[0], dict(text=r'$\omega^{*}$')],
                  omega_me=[add_omega.input_bottom[0], dict(text='-', text_position='end', text_align='right',
                                                            move_text=(-0.2, -0.2))])
    outputs = dict(t_ref=limit.output_right[0])
    connect_to_lines = dict()
    connections = dict()

    return start, inputs, outputs, connect_to_lines, connections
