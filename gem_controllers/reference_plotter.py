class ReferencePlotter:
    def __init__(self):
        self._referenced_plots = []
        self._referenced_states = []
        self._plot_references = None

    def tune(self, env, referenced_states, plot_references, **_):
        if plot_references:
            for visualization in env.visualizations:
                for time_plot in visualization._time_plots:
                    if time_plot.state in referenced_states:
                        self._referenced_plots.append(time_plot)
                        self._referenced_states.append(time_plot.state)

        for plot in self._referenced_plots:
            plot._referenced = True

    def update_plots(self, references):
        for plot, state in zip(self._referenced_plots, self._referenced_states):
            plot._ref_data[plot.data_idx] = references[state]
