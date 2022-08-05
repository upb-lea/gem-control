import gym_electric_motor as gem
import gem_controllers as gc
from gym_electric_motor.visualization import MotorDashboard
from gym_electric_motor.physical_system_wrappers import FluxObserver
from matplotlib import pyplot as plt

env_id = 'Finite-TC-PermExDc-v0'

# Initialize the motor environment. The controller of the induction motor requires a flux observer.
env = gem.make(
        env_id,
        #physical_system_wrappers=(FluxObserver(),),
        visualization=MotorDashboard(
            state_plots=['omega', 'torque', 'i', 'u']),#, 'psi_angle', 'psi_abs']),
    )

state, reference = env.reset()

# Initialize the controller
c = gc.GemController.make(
    env,
    env_id,
    a=5,
    current_safety_margin=0.15,
)

c.reset()

for i in range(10001):
    env.render()
    action = c.control(state, reference)
    (state, reference), rew, done, _ = env.step(action)
    if done:
        state, reference = env.reset()
        c.reset()

plt.show(block=True)
env.close()

# Control the motor environment
c.control_environment(env, n_steps=50001, render_env=True)
