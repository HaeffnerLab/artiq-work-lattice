from artiq.pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from artiq.experiment import *


class Spectrum(PulseSequence):
    PulseSequence.accessed_params.update(
        {"Excitation_729.rabi_excitation_frequency",
         "Excitation_729.rabi_excitation_amplitude",
         "Excitation_729.rabi_excitation_att",
         "Excitation_729.rabi_excitation_phase",
         "Excitation_729.channel_729",
         "Excitation_729.rabi_excitation_duration"}
    )
    PulseSequence.scan_params.update(
        spectrum=("Spectrum",
            [("Spectrum.carrier_detuning", -150*kHz, 150*kHz, 100)])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.rabi = self.add_subsequence(RabiExcitation)

    @kernel
    def spectrum(self):
        delta = self.get_variable_parameter("Spectrum_carrier_detuning")
        opc_line = self.opc.line_selection
        opc_dds = self.opc.channel_729
        rabi_dds = self.rabi.channel_729
        self.opc.freq_729 = self.calc_frequency(opc_line, dds=opc_dds)
        self.rabi.freq_729 = self.calc_frequency(opc_line, delta, dds=rabi_dds,
                bound_param="Spectrum_carrier_detuning")
        
        delay(1*ms)

        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        self.rabi.run(self)