import numpy as np

import gym_electric_motor.physical_systems.converters as cv


def non_parameterized(*args, **kwargs):
    raise Exception('Component not parameterized. Call the parameterize() function before the first control cycle.')


def disc_converter_actions(converter):
    """Calculates the high, idle and low switching actions for each from a given finite converter for each
    of the converters output voltages.

    Args:
        Converter(PowerElectronicConverter): The converter to read the switching levels from.
    Returns:
        high_action(np.ndarray): The high switching actions
        idle_action(np.ndarray): The idle switching actions
        low_action(np.ndarray): The low switching actions

    """
    if type(converter) is cv.FiniteMultiConverter:
        high_actions = []
        idle_actions = []
        low_actions = []
        for subconverter in converter.subconverters:
            #cv_actions =
            high_actions.append(_converter_actions[subconverter])

_converter_actions = {
    cv.FiniteOneQuadrantConverter : np.array([[1], [0], [0]]),
    cv.FiniteTwoQuadrantConverter : np.array([[1], [0], [2]]),
    cv.FiniteFourQuadrantConverter : np.array([[1], [0], [2]]),
    cv.FiniteB6BridgeConverter : np.array([[1, 1, 1], [0, 0, 0], [2, 2, 2]])
}