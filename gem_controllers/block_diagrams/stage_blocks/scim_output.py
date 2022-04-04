from control_block_diagram.components import Connection
from control_block_diagram.predefined_components import DcConverter, SCIM


def scim_output(emf_feedforward):
    def _scim_output(start, control_task):
        converter = DcConverter(start.add_x(2.7), input_number=3, input_space=0.3, output_number=3)
        scim = SCIM(converter.position.sub_y(5), size=1.3, input='top')
        con_1 = Connection.connect(converter.output_bottom, scim.input_top, arrow=False)
        start = scim.position
        inputs = dict(S=[converter.input_left, dict(text=[r'$\mathbf{S}_{\mathrm{a,b,c}}$', '', ''], distance_y=0.25)])
        outputs = dict(omega=scim.output_left[0])
        connect_to_lines = dict()
        connections = dict(i=con_1)

        return start, inputs, outputs, connect_to_lines, connections
    return _scim_output
