class Stage:

    def __call__(self, stage, reference):
        raise NotImplementedError

    def reset(self):
        pass

    def tune(self, env, motor_type, action_type, control_task):
        """Optional method to tune the """
        pass
