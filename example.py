import gym_electric_motor as gem
import gem_controllers as gc
from gym_electric_motor.visualization import MotorDashboard
from gym_electric_motor.state_action_processors import FluxObserver

import numpy as np


env_id = 'Cont-CC-PMSM-v0'

# Initialize the motor environment. The controller of the induction motor requires a flux observer.
env = gem.make(
        env_id,
        #state_action_processors=(FluxObserver(),),
        visualization=MotorDashboard(state_plots=['omega', 'torque', 'i_sd', 'i_sq', 'u_sd', 'u_sq']),
    )

# Initialize the controller
c = gc.GemController.make(
    env,
    env_id,
    #a=5,
    #current_safety_margin=0.15,
)

# Control the motor environment
c.control_environment(env, n_steps=50001, render_env=True)
