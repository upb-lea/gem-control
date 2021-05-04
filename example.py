import gym_electric_motor as gem
import gem_controllers as gc

env_id = 'Cont-SC-ExtExDc-v0'
env = gem.make(env_id, visualization=dict(state_plots='all'))

c = gc.GemController.make(env, env_id, tuner_kwargs=dict(a=6, current_safety_margin=0.3))

done = True

for i in range(30000):
    if done:
        state, reference = env.reset()
        c.reset()
    env.render()
    action = c.control(state, reference)
    (state, reference), reward, done, _ = env.step(action)