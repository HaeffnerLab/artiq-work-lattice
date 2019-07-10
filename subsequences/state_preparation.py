from artiq.experiment import *
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous
from subsequences.sideband_cooling import SidebandCooling

class StatePreparation:
    enable_optical_pumping="StatePreparation.optical_pumping_enable"
    enable_pulsed_optical_pumping="StatePreparation.pulsed_optical_pumping"
    enable_sideband_cooling="StatePreparation.sideband_cooling_enable"
    sideband_cooling_cycles="SidebandCooling.sideband_cooling_cycles"
    
    def add_child_subsequences(self, pulse_sequence):
        self.dopplerCooling = pulse_sequence.add_subsequence(DopplerCooling)
        self.opp = pulse_sequence.add_subsequence(OpticalPumpingPulsed)
        self.opc = pulse_sequence.add_subsequence(OpticalPumpingContinuous)
        self.sbc = pulse_sequence.add_subsequence(SidebandCooling)

    @kernel
    def subsequence(self):
        s = StatePreparation

        delay(1*ms)
        self.dopplerCooling.run(self)
        if s.enable_pulsed_optical_pumping:
            self.opp.run(self)
        elif s.enable_optical_pumping:
            self.opc.run(self)

        if s.enable_sideband_cooling:
            num_cycles = int(s.sideband_cooling_cycles)
            for i in range(num_cycles):
                self.sbc.run(self)
                if s.enable_pulsed_optical_pumping:
                    self.opp.run(self)
                elif s.enable_optical_pumping:
                    self.opc.run(self)
