from .permex_dc_ops import PermExDcOperationPointSelection
from .extex_dc_ttc import ExtExDcOperationPointSelection
from .series_dc_ops import SeriesDcOperationPointSelection
from .shunt_dc_ops import ShuntDcOperationPointSelection
from .pmsm_ops import PMSMOperationPointSelection

torque_to_current_function = {
    'PermExDc': PermExDcOperationPointSelection,
    'ExtExDc': ExtExDcOperationPointSelection,
    'SeriesDc': SeriesDcOperationPointSelection,
    'ShuntDc': ShuntDcOperationPointSelection,
    'PMSM': PMSMOperationPointSelection,
    'SynRM': PMSMOperationPointSelection
}
