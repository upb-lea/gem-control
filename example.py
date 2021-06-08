import gym_electric_motor as gem
import gem_controllers as gc

env_id = 'Cont-SC-ExtExDc-v0'
env = gem.make(
    env_id, visualization=dict(state_plots='all'),
)

c = gc.GemController.make(
    env,
    env_id,
    a=4,
    current_safety_margin=0.05
)
c.control_environment(env, n_steps=30000, render_env=True)
