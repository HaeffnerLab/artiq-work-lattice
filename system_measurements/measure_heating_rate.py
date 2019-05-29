from pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class HeatingRate1(PulseSequence):
    PulseSequence.accessed_params.update(
        {"RabiFlopping.line_selection",
         "RabiFlopping.amplitude_729",
         "RabiFlopping.att_729",
         "RabiFlopping.channel_729",
         "RabiFlopping.duration",
         "RabiFlopping.selection_sideband",
         "RabiFlopping.order",
         "RabiFlopping.detuning",
         "StatePreparation.sideband_cooling_enable"
         }
    )
    PulseSequence.scan_params.update(
        RabiFlopping=("Rabi",
            [("RabiFlopping.duration", 0., 100e-6, 20, "us")])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["RabiFlopping"] = self.set_subsequence_rabiflopping

    @kernel
    def set_subsequence_rabiflopping(self):
        self.rabi.duration = self.get_variable_parameter("RabiFlopping_duration")
        self.rabi.amp_729 = self.RabiFlopping_amplitude_729
        self.rabi.att_729 = self.RabiFlopping_att_729
        self.rabi.freq_729 = self.calc_frequency(
            self.RabiFlopping_line_selection, 
            detuning=self.RabiFlopping_detuning,
            sideband=self.RabiFlopping_selection_sideband,
            order=self.RabiFlopping_order, 
            dds=self.RabiFlopping_channel_729
        )

    @kernel
    def RabiFlopping(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
        self.rabi.run(self)


class HeatingRate2(PulseSequence):
    PulseSequence.accessed_params.update(
        {"RabiFlopping.line_selection",
         "RabiFlopping.amplitude_729",
         "RabiFlopping.att_729",
         "RabiFlopping.channel_729",
         "RabiFlopping.duration",
         "RabiFlopping.selection_sideband",
         "RabiFlopping.order",
         "RabiFlopping.detuning",
         "StatePreparation.sideband_cooling_enable"
         }
    )
    PulseSequence.scan_params.update(
        RabiFlopping=("Rabi",
            [("RabiFlopping.duration", 0., 100e-6, 20, "us")])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["RabiFlopping"] = self.set_subsequence_rabiflopping

    @kernel
    def set_subsequence_rabiflopping(self):
        self.rabi.duration = self.get_variable_parameter("RabiFlopping_duration")
        self.rabi.amp_729 = 0.1
        self.rabi.att_729 = self.RabiFlopping_att_729
        self.rabi.freq_729 = self.calc_frequency(
            self.RabiFlopping_line_selection, 
            detuning=self.RabiFlopping_detuning,
            sideband=self.RabiFlopping_selection_sideband,
            order=self.RabiFlopping_order, 
            dds=self.RabiFlopping_channel_729
        )

    @kernel
    def RabiFlopping(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
        self.rabi.run(self)