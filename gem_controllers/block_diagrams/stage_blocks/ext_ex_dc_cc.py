from control_block_diagram.components import Box, Connection


def ext_ex_dc_cc(emf_feedforward):
    def cc_ext_ex_dc(start, control_task):
        if emf_feedforward:
            box = Box(start.add_x(3), (3, 1.5), text=r'Current Controller\nExt Ex DC\nEMF Feedforward')
        else:
            box = Box(start.add_x(3), (2, 1.5), text=r'Current\nController\nExt Ex DC')
        Connection.connect(start, box.input_left[0])
        output = box.output_right[0]
        return output
    return cc_ext_ex_dc
