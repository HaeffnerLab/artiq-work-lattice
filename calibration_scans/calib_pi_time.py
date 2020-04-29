import numpy as np
import labrad
from scipy.optimize import curve_fit
from pulse_sequence import PulseSequence, FitError
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *

class CalibPiTime(PulseSequence):
    PulseSequence.accessed_params = {
        "RabiFlopping.line_selection",
        "RabiFlopping.amplitude_729",
        "RabiFlopping.att_729",
        "RabiFlopping.channel_729",
        "RabiFlopping.duration",
        "RabiFlopping.selection_sideband",
        "RabiFlopping.order",
        "RabiFlopping.detuning",
    }

    PulseSequence.scan_params = dict(
        CalibPiTime=[
            ("Rabi", ("RabiFlopping.duration", 0., 100e-6, 20, "us")),
        ])

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.set_subsequence["CalibPiTime"] = self.set_subsequence_calibpitime

    @kernel
    def set_subsequence_calibpitime(self):
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

        # Uncomment this to enable ramping for RabiFlopping sequence
        if self.rabi.duration > 0:
            self.rabi.setup_ramping(self)

        self.rabi.att_729=self.get_variable_parameter("RabiFlopping_att_729")

    @kernel
    def CalibPiTime(self):
        self.stateprep.run(self)
        self.rabi.run(self)

    def run_finally(self):
        x = self.data.CalibPiTime.x
        y = self.data.CalibPiTime.y[-1]
        print("x: ", x)
        global_max = x[np.argmax(y)]
        try:
            # p0 is initial guesses for A, tau, tpi, phi, B
            p0 = [0.5, global_max, y, 0.0, 0.0]
            popt, pcov = curve_fit(gaussian_sinesquare, x, y, p0)
            A, tau, tpi, phi, B = popt
        except:
            raise FitError

        cxn = labrad.connect()
        p = cxn.parametervault
        p.set_parameter(
            "Rotation729G", "pi_time", U(tpi * 1e-6, "s")
        )
        cxn.disconnect() 

def gaussian_sinesquare(x, A, tau, tpi, phi, B):
    return 0.5 * A * (1 - np.exp(-(x**2)/2/(tau*1e-6)**2) * np.sin(2*2 * np.pi * (1/(4*tpi)) * 1e6 * x + phi)**2) + B
        
