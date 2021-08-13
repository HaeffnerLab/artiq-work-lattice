from pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from subsequences.rap import RAP
from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_RAMPUP, RAM_MODE_CONT_BIDIR_RAMP, RAM_MODE_CONT_RAMPUP
import numpy as np


class RAPFlop(PulseSequence):
    PulseSequence.accessed_params = {
        "RAP.amp_max",
        "RAP.att",
        "RAP.aux_strength",
        "RAP.aux_att",
        "RAP.beta",
        "RAP.channel_729",
        "RAP.detuning_max",
        "RAP.dp_amp",
        "RAP.dp_att",
        "RAP.duration",
        "RAP.line_selection",
        "RAP.order",
        "RAP.sideband_selection",
        "RAP.stark_shift",
    }

    PulseSequence.scan_params = dict(
        RAPFlop=[
            ("Current", ("RAP.duration", 100*us, 1000*us, 20, "us")),
            ("Current", ("RAP.stark_shift", 0., 1000*kHz, 20, "kHz")),
            ("Current", ("RAP.detuning_max", 0., 1000*kHz, 20, "kHz")),
            ("Current", ("RAP.beta", 0., 1.0, 20)),
            ("Current", ("RAP.aux_strength", 0., 1.0, 20)),
            ("Current", ("RAP.amp_max", 0., 1.0, 20))
        ]
    )

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.rap = self.add_subsequence(RAP)
        self.set_subsequence["RAPFlop"] = self.set_subsequence_rap_flop
        self.available_ram = 1024
        self.num_points = 1024
        self.less_points = self.available_ram - self.num_points
        self.t_dds = 5*ns
        self.amp_profile = [0] * self.available_ram
        self.freq_profile = [0] * self.available_ram
        self.amp_profile_raw = [0.0 for i in range(self.less_points)]
        self.step = 1
        for i in range(self.available_ram - self.less_points):
            val = 0.1 * np.sin(np.pi/2 + np.pi * i / (2 * self.num_points))
            if val < 0.0:
                val = 0.0
            elif val > 1.0:
                val = 1.0
            self.amp_profile_raw.append(val)
        self.freq_profile_raw = [0.0] * self.available_ram

    @kernel
    def set_subsequence_rap_flop(self):
        self.rap.T = self.get_variable_parameter("RAP_duration")
        self.rap.ss = self.get_variable_parameter("RAP_stark_shift")
        self.rap.delta = self.get_variable_parameter("RAP_detuning_max")
        self.rap.beta = self.get_variable_parameter("RAP_beta")
        self.rap.aux_strength = self.get_variable_parameter("RAP_aux_strength")
        self.rap.omega = self.get_variable_parameter("RAP_amp_max")
        
        n = self.num_points
        m = self.less_points
        T = self.rap.T
        t_dds = self.t_dds
        T = np.ceil(T / (n * t_dds)) * t_dds * 1024
        step = int((T / n) / t_dds / 2)
        self.step = step
        delta0 = self.rap.delta
        ss = self.rap.ss
        beta = self.rap.beta

        for i in range(m+1, self.num_points):
            self.freq_profile_raw[i] = 320*MHz + ss - ss * (beta**2 + np.sin(np.pi * i / n)**2) + delta0 * np.cos(np.pi * i / n)
        self.dds_RAP_amp.amplitude_to_ram(self.amp_profile_raw, self.amp_profile)
        self.dds_RAP_freq.frequency_to_ram(self.freq_profile_raw, self.freq_profile)
        
        self.core.break_realtime()
        self.setup_ram_modulation(
                3,
                ram_waveform=self.amp_profile,
                modulation_type=self.AMP_MOD,
                step=step,
                ram_mode=RAM_MODE_CONT_BIDIR_RAMP
            )
        self.setup_ram_modulation(
                4,
                ram_waveform=self.freq_profile,
                modulation_type=self.FREQ_MOD,
                step=step * 2,
                ram_mode=RAM_MODE_CONT_RAMPUP
            )

    @kernel
    def RAPFlop(self):
        self.setup_ram_modulation(
                3,
                ram_waveform=self.amp_profile,
                modulation_type=self.AMP_MOD,
                step=self.step,
                ram_mode=RAM_MODE_CONT_BIDIR_RAMP
            )
        self.setup_ram_modulation(
                4,
                ram_waveform=self.freq_profile,
                modulation_type=self.FREQ_MOD,
                step=self.step * 2,
                ram_mode=RAM_MODE_CONT_RAMPUP
            )
        self.stateprep.run(self)
        self.rap.run(self)

    def run_finally(self):
        self.stop_ram_modulation(self.dds_RAP_amp)
        self.stop_ram_modulation(self.dds_RAP_freq)
