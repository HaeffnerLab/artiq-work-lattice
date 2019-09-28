import numpy as np
import labrad
import artiq.dashboard.drift_tracker.client_config as cl
from labrad.units import WithUnit as U 
from scipy.optimize import curve_fit
from pulse_sequence import PulseSequence, FitError
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *


class CalibSideband(PulseSequence):
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
    }

    PulseSequence.scan_params.update(
        CalibSideband=[
             ("Spectrum", ("Spectrum.sideband_detuning", -5e3, 5e3, 15, "kHz"))
        ])

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.rabi = self.add_subsequence(RabiExcitation)

        # Use calibration_channel_729 from CalibrationScans parameter group
        # instead of RabiFlopping.channel_729
        self.rabi.channel_729 = self.p.CalibrationScans.calibration_channel_729
        self.kernel_invariants.update({"sideband"})
        self.sideband = self.p.CalibrationScans.selection_sideband
        self.set_subsequence["CalibSideband"] = self.set_subsequence_calibsideband
        rt = self.rcg_tabs
        assert int(self.p.CalibrationScans.order) == self.p.CalibrationScans.order, "SB order needs to be int"
        if self.p.CalibrationScans.order < 0:
            rt["CalibSideband"]["Spectrum.sideband_detuning"] = "CalibRed"
        else:
            rt["CalibSideband"]["Spectrum.sideband_detuning"] = "CalibBlue"
        self.p.StateReadout.readout_mode = self.p.CalibrationScans.readout_mode

    @kernel
    def set_subsequence_calibsideband(self):
        delta = self.get_variable_parameter("Spectrum_sideband_detuning")
        rabi_line = self.CalibrationScans_sideband_calibration_line
        rabi_dds = self.CalibrationScans_calibration_channel_729
        self.rabi.amp_729 = self.CalibrationScans_sideband_calibration_amp
        self.rabi.att_729 = self.CalibrationScans_sideband_calibration_att
        self.rabi.duration = self.Spectrum_manual_excitation_time
        self.rabi.freq_729 = self.calc_frequency(
                rabi_line, delta, sideband=self.sideband, order=self.CalibrationScans_order, 
                dds=rabi_dds, bound_param="Spectrum_sideband_detuning"
            )
   
    @kernel
    def CalibSideband(self):
        self.stateprep.run(self)
        self.rabi.run(self)

    def run_finally(self):
        x = self.data.CalibSideband.x
        y = self.data.CalibSideband.y[-1]
        print("x: ", x)
        global_max = x[np.argmax(y)]
        try:
            popt, pcov = curve_fit(gaussian, x, y, p0=[0.5, global_max, 2e-3])
        except:
            raise FitError
        if self.p.Display.relative_frequencies:
            peak = popt[1] + self.p["TrapFrequencies"][self.p.CalibrationScans.selection_sideband]
        else:
            line = self.carrier_values[self.carrier_dict[self.p.CalibrationScans.sideband_calibration_line]]
            peak = popt[1] - (line + self.p["TrapFrequencies"][self.p.CalibrationScans.selection_sideband])

        cxn = labrad.connect()
        p = cxn.parametervault
        p.set_parameter(
            "TrapFrequencies", self.p.CalibrationScans.selection_sideband, U(peak * 1e-6, "MHz")
        )
        cxn.disconnect() 

def gaussian(x, A, x0, sigma):
    return A * np.exp((-(x - x0)**2) / (2*sigma**2))
