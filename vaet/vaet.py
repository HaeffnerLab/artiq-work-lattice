from pulse_sequence import PulseSequence
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from subsequences.bichro_excitation import BichroExcitation
from artiq.experiment import *


class VAET(PulseSequence):
    PulseSequence.accessed_params = {}

    PulseSequence.scan_params.update(
        VAET=[

        ]
    )

    def run_initially(self):
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opp = self.add_subsequence(OpticalPumpingPulsed)
        self.opc = self.add_subsequence(OpticalPumpingContinuous)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.ms = self.add_subsequence(BichroExcitation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["VAET"] = self.set_subsequence_vaet

    @kernel
    def set_subsequence_vaet(self):
        pass

    @kernel
    def VAET(self):
        delay(1*ms)
        self.dopplerCooling.run(self)
        if self.StatePreparation_pulsed_optical_pumping:
            self.opp.run(self)
        else:
            self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.duration = 100*us
            self.opc.run(self)