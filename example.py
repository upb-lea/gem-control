import gym_electric_motor as gem
import gem_controllers as gc
from gym_electric_motor.physical_system_wrappers import FluxObserver


env_id = 'Cont-TC-SCIM-v0'

# Initialize the motor environment. The controller of the induction motor requires a flux observer.
env = gem.make(
        env_id,
        physical_system_wrappers=(FluxObserver(),),
    )

# Initialize the controller
c = gc.GemController.make(
    env,
    env_id,
    a=5,
    current_safety_margin=0.15,
)

# Control the motor environment
c.control_environment(env, n_steps=50001, render_env=True)
