import matplotlib.pyplot as plt
import gym_electric_motor as gem
import gem_controllers as gc
import time

env_id = 'DqCont-SC-PMSM-v0'
env = gem.make(
    env_id,
    visualization=gem.visualization.MotorDashboard(state_plots='all')
)

c = gc.GemController.make(
    env,
    env_id,
    a=4,
    current_safety_margin=0.15
)
env.reset()
start = time.time()
c.control_environment(env, n_steps=50000, render_env=True)
print(time.time() - start)

plt.show(block=True)