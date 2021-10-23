from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.rabi_excitation2 import RabiExcitation2  #Fix this later
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *
from datetime import datetime
import h5py as h5
import numpy as np

class NLQMRamsey(PulseSequence):
    PulseSequence.accessed_params = {
        "Ramsey.wait_time",
        "Ramsey.selection_sideband",
        "Ramsey.order",
        "Ramsey.channel_729",
        "Ramsey.detuning",
        "Ramsey.repeat_each_measurement",
        "Ramsey.no_return",
        "Ramsey.bsb_pulse",
        "Ramsey.echo",
        "Ramsey.carrier_duration",
        "Rotation729L1.pi_time",
        "Rotation729L1.line_selection",
        "Rotation729L1.amplitude",
        "Rotation729L1.att",
        "Rotation729L1.bsb_amplitude",
        "Rotation729L1.bsb_att",
        "Rotation729L1.bsb_pi_time",
        "Rotation729G.pi_time",
        "Rotation729G.line_selection",
        "Rotation729G.amplitude",
        "Rotation729G.att",
        "RabiFlopping.detuning",
    }

    master_scans = [("Ramsey.wait_time", 1., 20., 1., "ms")]

    PulseSequence.scan_params.update(
        RamseyRepeat = [
            ("Ramsey", ("Ramsey.phase", 0., 360., 20, "deg"))
        ])

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.Ramsey.channel_729
        self.bsb_rabi = self.add_subsequence(RabiExcitation2)
        self.bsb_rabi.channel_729 = self.p.Ramsey.channel_729
        self.set_subsequence["Ramsey"] = self.set_subsequence_ramsey
        
        self.pi_time = self.p.Rotation729G.pi_time
        self.line_selection = self.p.Rotation729G.line_selection
        self.amplitude = self.p.Rotation729G.amplitude
        self.att = self.p.Rotation729G.att

        self.bsb_pi_time = self.p.Rotation729L1.bsb_pi_time
        self.bsb_amplitude = self.p.Rotation729L1.bsb_amplitude
        self.bsb_att = self.p.Rotation729L1.bsb_att
        self.wait_time = 0.
        self.phase = 0.
        self.N = self.p.Ramsey.repeat_each_measurement

        self.run_after["Ramsey"] = self.analyze_phase
        self.start_time = str(datetime.now().strftime("%H%M_%S"))

        self.calculated_phase = list()
        self.calculated_phase_error = list()
        self.calculated_contrast = list()
        self.calculated_contrast_error = list()
        self.calculated_offset = list()
        self.calculated_offset_error = list()

    @kernel
    def set_subsequence_ramsey(self):
        self.rabi.duration = self.Ramsey_carrier_duration #self.pi_time
        self.rabi.amp_729 = self.amplitude
        self.rabi.att_729 = self.att
        self.rabi.freq_729 = self.calc_frequency(
                    self.line_selection,
                    detuning=self.Ramsey_detuning,
                    sideband=self.Ramsey_selection_sideband,
                    order=self.Ramsey_order,
                    dds=self.Ramsey_channel_729
                )
        self.bsb_rabi.duration = self.bsb_pi_time
        self.bsb_rabi.amp_729 = self.bsb_amplitude
        self.bsb_rabi.att_729 = self.bsb_att
        self.bsb_rabi.freq_729 = self.calc_frequency(
                    self.line_selection,
                    detuning=self.RabiFlopping_detuning,
                    sideband=self.Ramsey_selection_sideband,
                    order=1.0,
                    dds=self.Ramsey_channel_729
                )
        self.wait_time = self.get_variable_parameter("Ramsey_wait_time")
        self.get_729_dds("729G")

    @kernel
    def Ramsey(self):
        self.rabi.phase_ref_time = now_mu()
        self.bsb_rabi.phase_ref_time = self.rabi.phase_ref_time
        self.stateprep.run(self)

        self.rabi.phase_729 = 0.
        self.rabi.run(self)
        if self.Ramsey_bsb_pulse:
            self.bsb_rabi.run(self)

        if not self.Ramsey_echo:
            delay_mu(self.core.seconds_to_mu(self.wait_time))
        else:
            delay_mu(self.core.seconds_to_mu(self.wait_time / 2))
            self.bsb_rabi.run(self)
            self.rabi.duration = self.pi_time
            self.rabi.run(self)
            self.rabi.duration = self.Ramsey_carrier_duration
            self.bsb_rabi.run(self)
            delay_mu(self.core.seconds_to_mu(self.wait_time / 2))

        if self.Ramsey_bsb_pulse and not self.Ramsey_no_return:
            self.bsb_rabi.phase_729 = 180.
            self.bsb_rabi.run(self)
        self.rabi.phase_729 = self.get_variable_parameter("Ramsey_phase")
        self.rabi.run(self)

    def analyze_phase(self):
        y = self.data.Ramsey.y[-1]

        # We assume that Ramsey phase scan has exactly 3 ordered points: [0, 90, 180] degrees.
        # We can double-check this by looking at actual x data
        x_actual = self.data.Ramsey.x

        A, δA, B, δB, ϕ, δϕ = analyze_phase(
                    y, repetitions=self.p.StateReadout.repeat_each_measurement
                )
        self.calculated_phase.append(ϕ)
        self.calculated_phase_error.append(δϕ)
        self.calculated_contrast.append(A)
        self.calculated_contrast_error.append(δA)
        self.calculated_offset.append(B)
        self.calculated_offset_error.append(δB)
        iterations = range(len(self.calculated_phase))

        self.rcg.plot(iterations, self.calculated_phase, tab_name="NLQM",
            plot_name="Phase", append=True, plot_title="Phase-" + self.start_time)
        self.rcg.plot(terations, self.calculated_contrast, tab_name="NLQM",
            plot_name="Contrast", append=True, plot_title="Contrast-" + self.start_time)
        self.rcg.plot(terations, self.calculated_offset, tab_name="NLQM",
            plot_name="Offset", append=True, plot_title="Offset-" + self.start_time)

        with h5.File("NLQM-" + self.start_time + ".h5", "w") as f:
            datagrp = f.create_group("scan_data")
            datagrp = f["scan_data"]
            datasets = {
                    "phase": self.calculated_phase, 
                    "phase_error": self.calculated_phase_error, 
                    "contrast": self.calculated_contrast, 
                    "contrast_error": self.calculated_contrast_error, 
                    "offset": self.calculated_offset, 
                    "offset_error": self.calculated_offset_error
                }
            try:
                for set in datasets.keys():
                    del datagrp[set]
            except:
                pass
            for set in datasets.keys():
                datagrp.create_dataset(set, data=datasets[set])
            
            params = f.create_group("parameters")
            for collection in self.p.keys():
                collectiongrp = params.create_group(collection)
                for key, val in self.p[collection].items():
                    collectiongrp.create_dastaset(key, data=str(val))

        #### Make sure ramsey time is recorded somewhere!


