import gym_electric_motor as gem
import gem_controllers as gc
import numpy as np

env_id = 'Finite-TC-PermExDc-v0'
env = gem.make(
    env_id, visualization=dict(state_plots='all'),
    converter='Finite-4QC'
    #supply=dict(u_nominal=80.0),
)
'''
c = gc.GemController.make(
    env,
    env_id,
    tuner_kwargs=dict(a=4, current_safety_margin=0.15),
)
'''
c = gc.TorqueController()
c = gc.GymElectricMotorAdapter(c)
action_type, control_type, motor_type, *version_ = env_id.split('-')
c.design(env, env_id)
c.tune(env, env_id, a=6, current_safety_margin=0.3)


done = True

for i in range(30000):
    if done:
        state, reference = env.reset()
        c.reset()
    env.render()
    action = c.control(state, reference)
    (state, reference), reward, done, _ = env.step(action)
