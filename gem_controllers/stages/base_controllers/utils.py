import gem_controllers.stages.base_controllers as bc


def get(base_controller_id: str):
    return _base_controller_registry[base_controller_id]


_base_controller_registry = {
    'P': bc.PController,
    'I': bc.IController,
    'PI': bc.PIController,
    'PID': bc.PIDController,
    'ThreePoint': bc.ThreePointController
}