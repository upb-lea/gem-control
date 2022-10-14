import gym_electric_motor as gem
import gem_controllers as gc
from gym_electric_motor.physical_system_wrappers import FluxObserver


if __name__ == '__main__':

    # choose the action space
    action_space = 'Cont'   # 'Cont' or 'Finite'

    # choose the control task
    control_task = 'TC'     # 'SC' (speed control), 'TC' (torque control) or 'CC' (current control)

    # chosse the motor type
    motor_type = 'EESM'     # 'PermExDc', 'ExtExDc', 'SeriesDc', 'ShuntDc', 'PMSM', 'EESM', 'SynRM' or 'SCIM'

    env_id = action_space + '-' + control_task + '-' + motor_type + '-v0'

    # Initilize the environment
    if motor_type == 'SCIM':
        env = gem.make(env_id, physical_system_wrappers=(FluxObserver(),))
    else:
        env = gem.make(env_id)

    # Initialize the controller
    c = gc.GemController.make(
        env,
        env_id,
        a=8,
        block_diagram=True,
        current_safety_margin=0.25,
        save_block_diagram_as=(),
    )

    # Control the environment
    c.control_environment(env, n_steps=30000, render_env=True, max_episode_length=10000)

