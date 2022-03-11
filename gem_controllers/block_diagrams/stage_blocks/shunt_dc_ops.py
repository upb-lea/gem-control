from control_block_diagram.components import Box, Connection


def shunt_dc_ops(start, control_task):
    space = 1 if control_task == 'TC' else 2.2
    box_torque = Box(start.add_x(space), size=(0.8, 0.8), text=r"$\frac{1}{\Psi'_{\mathrm{E}}}$")
    if control_task == 'TC':
        Connection.connect(start, box_torque.input_left[0], text=r'$T^{*}$', text_align='left',
                           text_position='start')

    inputs = dict(t_ref=[box_torque.input_left[0], dict(text=r'$T^{*}$')])
    outputs = dict(i_ref=box_torque.output_right[0])
    connect_to_lines = dict()
    connections = dict()

    start = box_torque.position

    return start, inputs, outputs, connect_to_lines, connections
