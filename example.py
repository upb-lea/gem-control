import gym_electric_motor as gem
import gem_controllers as gc
import matplotlib
from gym_electric_motor.state_action_processors import FluxObserver
from gym_electric_motor.visualization import MotorDashboard
from gym_electric_motor.reference_generators import WienerProcessReferenceGenerator, MultipleReferenceGenerator

matplotlib.use('TkAgg')
env_id = 'AbcCont-TC-SCIM-v0'

rg = MultipleReferenceGenerator([WienerProcessReferenceGenerator(reference_state='i_sd', sigma_range=(0.001, 0.002)),
                                 WienerProcessReferenceGenerator(reference_state='i_sq', sigma_range=(0.001, 0.002))])

env = gem.make(
        env_id,
        state_action_processors=(FluxObserver(),),
        visualization=MotorDashboard(state_plots=('torque', 'i_sd', 'i_sq', 'psi_angle', 'psi_abs')),
        #reference_generator=rg
    )

state, reference = env.reset()


c = gc.GemController.make(
    env,
    env_id,
    a=5,
    current_safety_margin=0.15
    )

c.control_environment(env, n_steps=50001, render_env=True)