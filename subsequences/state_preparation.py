from artiq.experiment import *
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping import OpticalPumping
from subsequences.sideband_cooling import SidebandCooling

class StatePreparation:
    enable_optical_pumping="StatePreparation.optical_pumping_enable"
    enable_sideband_cooling="StatePreparation.sideband_cooling_enable"

    def add_child_subsequences(pulse_sequence):
        s = StatePreparation
        s.dopplerCooling = pulse_sequence.add_subsequence(DopplerCooling)
        s.op = pulse_sequence.add_subsequence(OpticalPumping)
        s.sbc = pulse_sequence.add_subsequence(SidebandCooling)

    def subsequence(self):
        s = StatePreparation

        delay(1*ms)
        s.dopplerCooling.run(self)
        if s.enable_optical_pumping:
            s.op.run(self)
        if s.enable_sideband_cooling:
            s.sbc.run(self)

            
        if s.enable_sideband_cooling:
            s.sbc.run(self)

            num_cycles = int(s.sideband_cooling_cycles)
            for i in range(num_cycles):
                s.sbc.run(self)
                if s.enable_pulsed_optical_pumping:
                    s.opp.run(self)
                elif s.enable_optical_pumping:
                    s.opc.run(self)
