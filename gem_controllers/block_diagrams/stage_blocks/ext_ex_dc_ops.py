from control_block_diagram.components import Box, Connection, Circle
from control_block_diagram.predefined_components import Multiply, Divide


def ext_ex_dc_ops(start, control_task):
    inp = start.add_x(1) if control_task == 'TC' else start.add_x(1.5)
    Circle(inp, radius=0.05, fill='black')
    box_abs = Box(inp.add(1, 1), size=(0.8, 0.8), text=r'|x|')
    Connection.connect(inp, box_abs.input_left[0], start_direction='north')

    if control_task == 'TC':
        Connection.connect(start, inp, text=r'$T^{*}$', text_align='left',
                           text_position='start', arrow=False)

    multiply = Multiply(box_abs.position.add_x(1.5), size=(0.8, 0.8), inputs=dict(left=1, top=1))
    Connection.connect(box_abs.output_right, multiply.input_left)
    box_rl = Box(multiply.position.add_y(1.2), size=(1.5, 0.8), text=r"$\sqrt{\frac{R_a}{R_e}}L'_e$",
                 outputs=dict(bottom=1))
    Connection.connect(box_rl.output_bottom, multiply.input_top)
    box_sqrt = Box(multiply.position.add_x(1.5), size=(0.8, 0.8), text=r'$\sqrt{x}$')
    Connection.connect(multiply.output_right, box_sqrt.input_left)

    divide_1 = Divide(multiply.position.sub_y(2.3), size=(0.8, 1.2), input_space=0.6)
    Connection.connect(inp, divide_1.input_left[0], start_direction='south')
    box_le = Box(divide_1.input_left[1].sub_x(1), size=(0.8, 0.8), text=r"$L'_e$")
    Connection.connect(box_le.output_right[0], divide_1.input_left[1])
    divide_2 = Divide(divide_1.output_right[0].add(3, 0.3), size=(0.8, 1.2), input_space=0.6)
    Connection.connect(divide_1.output_right[0], divide_2.input_left[1])
    con_sqrt = Connection.connect(box_sqrt.output_right[0], box_sqrt.output_right[0].add_x(2), arrow=False)
    Connection.connect_to_line(con_sqrt, divide_2.input_left[0].sub_x(0.5), arrow=False)
    Connection.connect(divide_2.input_left[0].sub_x(0.5), divide_2.input_left[0])

    inputs = dict(t_ref=[inp, dict(text=r'$T^{*}$', arrow=False)])
    outputs = dict(i_e_ref=con_sqrt.end, i_a_ref=divide_2.output_right[0])
    connect_to_lines = dict()
    connections = dict()
    start = con_sqrt.end

    return start, inputs, outputs, connect_to_lines, connections
