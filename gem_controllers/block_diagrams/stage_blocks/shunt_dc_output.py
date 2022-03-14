from control_block_diagram.components import Box, Connection
from control_block_diagram.predefined_components import DcShuntMotor, DcConverter


def shunt_dc_output(emf_feedforward):
    def _shunt_dc_output(start, control_task):
        space = 1.5 if emf_feedforward else 2
        pwm = Box(start.add_x(space), size=(1, 0.8), text='PWM')
        converter = DcConverter(pwm.position.add_x(2), size=1.2, input_number=1)
        Connection.connect(pwm.output_right, converter.input_left, text='$S$')

        dc_shunt = DcShuntMotor(converter.position.sub_y(3), size=1.2, input='top', output='left')

        conv_motor = Connection.connect(converter.output_bottom, dc_shunt.input_top, text=['', r'$i_{\mathrm{A}}$'],
                                        text_align='right', arrow=False)

        con_i = Connection.connect_to_line(conv_motor[0], pwm.position.sub_y(1.5), text=r'$i_{\mathrm{A}}$',
                                           arrow=False, fill=False, draw=0.1)

        start = converter.position
        inputs = dict(u=[pwm.input_left[0], dict(text=r'$u^{*}$')])
        outputs = dict(i=con_i.end)
        connect_to_lines = dict()
        connections = dict()

        if emf_feedforward or control_task in ['SC']:
            con_omega = Connection.connect(dc_shunt.output_left[0].sub_x(2), dc_shunt.output_left[0],
                                           text=r'$\omega_{\mathrm{me}}$', arrow=False)
            outputs['omega'] = con_omega.end

        return start, inputs, outputs, connect_to_lines, connections
    return _shunt_dc_output