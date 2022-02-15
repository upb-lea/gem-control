import gym_electric_motor as gem
from gym_electric_motor import reference_generators as rg
import gem_controllers as gc
from gym_electric_motor.visualization import MotorDashboard
from gym_electric_motor.state_action_processors import FluxObserver


env_id = 'Cont-CC-SCIM-v0'

# Initialize the motor environment. The controller of the induction motor requires a flux observer.
env = gem.make(
        env_id,
        state_action_processors=(FluxObserver(),),
        visualization=MotorDashboard(state_plots=['omega', 'torque', 'i_sd', 'i_sq', 'u_sd', 'u_sq', 'psi_angle', 'psi_abs']),
    )

state, reference = env.reset()

# Initialize the controller
c = gc.GemController.make(
    env,
    env_id,
    a=5,
    current_safety_margin=0.15,
)

# Control the motor environment
c.control_environment(env, n_steps=50001, render_env=True)
