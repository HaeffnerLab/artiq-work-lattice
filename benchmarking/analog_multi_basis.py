from pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from subsequences.ising_simulation import IsingSimulation
import numpy as np
from artiq.experiment import *

# This sequence implements a multi-basis analog benchmarking protocol for
# an analog simulation involving a Molmer-Sorensen interaction and a single-ion
# AC stark shift.
# It runs the dynamics forward in one basis and backward in a different basis,
# with appropriate global rotations before and after the backward execution,
# and therefore should end up in the initial state.
# It also implements amplitude noise on the two parameters, such that when
# increasing the noise, the result should be a decrease in the population that
# ends up in the initial state.

class AnalogMultiBasisBenchmarking(PulseSequence):
    PulseSequence.accessed_params = {
        "Benchmarking.amplitude_noise_fraction",
        "Benchmarking.simulation_time",
    }

    PulseSequence.scan_params.update(
        AnalogMultiBasisBenchmarking=[
            ("Benchmarking", ("Benchmarking.amplitude_noise_fraction", 0., 0.5, 11)),
            ("Benchmarking", ("Benchmarking.simulation_time", 0., 2*ms, 20, "ms")),
        ]
    )

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.simulation = self.add_subsequence(IsingSimulation)
        self.simulation.setup_noisy_single_pass(self)
        self.phase_ref_time = np.int64(0)
        self.set_subsequence["AnalogMultiBasisBenchmarking"] = self.set_subsequence_benchmarking

    @kernel
    def set_subsequence_benchmarking(self):
        self.simulation.duration = self.get_variable_parameter("Benchmarking_simulation_time")
        self.simulation.noise_fraction = self.get_variable_parameter("Benchmarking_amplitude_noise_fraction")
        self.simulation.setup_ramping(self)

    @kernel
    def AnalogMultiBasisBenchmarking(self):
        self.phase_ref_time = now_mu()
        self.simulation.phase_ref_time = self.phase_ref_time

        self.stateprep.run(self)
        # run the simulation forward
        self.simulation.reverse = False
        self.simulation.alternate_basis = False
        self.simulation.run(self)

        # run the simulation backward
        self.simulation.reverse = True
        self.simulation.alternate_basis = True
        self.simulation.run(self)
