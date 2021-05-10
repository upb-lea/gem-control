from gem_controllers import stages
import gem_controllers as gc

dc_motors = ['PermExDc', 'ExtExDc', 'SeriesDc', 'ShuntDc']
sync_motors = ['PMSM', 'SynRM']
induction_motors = ['SCIM', 'DFIM']


def design_controller(env, action_type, motor, control_task,  base_current_controller=None, base_speed_controller='PI'):
    if motor in dc_motors:
        return design_dc_controller(action_type, control_task, motor, base_current_controller, base_speed_controller)
    elif motor in sync_motors:
        return design_field_oriented_controller(
            action_type, control_task, motor, base_current_controller, base_speed_controller
        )

    raise Exception(f'No Designer available for motor type: {motor}')


def design_dc_controller(action_type, control_task, motor, base_current_controller=None, base_speed_controller='PI'):

    if base_current_controller is None:
        base_current_controller = 'ThreePoint' if action_type == 'Finite' else 'PI'
    stages_ = [stages.InputStage()]
    if control_task == 'SC':
        stages_.append(_controller_registry[base_speed_controller](control_task='SC'))
    if control_task in ['SC', 'TC']:
        stages_.append(stages.torque_to_current_function[motor]())
    stages_.append(_controller_registry[base_current_controller](control_task='CC'))
    stages_.append(stages.EMFFeedforward())
    if action_type == 'Finite':
        stages_.append(stages.DiscOutputStage())
    else:
        stages_.append(stages.ContOutputStage())
    controller = gc.FeedforwardController()
    controller.stages.extend(stages_)
    return controller


def design_field_oriented_controller(
    action_type, control_task, motor, base_current_controller=None, base_speed_controller='PI'
):
    from gem_controllers.gem_controller import GemController
    if base_current_controller is None:
        base_current_controller = 'ThreePoint' if action_type == 'Finite' else 'PI'
    stages_ = [stages.InputStage()]
    if control_task == 'SC':
        stages_.append(_controller_registry[base_speed_controller]())
    if control_task in ['SC', 'TC']:
        stages_.append(stages.MTPC())
    if action_type == 'Finite':
        stages_.append(stages.AbcTransformation())
    stages_.append(_controller_registry[base_current_controller]())
    if action_type == 'Cont':
        stages_.append(stages.EMFFeedforward())
        stages_.append(stages.AbcTransformation())
    if action_type == 'Finite':
        stages_.append(stages.DiscOutputStage())
    else:
        stages_.append(stages.ContOutputStage())
    controller = GemController()
    controller.stages.extend(stages)
    return controller


_controller_registry = {
    'PI': stages.PIController,
    'P': stages.PController,
    'I': stages.IController,
    'PID': stages.PIDController,
    'ThreePoint': stages.ThreePointController
}
