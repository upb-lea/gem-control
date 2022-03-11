from control_block_diagram.components import Box, Connection


def ext_ex_dc_ops(start, control_task):
    box = Box(start.add_x(3), (3.5, 1), text=r'Ext Ex DC Operation\nPoint Selection')
    Connection.connect(start, box.input_left[0])
    output = box.output_right[0]
    return output
