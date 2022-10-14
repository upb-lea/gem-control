from control_block_diagram.components import Connection
from control_block_diagram.predefined_components import PMSM, DcConverter


def pmsm_output(emf_feedforward):
    """
    Args:
        emf_feedforward: Boolean whether emf feedforward stage is included

    Returns:
        Function to build the PMSM Output Block
    """

    def _pmsm_output(start, control_task):
        """
        Function to build the PMSM Output Block
        Args:
            start:          Starting Point of the Block
            control_task:   Control task of the controller

        Returns:
            endpoint, inputs, outputs, connection to other lines, connections
        """

        # Converter with DC input voltage
        converter = DcConverter(start.add_x(2.7), input_number=3, input_space=0.3, output_number=3)

        # PMSM block
        pmsm = PMSM(converter.position.sub_y(5), size=1.3, input='top')

        # Connection between the converter and the motor block
        con_1 = Connection.connect(converter.output_bottom, pmsm.input_top, arrow=False)

        start = pmsm.position   # starting point of the next block
        # Inputs of the stage
        inputs = dict(S=[converter.input_left, dict(text=[r'$\mathbf{S}_{\mathrm{a,b,c}}$', '', ''], distance_y=0.25)])
        outputs = dict(epsilon=pmsm.output_left[0])     # Outputs of the stage
        connect_to_lines = dict()   # Connections to other lines
        connections = dict(i=con_1)     # Connections

        return start, inputs, outputs, connect_to_lines, connections

    return _pmsm_output
