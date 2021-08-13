from artiq.experiment import *
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping import OpticalPumping
from subsequences.sideband_cooling import SidebandCooling
from subsequences.two_tone_sideband_cooling import TwoToneSidebandCooling

class StatePreparation:
    enable_optical_pumping="StatePreparation.optical_pumping_enable"
    enable_sideband_cooling="StatePreparation.sideband_cooling_enable"
    post_delay="StatePreparation.post_delay"
    enable_two_tone_sideband_cooling="StatePreparation.enable_two_tone_sideband_cooling"
    enable_doppler_cooling=1

    def add_child_subsequences(pulse_sequence):
        s = StatePreparation
        s.dopplerCooling = pulse_sequence.add_subsequence(DopplerCooling)
        s.op = pulse_sequence.add_subsequence(OpticalPumping)
        s.sbc = pulse_sequence.add_subsequence(SidebandCooling)
        s.ttsbc = pulse_sequence.add_subsequence(TwoToneSidebandCooling)

    def subsequence(self):
        s = StatePreparation
        
        if s.enable_doppler_cooling:
            s.dopplerCooling.run(self)
        if s.enable_two_tone_sideband_cooling:
            s.ttsbc.run(self)
        if s.enable_optical_pumping:
            s.op.run(self)
        if s.enable_sideband_cooling:
            s.sbc.run(self)
        