import gym_electric_motor as gem
import gem_controllers as gc
from gym_electric_motor.state_action_processors import FluxObserver


if __name__ == '__main__':

    env_id = 'Cont-SC-ExtExDc-v0'
    env = gem.make(
            env_id,
            #state_action_processors=(FluxObserver(),)
        )

    state, reference = env.reset()

    # Initialize the controller
    c = gc.GemController.make(
        env,
        env_id,
        a=5,
        current_safety_margin=0.15,
        save_block_diagram_as='pdf'
    )

    # Control the motor environment
    c.control_environment(env, n_steps=30001, render_env=True)
