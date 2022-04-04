from control_block_diagram.components import Connection
from control_block_diagram.predefined_components import DcConverter, DcExtExMotor


def ext_ex_dc_output(emf_feedforward):
    def _ext_ex_dc_output(start, control_task):
        converter = DcConverter(start.add(2.5, -0.6), size=1.7, input_number=2, input_space=1.2, output_number=4,
                                output_space=0.25)

        dc_ext_ex = DcExtExMotor(converter.position.sub_y(3), size=1.2, input='top', output='left')

        con_conv_a = Connection.connect(converter.output_bottom[0], dc_ext_ex.input_top[0], arrow=False)
        Connection.connect(converter.output_bottom[1], dc_ext_ex.input_top[1], arrow=False)
        con_conv_e = Connection.connect(converter.output_bottom[2], dc_ext_ex.input_top[2], arrow=False)
        Connection.connect(converter.output_bottom[3], dc_ext_ex.input_top[3], arrow=False)

        con_e = Connection.connect_to_line(con_conv_e, start.sub_y(2), arrow=False, draw=0.1, fill=False,
                                           text=r'$i_{\mathrm{e}}$', distance_y=0.25)
        con_a = Connection.connect_to_line(con_conv_a, start.sub_y(2.5), arrow=False, draw=0.1, fill=False,
                                           text=r'$i_{\mathrm{a}}$', distance_y=0.25, text_align='bottom',
                                           move_text=(0.25, 0))

        start = converter.position
        inputs = dict(u_e=[converter.input_left[0], dict(text=r'$\mathrm{S_e}$', distance_y=0.25)],
                      u_a=[converter.input_left[1], dict(text=r'$\mathrm{S_a}$', distance_y=0.25)])
        outputs = dict(i_e=con_e.end, i_a=con_a.end)
        connect_to_lines = dict()
        connections = dict()

        if emf_feedforward or control_task in ['SC']:
            con_omega = Connection.connect(dc_ext_ex.output_left[0].sub_x(2), dc_ext_ex.output_left[0],
                                           text=r'$\omega_{\mathrm{me}}$', arrow=False)
            outputs['omega'] = con_omega.end

        return start, inputs, outputs, connect_to_lines, connections
    return _ext_ex_dc_output
