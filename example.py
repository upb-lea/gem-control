import gym_electric_motor as gem
import gem_controllers as gc
import matplotlib
from gym_electric_motor.visualization import MotorDashboard


matplotlib.use('TkAgg')
env_id = 'Cont-TC-ShuntDc-v0'

env = gem.make(
        env_id,
        #visualization=MotorDashboard(state_plots=('torque', 'i', 'u')),
    )

state, reference = env.reset()


c = gc.GemController.make(
    env,
    env_id,
    a=5,
    current_safety_margin=0.15,
    visualization=True
    )

c.control_environment(env, n_steps=50001, render_env=True)