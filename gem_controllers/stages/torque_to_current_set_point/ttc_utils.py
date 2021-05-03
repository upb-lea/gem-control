from .permex_dc_ttc import PermExDcTorqueToCurrent
from .extex_dc_ttc import ExtExDcTorqueToCurrent
from .series_dc_ttc import SeriesDcTorqueToCurrent
from .shunt_dc_ttc import ShuntDcTorqueToCurrent

torque_to_current_function = {
    'PermExDc': PermExDcTorqueToCurrent,
    'ExtExDc': ExtExDcTorqueToCurrent,
    'SeriesDc': SeriesDcTorqueToCurrent,
    'ShuntDc': ShuntDcTorqueToCurrent
}