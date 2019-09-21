from pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from subsequences.rabi_excitation import RabiExcitation
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
        "Benchmarking.simulation_time",
        "Benchmarking.fast_noise_fraction",
        "Benchmarking.slow_noise_fraction",
        "Benchmarking.parameter_miscalibration_fraction",
        "Benchmarking.crosstalk_fraction",
        "Benchmarking.control_leakage_fraction",
        "Benchmarking.initial_state",
        "Benchmarking.global_pi_time",
        "Benchmarking.global_amp",
        "Benchmarking.global_att",
        "Benchmarking.global_line_selection",
        "Benchmarking.local_pi_time",
        "Benchmarking.local_amp",
        "Benchmarking.local_att",
        "Benchmarking.local_line_selection",
    }

    PulseSequence.scan_params.update(
        AnalogMultiBasisBenchmarking=[
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
        self.rabi = self.add_subsequence(RabiExcitation)
        self.simulation = self.add_subsequence(IsingSimulation)
        self.simulation.setup_noisy_single_pass(self)
        self.phase_ref_time = np.int64(0)
        self.set_subsequence["AnalogMultiBasisBenchmarking"] = self.set_subsequence_benchmarking

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
    def global_pi_pulse(self, phase=0.):
        self.rabi.channel_729 = "729G"
        self.rabi.duration = self.Benchmarking_global_pi_time
        self.rabi.amp_729 = self.Benchmarking_global_amp
        self.rabi.att_729 = self.Benchmarking_global_att
        self.rabi.freq_729 = self.calc_frequency(
            self.Benchmarking_global_line_selection,
            dds=self.rabi.channel_729
        )
        self.rabi.phase_729 = phase
        self.rabi.run()

    @kernel
    def local_pi_pulse(self, phase=0.):
        self.rabi.channel_729 = "729L1"
        self.rabi.duration = self.Benchmarking_local_pi_time
        self.rabi.amp_729 = self.Benchmarking_local_amp
        self.rabi.att_729 = self.Benchmarking_local_att
        self.rabi.freq_729 = self.calc_frequency(
            self.Benchmarking_local_line_selection,
            dds=self.rabi.channel_729
        )
        self.rabi.phase_729 = phase
        self.rabi.run()

    @kernel
    def AnalogMultiBasisBenchmarking(self):
        self.phase_ref_time = now_mu()
        self.simulation.phase_ref_time = self.phase_ref_time
        self.rabi.phase_ref_time = self.phase_ref_time

        self.stateprep.run(self)

        # initial_state will be a string: "SS", "SD", "DS", or "DD"
        initial_state = self.Benchmarking_initial_state
        if initial_state == "SD" or initial_state == "DD":
            self.global_pi_pulse()
        if initial_state == "SD" or initial_state == "DS":
            self.local_pi_pulse()

        # run the simulation forward
        self.simulation.reverse = False
        self.simulation.alternate_basis = False
        self.simulation.run(self)

        # run the simulation backward
        self.simulation.reverse = True
        self.simulation.alternate_basis = True
        self.simulation.run(self)

        # undo the initial_state preparation so that we ideally end up back in SS
        if initial_state == "SD" or initial_state == "DS":
            self.local_pi_pulse(phase=180.)
        if initial_state == "SD" or initial_state == "DD":
            self.global_pi_pulse(phase=180.)
