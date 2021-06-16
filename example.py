import matplotlib.pyplot as plt
import gym_electric_motor as gem
import gem_controllers as gc
import time

env_id = 'Finite-SC-ExtExDc-v0'
env = gem.make(
    env_id, visualization=dict(state_plots='all'), ode_solver='euler'
)

c = gc.GemController.make(
    env,
    env_id,
    a=5,
    current_safety_margin=0.15
)
env.reset()
start = time.time()
c.control_environment(env, n_steps=50000, render_env=True)
print(time.time() - start)

plt.show(block=True)