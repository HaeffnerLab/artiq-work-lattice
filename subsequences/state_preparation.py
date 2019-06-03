from artiq.experiment import *
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous
from subsequences.sideband_cooling import SidebandCooling


class StatePreparation:
    enable_pulsed_optical_pumping="StatePreparation.pulsed_optical_pumping"
    enable_sideband_cooling="StatePreparation.sideband_cooling_enable"
    composite = [DopplerCooling, OpticalPumpingContinuous, OpticalPumpingPulsed,
                 SidebandCooling]

    @kernel
    def subsequence(self):
        s = StatePreparation
        self.dopplerCooling.run(self)
        if s.enable_pulsed_optical_pumping:
            self.opp.run(self)
        else:
            self.opc.run(self)
        if s.enable_sideband_cooling:
            self.sbc.run(self)
            self.opc.duration = 100*us
            self.opc.run(self)
