from artiq.pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from artiq.experiment import *


class Spectrum(PulseSequence):
    PulseSequence.accessed_params.update(
        {"Excitation_729.channel_729",
         "Excitation_729.bichro",
         "Spectrum.manual_amplitude_729",
         "Spectrum.manual_excitation_time",
         "Spectrum.line_selection",
         "Spectrum.selection_sideband",
         "Spectrum.order",
         "Display.relative_frequencies",
         "StatePreparation.channel_729",
         "StatePreparation.optical_pumping_enable",
         "StatePreparation.sideband_cooling_enable"}
    )
    PulseSequence.scan_params.update(
        spectrum=("Spectrum",
            [("Spectrum.carrier_detuning", -150*kHz, 150*kHz, 100)])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)

    @kernel
    def spectrum(self):

        delay(1*ms)
        self.repump854.duration = param*ms
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)