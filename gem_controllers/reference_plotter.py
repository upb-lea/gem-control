from gym_electric_motor.visualization.motor_dashboard import StatePlot


class ReferencePlotter:
    """This class adds the reference values of the subordinate stages to the stage plots of the GEM environment."""
    def __init__(self):
        self._referenced_plots = []
        self._referenced_states = []
        self._plot_references = None

    def tune(self, env, referenced_states, plot_references, **_):
        """
        Tune the reference plotter.

        Args:
            env(ElectricMotorEnvironment): The GEM-Environment that the controller shall be created for.
            referenced_states(np.ndarray): Array of all referenced states.
            plot_references(bool): Flag, if the references of the subordinate stages should be plotted.

        """
        if plot_references:
            for visualization in env.visualizations:
                for time_plot in visualization._time_plots:
                    if isinstance(time_plot, StatePlot):
                        if time_plot.state in referenced_states:
                            self._referenced_plots.append(time_plot)
                            self._referenced_states.append(time_plot.state)

        for plot in self._referenced_plots:
            plot._referenced = True

    def update_plots(self, references):
        """
        Update the state plots of the GEM environment.

        Args:
            references(np.ndarray): Array of all reference values of the subordinate stages.
        """

        for plot, state in zip(self._referenced_plots, self._referenced_states):
            plot._ref_data[plot.data_idx] = references[state]
