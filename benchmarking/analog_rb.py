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
        "Benchmarking.sequence_number",
        "Benchmarking.fast_noise_fraction",
        "Benchmarking.slow_noise_fraction",
        "Benchmarking.parameter_miscalibration_fraction",
        "Benchmarking.crosstalk_fraction",
        "Benchmarking.control_leakage_fraction",
    }

    PulseSequence.scan_params.update(
        AnalogRB=[
            ("Benchmarking", ("Benchmarking.sequence_number", 1, 1, 200)),
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
        self.set_subsequence["AnalogRB"] = self.set_subsequence_benchmarking

        # load pickle files with analog RB sequences, initial states, and final states
        self.sequences = pickle.load(open("analog_rb_sequences.pickle", "rb"))
        self.initial_states = pickle.load(open("analog_rb_initial_states.pickle", "rb"))
        self.final_states = pickle.load(open("analog_rb_final_states.pickle", "rb"))

    @kernel
    def set_subsequence_benchmarking(self):
        self.sequence_number = self.get_variable_parameter("Benchmarking_sequence_number")
        analog_rb_sequence = self.sequences[self.sequence_number]
        _, t_step, _ = analog_rb_sequence[0]
        self.simulation.duration = t_step
        self.simulation.fast_noise_fraction = self.get_variable_parameter("Benchmarking_fast_noise_fraction")
        self.simulation.slow_noise_fraction = self.get_variable_parameter("Benchmarking_slow_noise_fraction")
        self.simulation.parameter_miscalibration_fraction = self.get_variable_parameter("Benchmarking_parameter_miscalibration_fraction")
        self.simulation.crosstalk_fraction = self.get_variable_parameter("Benchmarking_crosstalk_fraction")
        self.simulation.control_leakage_fraction = self.get_variable_parameter("Benchmarking_control_leakage_fraction")
        self.simulation.setup_ramping(self)

    @kernel
    def AnalogRB(self):
        self.phase_ref_time = now_mu()
        self.simulation.phase_ref_time = self.phase_ref_time

        self.stateprep.run(self)

        # initial_state will be a string: "SS", "SD", "DS", or "DD"
        initial_state = self.initial_states[self.sequence_number]
        if initial_state == "SD" or initial_state == "DD":
            # TODO_RYAN: pi pulse with global 729
        if initial_state == "SD" or initial_state == "DS":
            # TODO_RYAN: pi pulse with local 729

        def is_term_selected(term_index, selected_terms):
            for term in selected_terms:
                if term_index == term:
                    return True
            return False

        # Run the simulation for each item in the sequence
        analog_rb_sequence = self.sequences[self.sequence_number]
        for selected_h_terms, _, reverse_step in analog_rb_sequence[0]:
            self.simulation.reverse = reverse_step
            self.simulation.disable_coupling_term = not is_term_selected(0)
            self.simulation.disable_transverse_term = not is_term_selected(1)
            self.simulation.run(self)

        # adjust for the final_state so that we ideally end up back in SS
        final_state = self.final_states[self.sequence_number]
        if final_state == "SD" or final_state == "DS":
            # TODO_RYAN: -pi pulse with local 729
        if final_state == "SD" or final_state == "DD":
            # TODO_RYAN: -pi pulse with global 729
