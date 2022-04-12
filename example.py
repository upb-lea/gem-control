import gym_electric_motor as gem
import gem_controllers as gc


if __name__ == '__main__':

    env_id = 'Cont-CC-ExtExDc-v0'
    env = gem.make(
            env_id,
        )

    state, reference = env.reset()

    # Initialize the controller
    c = gc.GemController.make(
        env,
        env_id,
        a=5,
        block_diagram=True,
        current_safety_margin=0.15,
    )

    # Control the motor environment
    c.control_environment(env, n_steps=30001, render_env=True)
