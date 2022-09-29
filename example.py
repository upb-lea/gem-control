import gym_electric_motor as gem
import gem_controllers as gc
from gym_electric_motor.visualization.motor_dashboard import MotorDashboard
from gym_electric_motor.physical_system_wrappers import FluxObserver


if __name__ == '__main__':

    env_id = 'Cont-CC-PMSM-v0'
    env = gem.make(
            env_id,
            visualization=MotorDashboard(state_plots=['torque', 'i_sd', 'i_sq', 'u_sd', 'u_sq'])
            #physical_system_wrappers=(FluxObserver(),)
        )

    state, reference = env.reset()
    # Initialize the controller
    c = gc.GemController.make(
        env,
        env_id,
        a=8,
        block_diagram=True,
        current_safety_margin=0.2,
        #save_block_diagram_as='pdf'
    )

    # Control the motor environment
    c.control_environment(env, n_steps=30001, render_env=True)
