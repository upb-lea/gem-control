from control_block_diagram.components import Box, Connection
from control_block_diagram.predefined_components import Limit


def series_dc_ops(start, control_task):
    space = 1 if control_task == 'TC' else 2.2
    box_torque = Box(start.add_x(space), size=(0.8, 0.8), text=r"$\frac{1}{L'_{\mathrm{e}}}$")

    box_sqrt = Box(box_torque.output_right[0].add_x(1), size=(0.8, 0.8), text=r'$\sqrt{\mathrm{x}}$')
    Connection.connect(box_torque.output_right, box_sqrt.input_left)

    limit = Limit(box_sqrt.output_right[0].add_x(1), size=(1, 1))
    Connection.connect(box_sqrt.output_right, limit.input_left)

    if control_task == 'TC':
        Connection.connect(start, box_torque.input_left[0], text=r'$T^{*}$', text_align='left',
                           text_position='start')

    inputs = dict(t_ref=[box_torque.input_left[0], dict(text=r'$T^{*}$')])
    outputs = dict(i_ref=limit.output_right[0])
    connect_to_lines = dict()
    connections = dict()

    start = limit.position

    return start, inputs, outputs, connect_to_lines, connections
