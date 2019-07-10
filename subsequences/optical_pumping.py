from artiq.experiment import *
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous

class OpticalPumping:
    enable_pulsed_optical_pumping="StatePreparation.pulsed_optical_pumping"

    def add_child_subsequences(pulse_sequence):
        o = OpticalPumping
        o.opp = pulse_sequence.add_subsequence(OpticalPumpingPulsed)
        o.opc = pulse_sequence.add_subsequence(OpticalPumpingContinuous)

    def subsequence(self):
        o = OpticalPumping
        if s.enable_pulsed_optical_pumping:
            s.opp.run(self)
        else
            s.opc.run(self)
