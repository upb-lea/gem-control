import gym_electric_motor as gem
import gem_controllers as gc
from gym_electric_motor.visualization import MotorDashboard
from gym_electric_motor.state_action_processors import FluxObserver
import matplotlib
matplotlib.use('TkAgg')

env_id = 'AbcCont-TC-SCIM-v0'

env = gem.make(
        env_id,
        state_action_processors=(FluxObserver(),),
        visualization=MotorDashboard(state_plots=['torque', 'i_sd', 'i_sq', 'u_sd', 'u_sq', 'psi_abs']),
    )

state, reference = env.reset()


c = gc.GemController.make(
    env,
    env_id,
    a=5,
    current_safety_margin=0.15,
    )

c.control_environment(env, n_steps=50001, render_env=True)
