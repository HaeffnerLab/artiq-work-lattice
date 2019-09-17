from pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from subsequences.ising_simulation import IsingSimulation
import numpy as np
import pickle
import os
from artiq.experiment import *

# This sequence implements analog randomized benchmarking protocol for
# an analog simulation involving a Molmer-Sorensen interaction and a single-ion
# AC stark shift.
# It also implements amplitude noise on the two parameters, such that when
# increasing the noise, the result should be a decrease in the population that
# ends up in the initial state.

class AnalogRB(PulseSequence):
    PulseSequence.accessed_params = {
        "Benchmarking.amplitude_noise_fraction",
        "Benchmarking.sequence_number",
    }

    PulseSequence.scan_params.update(
        AnalogRB=[
            ("Benchmarking", ("Benchmarking.amplitude_noise_fraction", 0., 0.5, 11)),
            ("Benchmarking", ("Benchmarking.sequence_number", 1, 1, 200)),
        ]
    )

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.simulation = self.add_subsequence(IsingSimulation)
        self.simulation.setup_noisy_single_pass(self)
        self.phase_ref_time = np.int64(0)
        self.set_subsequence["Benchmarking"] = self.set_subsequence_benchmarking

        # load pickle file with analog RB sequences and initial states
        filename = "analog_rb_sequences.pickle"
        self.sequences_and_initial_states = pickle.load(open(filename, "rb"))

    @kernel
    def set_subsequence_benchmarking(self):
        self.sequence_number = self.get_variable_parameter("Benchmarking_sequence_number")
        analog_rb_sequence, initial_state = self.sequences_and_initial_states[self.sequence_number]
        _, t_step, _ = analog_rb_sequence[0][0]
        self.simulation.duration = t_step
        self.simulation.noise_fraction = self.get_variable_parameter("Benchmarking_amplitude_noise_fraction")
        self.simulation.setup_ramping(self)

    @kernel
    def AnalogRB(self):
        self.phase_ref_time = now_mu()
        self.simulation.phase_ref_time = self.phase_ref_time

        self.stateprep.run(self)

        analog_rb_sequence, initial_state = self.sequences_and_initial_states[self.sequence_number]

        # TODO: initialize to initial_state via pi pulses on global and/or local beams

        # Run the simulation for each item in the sequence
        for selected_h_terms, _, reverse_step in analog_rb_sequence[0]:
            self.simulation.reverse = reverse_step
            self.simulation.disable_global = (0 not in selected_h_terms)
            self.simulation.disable_local = (1 not in selected_h_terms)
            self.simulation.run(self)

        # TODO: undo the initial_state initialization so that we ideally end up back in |SS>
