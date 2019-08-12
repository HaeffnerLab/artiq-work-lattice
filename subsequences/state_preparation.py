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

        # delay to avoid RTIO underflow
        if s.sbc.enable_sideband_cooling:
            num_cycles = int(s.sideband_cooling_cycles)
            num_modes = 1
            if s.sbc.sequential_enable:
                num_modes += 1
            if s.sbc.sequential1_enable:
                num_modes += 1
            if s.sbc.sequential2_enable:
                num_modes += 1
            delay(num_cycles*num_modes*1.4*ms)
            
        delay(1*ms)
        s.dopplerCooling.run(self)
        if s.enable_optical_pumping:
            s.op.run(self)
        if s.enable_sideband_cooling:
            s.sbc.run(self)
