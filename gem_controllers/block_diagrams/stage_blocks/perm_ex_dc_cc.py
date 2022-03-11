from control_block_diagram.components import Box, Connection
from control_block_diagram.predefined_components import Add, PIController


def perm_ex_dc_cc(emf_feedforward):
    def cc_perm_ex_dc(start, control_task):

        space = 1 if control_task == 'CC' else 1.5
        add_current = Add(start.add_x(space))
        if control_task == 'CC':
            Connection.connect(start, add_current.input_left[0], text=r'$i^{*}$', text_align='left',
                               text_position='start')
        pi_current = PIController(add_current.position.add_x(1.5), text='Current\nController')
        Connection.connect(add_current.output_right, pi_current.input_left)

        start = pi_current.position
        inputs = dict(i_ref=[add_current.input_left[0], dict(text=r'$i^{*}$')], i=[add_current.input_bottom[0],
                        dict(text=r'-', move_text=(-0.2, -0.2), text_position='end', text_align='right')])
        outputs = dict(u=pi_current.output_right[0])
        connect_to_lines = dict()
        connections = dict()

        if emf_feedforward:
            add_emf = Add(pi_current.position.add_x(2))
            Connection.connect(pi_current.output_right, add_emf.input_left, text=r'$\Delta u^{*}$')

            box_psi = Box(add_emf.position.sub_y(2.5), size=(0.7, 0.7), text=r"$\Psi'_{\mathrm{E}}$", inputs=dict(bottom=1),
                          outputs=dict(top=1))
            Connection.connect(box_psi.output_top, add_emf.input_bottom, text=r'$u^{0}$', text_position='end',
                               text_align='right', move_text=(-0.1, -0.2))
            if control_task in ['SC']:
                connect_to_lines['omega'] = [box_psi.input_bottom[0], dict(section=0)]
            elif control_task in ['CC', 'TC']:
                inputs['omega'] = [box_psi.input_bottom[0], dict()]
            outputs['u'] = add_emf.output_right[0]
            start = add_emf.position

        return start, inputs, outputs, connect_to_lines, connections
    return cc_perm_ex_dc
