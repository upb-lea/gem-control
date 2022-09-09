import gym_electric_motor as gem
import gem_controllers as gc
from gym_electric_motor.visualization import MotorDashboard
from gym_electric_motor.physical_system_wrappers import FluxObserver


if __name__ == '__main__':


# Initialize the motor environment. The controller of the induction motor requires a flux observer.
env = gem.make(
        env_id,
        physical_system_wrappers=(FluxObserver(),),
        visualization=MotorDashboard(state_plots=['omega', 'torque', 'i_sd', 'i_sq', 'u_sd', 'u_sq', 'psi_angle', 'psi_abs']),
)

state, reference = env.reset()

# Initialize the controller
c = gc.GemController.make(
    env,
    env_id,
    a=5,
    block_diagram=True,
    current_safety_margin=0.15,
    save_block_diagram_as='pdf'
)

# Control the motor environment
c.control_environment(env, n_steps=30001, render_env=True)
