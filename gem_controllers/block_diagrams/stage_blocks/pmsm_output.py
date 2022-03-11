from control_block_diagram.components import Connection
from control_block_diagram.predefined_components import PMSM, DcConverter


def pmsm_output(emf_feedforward):
    def _pmsm_output(start, control_task):
        converter = DcConverter(start.add_x(2.7), input_number=3, input_space=0.3, output_number=3)
        pmsm = PMSM(converter.position.sub_y(5), size=1.3, input='top')
        con_1 = Connection.connect(converter.output_bottom, pmsm.input_top, arrow=False)

        start = pmsm.position
        inputs = dict(S=[converter.input_left, dict(text=[r'$\mathbf{S}_{\mathrm{a,b,c}}$', '', ''], distance_y=0.25)])
        outputs = dict(epsilon=pmsm.output_left[0])
        connect_to_lines = dict()
        connections = dict(i=con_1)

        return start, inputs, outputs, connect_to_lines, connections

    return _pmsm_output
