import gem_controllers as gc


class CascadedController(gc.GemController):

    def control(self, state, reference):
        for stage in self._stages:
            reference = stage(state, reference)
        return reference
