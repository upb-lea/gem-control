import gym_electric_motor as gem
import gem_controllers as gc
ode_solver = gem.physical_systems.ScipyOde(integrator='dopri5', atol=0.01)
env_id = 'Cont-CC-PMSM-v0'
env = gem.make(env_id, ode_solver=ode_solver)
c = gc.GemController.make(
    env,
    env_id,
    a=5,
    current_safety_margin=0.3
)
env.reset()
done = True
for i in range(10000):
    if done:
        state, reference = env.reset()
        c.reset()
    env.render()
    action = c.control(state, reference)
    (state, reference), reward, done, _ = env.step(action)