def analyze_phase(x, repetitions=1000):
    x = np.array(x)
    xerr = np.sqrt(x * (1 - x) / repetitions)
    #result
    B = (x[0] + x[2]) / 2
    N = x[1] - B
    D = x[0] - B
    ϕ = np.arctan2(N, D)
    A = np.sqrt(((x[2] - x[0])/2)**2 + ((2 * x[1] - x[0] - x[2])/2)**2)
    
    #error
    temp_a = xerr[2]**2 * (x[0] - x[1])**2 + xerr[1]**2 * (x[0] - x[2])**2 + xerr[0]**2 * (x[1] - x[2])**2
    temp_b = (x[0]**2 - 2 * x[0] * x[1] + 2 * x[1]**2 - 2 * x[1] *x[2] + x[2]**2)**2
    error_ϕ = np.sqrt(temp_a / temp_b)
    error_B = np.sqrt((1/4) * xerr[0]**2 + (1/4) * xerr[2]**2)
    temp_a_A = xerr[0]**2 * (x[0] - x[1])**2 + xerr[2]**2 * (x[1] - x[2])**2 + xerr[1]**2 * (x[0] - 2*x[1] + x[2])**2
    temp_b_A = x[0]**2 - 2 * x[0] * x[1] + 2 * x[1]**2 - 2 * x[1] * x[2] + x[2]**2
    error_A = np.sqrt(temp_a_A / temp_b_A)
    return ϕ, error_ϕ, A, error_A, B, error_B
