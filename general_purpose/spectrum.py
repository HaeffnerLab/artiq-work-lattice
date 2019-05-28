from pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class Spectrum(PulseSequence):
    PulseSequence.accessed_params.update(
        {"Excitation_729.rabi_excitation_frequency",
         "Excitation_729.rabi_excitation_amplitude",
         "Excitation_729.rabi_excitation_att",
         "Excitation_729.rabi_excitation_phase",
         "Excitation_729.channel_729",
         "Excitation_729.rabi_excitation_duration",
         "Excitation_729.line_selection",
         "StatePreparation.sideband_cooling_enable"}
    )
    PulseSequence.scan_params.update(
        spectrum=("Spectrum",
            [("Spectrum.carrier_detuning", -150*kHz, 150*kHz, 100, "kHz")])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["spectrum"] = self.set_subsequence_spectrum

    @kernel
    def set_subsequence_spectrum(self):
        delta = self.get_variable_parameter("Spectrum_carrier_detuning")
        rabi_line = self.rabi.line_selection
        rabi_dds = self.rabi.channel_729
        self.rabi.freq_729 = self.calc_frequency(rabi_line, delta, dds=rabi_dds,
                bound_param="Spectrum_carrier_detuning")
  
    @kernel
    def spectrum(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
        self.rabi.run(self)