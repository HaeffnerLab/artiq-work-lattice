import numpy as np
import labrad
import artiq.dashboard.drift_tracker.client_config as cl
from labrad.units import WithUnit as U 
from scipy.optimize import curve_fit
from pulse_sequence import PulseSequence, FitError
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class CalibAllLines(PulseSequence):
    PulseSequence.accessed_params.update(
        {"CalibrationScans.calibration_channel_729",
         "Spectrum.car1_amp",
         "Spectrum.car2_amp",
         "Spectrum.car1_att",
         "Spectrum.car2_att",
         "Spectrum.manual_excitation_time",
         "DriftTracker.line_selection_1",
         "DriftTracker.line_selection_2",
         "Display.relative_frequencies",
         "CalibrationScans.readout_mode",
         "StatePreparation.sideband_cooling_enable"}
    )

    fixed_params = [("Display.relative_frequencies", False),
                    ("StateReadout.readout_mode", "pmt")]

    PulseSequence.scan_params["CalibLine2"] = ("CalibLine2",
            [("Spectrum.carrier_detuning", -5e3, 5e3, 15, "kHz")])
    PulseSequence.scan_params["CalibLine1"] = ("CalibLine1",
            [("Spectrum.carrier_detuning", -5e3, 5e3, 15, "kHz")])


    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["CalibLine1"] = self.set_subsequence_calibline1
        self.set_subsequence["CalibLine2"] = self.set_subsequence_calibline2
        self.run_after["CalibLine1"] = self.analyze_calibline1
        self.run_after["CalibLine2"] = self.analyze_calibline2

    @kernel
    def set_subsequence_calibline1(self):
        delta = self.get_variable_parameter("Spectrum_carrier_detuning")
        rabi_line = self.DriftTracker_line_selection_1
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.Spectrum_car1_amp
        self.rabi.att_729 = self.Spectrum_car1_att
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.rabi.freq_729 = self.calc_frequency(rabi_line, delta, dds=rabi_dds,
                bound_param="Spectrum_carrier_detuning")
    
    @kernel
    def CalibLine1(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        self.rabi.run(self)
    
    def analyze_calibline1(self):
        x = self.data.CalibLine1.x
        y = self.data.CalibLine1.y
        global_max = x[np.argmax(y)]
        try:
            popt, pcov = curve_fit(gaussian, x, y, p0=[0.5, global_max, 2e-3])
            self.line1_peak = popt[1]
        except:
            raise FitError

    @kernel
    def set_subsequence_calibline2(self):
        delta = self.get_variable_parameter("Spectrum_carrier_detuning")
        rabi_line = self.DriftTracker_line_selection_2
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.Spectrum_car2_amp
        self.rabi.att_729 = self.Spectrum_car2_att
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.rabi.freq_729 = self.calc_frequency(rabi_line, delta, dds=rabi_dds,
                bound_param="Spectrum_carrier_detuning")
    
    @kernel
    def CalibLine2(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            self.opc.run(self)
        self.rabi.run(self)

    def analyze_calibline2(self):
        x = self.data.CalibLine2.x
        y = self.data.CalibLine2.y
        global_max = x[np.argmax(y)]
        if np.max(y) < 0.1:
            raise FitError
        try:
            popt, pcov = curve_fit(gaussian, x, y, p0=[0.5, global_max, 2e-3])
            self.line2_peak = popt[1]
        except:
            raise FitError

    def run_finally(self):
        line1 = self.p.DriftTracker.line_selection_1
        line2 = self.p.DriftTracker.line_selection_2
        carr1 = self.line1_peak
        carr2 = self.line2_peak
        if self.p.Display.relative_frequencies:
            pass
        submission = [(line1, U(carr1, "MHz")), (line2, U(carr2, "MHz"))]
        try:
            global_cxn = labrad.connect(cl.global_address, password=cl.global_password,
                                        tls_mode="off")
            global_cxn.sd_tracker_global.set_measurements(submission, cl.client_name)
        except:
            logger.error("Failed to connect to global drift tracker.", exc_info=True)
            return
        global_cxn.disconnect()


def gaussian(x, A, x0, sigma):
    return A * np.exp((-(x - x0)**2) / (2*sigma**2))