import gym_electric_motor as gem
import gem_controllers as gc

env_id = 'Cont-TC-SeriesDc-v0'
env = gem.make(env_id, visualization=dict(state_plots='all'))
'''
c = gc.GemController.make(
    env,
    env_id,
    tuner_kwargs=dict(a=4, current_safety_margin=0.15),
)
'''
c = gc.TorqueController()
action_type, control_type, motor_type, *version_ = env_id.split('-')
c.design(action_type, motor_type, decoupling=True)
c.tune(env, motor_type, action_type, control_type)


done = True

for i in range(30000):
    if done:
        state, reference = env.reset()
        c.reset()
    env.render()
    action = c.control(state, reference)
    (state, reference), reward, done, _ = env.step(action)
