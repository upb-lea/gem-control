from control_block_diagram.components import Connection, Circle, Text
from control_block_diagram.predefined_components import EESM, DcConverter


def eesm_output(emf_feedforward):
    """
    Args:
        emf_feedforward: Boolean whether emf feedforward stage is included

    Returns:
        Function to build the EESM Output Block
    """

    def _eesm_output(start, control_task):
        """
        Function to build the EESM Output Block
        Args:
            start:          Starting Point of the Block
            control_task:   Control task of the controller

        Returns:
            endpoint, inputs, outputs, connection to other lines, connections
        """

        # Converter with DC input voltage
        converter = DcConverter(start.add(2.7, 0.15), input_number=4, input_space=0.3, output_number=5)

        # PMSM block
        eesm = EESM(converter.position.sub_y(6), size=1.3, input='top')

        # Connection between the converter and the motor block
        con_1 = Connection.connect(converter.output_bottom, eesm.input_top, arrow=False)
        output_i_e = Circle(con_1[3].start.sub_y(4.2), radius=0.1, outputs=dict(left=1), fill=None)
        Text(r'$i_{\mathrm{e}}$', output_i_e.output_left[0].add(-2, 0.25))

        start = eesm.position   # starting point of the next block
        # Inputs of the stage
        inputs = dict(S=[converter.input_left[1:], dict(text=['', '', r'$\mathbf{S}_{\mathrm{a,b,c}}$'],
                                                        distance_y=0.25, text_align='bottom')],
                      S_e=[converter.input_left[0], dict(text=r'$\mathbf{S}_{\mathrm{e}}$',
                                                         distance_y=0.25, text_position='start', move_text=(0.4, 0))])
        outputs = dict(epsilon=eesm.output_left[0], i_e=output_i_e.output_left[0])     # Outputs of the stage
        connect_to_lines = dict()   # Connections to other lines
        connections = dict(i=con_1)     # Connections

        return start, inputs, outputs, connect_to_lines, connections

    return _eesm_output
