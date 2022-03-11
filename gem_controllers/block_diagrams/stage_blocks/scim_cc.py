from control_block_diagram.components import Box, Connection


def scim_cc(emf_feedforward):
    def cc_scim(start, control_task):
        if emf_feedforward:
            box = Box(start.add_x(3), (3, 1.5), text=r'Current Controller\nSCIM\nEMF Feedforward')
        else:
            box = Box(start.add_x(3), (2, 1.5), text=r'Current\nController\nSCIM')
        Connection.connect(start, box.input_left[0])
        output = box.output_right[0]
        return output
    return cc_scim
