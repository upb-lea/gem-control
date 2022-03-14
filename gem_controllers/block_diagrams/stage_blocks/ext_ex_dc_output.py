from control_block_diagram.components import Connection
from control_block_diagram.predefined_components import Converter, DcExtExMotor


def ext_ex_dc_output(emf_feedforward):
    def _ext_ex_dc_output(start, control_task):
        converter_e = Converter(start.add_x(3.5), size=1.2, input='left', output='bottom', input_number=1,
                                output_number=2)
        converter_a = Converter(start.add(2, -2), size=1.2, input='left', output='bottom', input_number=1,
                                output_number=2)

        dc_ext_ex = DcExtExMotor(converter_a.position.sub_y(3), size=1.2, input=['top', 'right'], output='left')

        con_conv_a = Connection.connect(converter_a.output_bottom[0], dc_ext_ex.input_top[0], arrow=False)
        Connection.connect(converter_a.output_bottom[1], dc_ext_ex.input_top[1], arrow=False, text=r'$i_{\mathrm{e}}$',
                           text_align='right')
        con_conv_e = Connection.connect(converter_e.output_bottom[0], dc_ext_ex.input_right[0], arrow=False)
        Connection.connect(converter_e.output_bottom[1], dc_ext_ex.input_right[1], arrow=False,
                           text=r'$i_{\mathrm{e}}$', text_align='right', move_text=(0, 2))

        con_e = Connection.connect_to_line(con_conv_e, start.sub_y(0.9), arrow=False, draw=0.1, fill=False,
                                           text=r'$i_{\mathrm{e}}$', distance_y=0.25)
        con_a = Connection.connect_to_line(con_conv_a, start.sub_y(2.9), arrow=False, draw=0.1, fill=False,
                                           text=r'$i_{\mathrm{a}}$', distance_y=0.25, text_align='bottom')

        start = converter_a.position
        inputs = dict(u_e=[converter_e.input_left[0], dict(text='S', distance_y=0.25)],
                      u_a=[converter_a.input_left[0], dict(text='S', distance_y=0.25)])
        outputs = dict(i_e=con_e.end, i_a=con_a.end)
        connect_to_lines = dict()
        connections = dict()

        if emf_feedforward or control_task in ['SC']:
            con_omega = Connection.connect(dc_ext_ex.output_left[0].sub_x(2), dc_ext_ex.output_left[0],
                                           text=r'$\omega_{\mathrm{me}}$', arrow=False)
            outputs['omega'] = con_omega.end

        return start, inputs, outputs, connect_to_lines, connections
    return _ext_ex_dc_output
