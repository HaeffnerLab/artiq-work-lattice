from pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from subsequences.ising_simulation import IsingSimulation
import numpy as np
from artiq.experiment import *

# This sequence implements an analog-forward, analog-backward protocol for
# an analog simulation involving a Molmer-Sorensen interaction and a single-ion
# AC stark shift.
# It runs the same dynamics forward and backward in time, and therefore should
# end up in the initial state.
# It also implements amplitude noise on the two parameters, such that when
# increasing the noise, the result should be a decrease in the population that
# ends up in the initial state.

class AnalogAnalogBenchmarking(PulseSequence):
    PulseSequence.accessed_params = {
        "Benchmarking.simulation_time",
        "Benchmarking.fast_noise_fraction",
        "Benchmarking.slow_noise_fraction",
        "Benchmarking.parameter_miscalibration_fraction",
        "Benchmarking.crosstalk_fraction",
        "Benchmarking.control_leakage_fraction",
    }

    PulseSequence.scan_params.update(
        AnalogAnalogBenchmarking=[
            ("Benchmarking", ("Benchmarking.simulation_time", 0., 2*ms, 21, "ms")),
            ("Benchmarking", ("Benchmarking.fast_noise_fraction", 0., 0.5, 11)),
            ("Benchmarking", ("Benchmarking.slow_noise_fraction", 0., 0.5, 11)),
            ("Benchmarking", ("Benchmarking.parameter_miscalibration_fraction", 0., 0.5, 11)),
            ("Benchmarking", ("Benchmarking.crosstalk_fraction", 0., 0.5, 11)),
            ("Benchmarking", ("Benchmarking.control_leakage_fraction", 0., 0.5, 11)),
        ]
    )

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.simulation = self.add_subsequence(IsingSimulation)
        self.simulation.setup_noisy_single_pass(self)
        self.phase_ref_time = np.int64(0)
        self.set_subsequence["AnalogAnalogBenchmarking"] = self.set_subsequence_benchmarking

    @kernel
    def set_subsequence_benchmarking(self):
        self.simulation.duration = self.get_variable_parameter("Benchmarking_simulation_time")
        self.simulation.fast_noise_fraction = self.get_variable_parameter("Benchmarking_fast_noise_fraction")
        self.simulation.slow_noise_fraction = self.get_variable_parameter("Benchmarking_slow_noise_fraction")
        self.simulation.parameter_miscalibration_fraction = self.get_variable_parameter("Benchmarking_parameter_miscalibration_fraction")
        self.simulation.crosstalk_fraction = self.get_variable_parameter("Benchmarking_crosstalk_fraction")
        self.simulation.control_leakage_fraction = self.get_variable_parameter("Benchmarking_control_leakage_fraction")
        self.simulation.setup_ramping(self)

    @kernel
    def AnalogAnalogBenchmarking(self):
        self.phase_ref_time = now_mu()
        self.simulation.phase_ref_time = self.phase_ref_time

        self.stateprep.run(self)
        # run the simulation forward
        self.simulation.reverse = False
        self.simulation.run(self)
        # run the simulation backward
        self.simulation.reverse = True
        self.simulation.run(self)
