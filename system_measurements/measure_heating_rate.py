import numpy as np
from datetime import datetime
from pulse_sequence import PulseSequence, FitError
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class HeatingRate(PulseSequence):
    PulseSequence.accessed_params = {
        "CalibrationScans.calibration_channel_729",
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
        "Heating.scan_range"
    }
    
    master_scans = [("Heating.background_heating_time", 0., 100e-3, 20, "ms")]

    PulseSequence.scan_params.update(
            CalibRed=("CalibRed", [("Spectrum.sideband_detuning", -5e3, 5e3, 15, "kHz")]),
            CalibBlue=("CalibBlue", [("Spectrum.sideband_detuning", -5e3, 5e3, 15, "kHz")])
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.kernel_invariants.update({"sideband"})
        self.sideband = self.p.CalibrationScans.selection_sideband
        self.set_subsequence["CalibRed"] = self.set_subsequence_calibred
        self.set_subsequence["CalibBlue"] = self.set_subsequence_calibblue
        self.wait_time = 0.
        self.red_amps = list()
        self.blue_amps = list()
        self.wait_times = list()
        self.nbars = list()
        self.run_after["CalibRed"] = self.analyze_calibred
        self.run_after["CalibBlue"] = self.analyze_calibblue
        self.plotname = str(datetime.now().strftime("%Y-%m-%d")) + " - HeatingRates"

    @kernel
    def set_subsequence_calibred(self):
        delta = self.get_variable_parameter("Spectrum_sideband_detuning")
        rabi_line = self.CalibrationScans_sideband_calibration_line
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.CalibrationScans_sideband_calibration_amp
        self.rabi.att_729 = self.CalibrationScans_sideband_calibration_att
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.rabi.freq_729 = self.calc_frequency(
                rabi_line, delta, sideband=self.sideband, 
                order=-abs(self.CalibrationScans_order), dds=rabi_dds,
                bound_param="Spectrum_sideband_detuning"
            )
    
    @kernel
    def set_subsequence_calibblue(self):
        delta = self.get_variable_parameter("Spectrum_sideband_detuning")
        rabi_line = self.CalibrationScans_sideband_calibration_line
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.CalibrationScans_sideband_calibration_amp
        self.rabi.att_729 = self.CalibrationScans_sideband_calibration_att
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.rabi.freq_729 = self.calc_frequency(
                rabi_line, delta, sideband=self.sideband, 
                order=abs(self.CalibrationScans_order), dds=rabi_dds,
                bound_param="Spectrum_sideband_detuning"
            )

    @kernel
    def CalibRed(self):
        delay(1*ms)##
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        delay(self.Heating_background_heating_time)
        self.rabi.run(self)

    def analyze_calibred(self):
        x = self.data.CalibRed.x
        y = self.data.CalibRed.y
        global_max = x[np.argmax(y)]
        try:
            popt, pcov = curve_fit(gaussian, x, y, p0=[0.5, global_max, 2e-3])
            self.red_amps.append(popt[1])
        except:
            self.red_amps.append(np.nan)
            raise FitError

    @kernel
    def CalibBlue(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        delay(self.Heating_background_heating_time)
        self.rabi.run(self)

    def analyze_calibblue(self):
        x = self.data.CalibBlue.x
        y = self.data.CalibBlue.y
        global_max = x[np.argmax(y)]
        if np.max(y) < 0.1:
            raise FitError
        try:
            popt, pcov = curve_fit(gaussian, x, y, p0=[0.5, global_max, 2e-3])
            self.blue_amps.append(popt[1])
        except:
            self.blue_amps.append(np.nan)
            raise FitError
        try:
            R = self.red_amps[-1] / self.blue_amps[-1]
            nbar = R / (1 - R)
            self.nbars.append(nbar)
            self.wait_times.append(self.p.Heating.background_heating_time)
            self.rcg.plot(self.wait_times, self.nbars, tab_name="Current",
                    plot_title=self.plotname)
        except:
            pass


def gaussian(x, A, x0, sigma):
    return A * np.exp((-(x - x0)**2) / (2*sigma**2))

       
