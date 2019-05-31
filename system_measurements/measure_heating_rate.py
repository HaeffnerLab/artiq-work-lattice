from pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class HeatingRate(PulseSequence):
    PulseSequence.accessed_params.update(
        {"CalibrationScans.calibration_channel_729",
         "CalibrationScans.sideband_calibration_amp",
         "CalibrationScans.sideband_calibration_att",
         "CalibrationScans.selection_sideband",
         "CalibrationScans.order",
         "Spectrum.manual_excitation_time",
         "CalibrationScans.sideband_calibration_line",
         "Display.relative_frequencies",
         "CalibrationScans.readout_mode",
         "StatePreparation.sideband_cooling_enable",
         "Heating.background_heating_time",
         "Heating.scan_range"}
    )

    
    PulseSequence.scan_params.update(
        Heating=("Spectrum",
            [("Heating.background_heating_time", 0., 100e-3, 20, "ms")])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.kernel_invariants.update({"sideband"})
        self.sideband = self.p.CalibrationScans.selection_sideband
        self.set_subsequence["CalibSideband"] = self.set_subsequence_heatingrate
        self.dynamically_generate_scans(
                PulseSequence.scan_params["Heating"],
                dict(
                    CalibRed=[("Spectrum.sideband_detuning", -5e3, 5e3, 15, "kHz")],
                    CalibBlue=[("Spectrum.sideband_detuning", -5e3, 5e3, 15, "kHz")]
                )
            )

    @kernel
    def set_subsequence_heatingrate(self):
        self.wait_time = self.get_variable_parameter("Heating_background_heating_time")
        rabi_line = self.CalibrationScans_sideband_calibration_line
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.CalibrationScans_sideband_calibration_amp
        self.rabi.att_729 = self.CalibrationScans_sideband_calibration_att
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.rabi.freq_729 = self.calc_frequency(
                rabi_line, 0., sideband=self.sideband, 
                order=self.CalibrationScans_order, dds=rabi_dds
            )

    @kernel
    def CalibRed(self):
        delay(1*ms)

    @kernel
    def CalibBlue(self):
        delay(1*ms)

       
