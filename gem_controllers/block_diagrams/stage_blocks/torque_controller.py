from control_block_diagram.components import Box, Connection


def torque_controller(start, control_task):
    box = Box(start.add_x(3), (2, 1), text=r'Torque\nController')
    Connection.connect(start, box.input_left[0])
    output = box.output_right[0]
    return output
