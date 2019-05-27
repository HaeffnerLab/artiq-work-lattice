import labrad
import numpy as np
from artiq.experiment import *
from artiq.language.core import TerminationRequested
from labrad.units import WithUnit as U


class set_dopplercooling_and_statereadout(EnvExperiment):

    def build(self):
        self.cxn = labrad.connect()
        self.p = self.cxn.parametervault
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.pmt = self.get_device("pmt")

    def prepare(self):
        self.set_dataset("pmt_counts", [], broadcast=True)
        self.set_dataset("collection_duration", [1*ms])
        self.set_dataset("pmt_counts_866_off", [], broadcast=True)
        self.set_dataset("pulsed", [False], broadcast=True)
        self.freq_866 = self.p.get_parameter("DopplerCooling", "doppler_cooling_frequency_866")["MHz"]
        self.amp_866 = self.p.get_parameter("DopplerCooling", "doppler_cooling_amplitude_866")[""]
        self.att_866 = self.p.get_parameter("DopplerCooling", "doppler_cooling_att_866")["dBm"]
        self.background_level = 0.
        self.cpld_list = [self.get_device("urukul{}_cpld".format(i)) for i in range(3)]
        self.dds_names = list()
        self.dds_device_list = list()
        for key, val in self.get_device_db().items():
            if isinstance(val, dict) and "class" in val:
                if val["class"] == "AD9910" or val["class"] == "AD9912":
                    setattr(self, "dds_" + key, self.get_device(key))
                    self.dds_device_list.append(getattr(self, "dds_" + key))
                    try:
                        self.dds_names.append(key)
                    except KeyError:
                        continue
        # Grab cw parameters:
        # NOTE: Because parameters are grabbed in prepare stage,
        # loaded dds cw parameters may not be the most current.
        self.dds_list = list()
        self.freq_list = list()
        self.amp_list = list()
        self.att_list = list()
        self.state_list = list()
        dds_cw_parameters = dict()
        names = self.p.get_parameter_names("dds_cw_parameters")
        for name in names:
            param = self.p.get_parameter("dds_cw_parameters", name)[""]
            dds_cw_parameters[name] = param
        for key, settings in dds_cw_parameters.items():
            self.dds_list.append(getattr(self, "dds_" + key))
            self.freq_list.append(float(settings[1][0]) * 1e6)
            self.amp_list.append(float(settings[1][1]))
            self.att_list.append(float(settings[1][3]))
            self.state_list.append(bool(float(settings[1][2])))
        self.peak_freq_397 = -1
        self.peak_amp_397 = -1
        self.completed = False

    def run(self):
        self.initialize()
        
        freq_list = np.linspace(65*MHz, 85*MHz, 1000)
        self.freq_list = freq_list
        for i, freq in enumerate(freq_list):
            try:
                self.krun_freq(freq)
                self.scheduler.pause()
            except TerminationRequested:
                return
            data = self.get_dataset("pmt_counts")
            if i > 100:
                if data[-1] <= data[-2] and data[-2] <= data[-3] and data[-3] <= data[-4]:
                    self.peak_freq_397 = freq
                    break
        if self.peak_freq_397 == -1:
            self.peak_freq_397 = freq_list[-1]
        self.set_dc_freq()

        amp_list = np.linspace(0, 1, 1000)
        self.amp_list = amp_list
        for i, amp in enumerate(amp_list):
            try:
                self.krun_amp(self.peak_freq_397, amp)
                self.scheduler.pause()
            except TerminationRequested:
                return
            data = self.get_dataset("pmt_counts")
            if i > 100:
                if data[-1] <= data[-2] and data[-2] <= data[-3] and data[-3] <= data[-4]:
                    self.peak_amp_397 = freq
                    break
        if self.peak_amp_397 == -1:
            self.peak_amp_397 = freq_list[-1]
        self.set_dc_amp()

        self.completed = True
        self.reset_cw_settings()

    @kernel
    def initialize(self):
        self.turn_off_all()
        t_count = self.pmt.gate_rising(1*ms)
        self.background_level = self.pmt.count(t_count)
        self.dds_866.set(self.freq_866, amplitude=self.amp_866)
        self.dds_866.set(self.att_866)
        self.dds_866.sw.on()
        self.dds_397.set(65*MHz, amplitude=0.2)
        self.dds_397.sw.on()

    @kernel
    def turn_off_all(self):
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        for device in self.dds_device_list:
            device.init()
            device.sw.off()

    @kernel
    def reset_cw_settings(self):
        # Return the CW settings to what they were when prepare stage was run
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        self.core.break_realtime()
        for i in range(len(self.dds_list)):
            try:
                self.dds_list[i].init()
            except RTIOUnderflow:
                self.core.break_realtime()
                self.dds_list[i].init()
            self.dds_list[i].set(self.freq_list[i], amplitude=self.amp_list[i])
            self.dds_list[i].set_att(self.att_list[i]*dB)
            if self.state_list[i]:
                self.dds_list[i].sw.on()
            else:
                self.dds_list[i].sw.off()
    
    @kernel
    def krun_freq(self, freq):
        self.core.break_realtime()
        self.dds_397.set(freq)
        t_count = self.pmt.gate_rising(1*ms)
        pmt_count = self.pmt_count(t_count)
        self.append("pmt_counts", pmt_count)
        self.append("pmt_counts_866_off", -1)

    @kernel
    def krun_amp(self, freq, amp):
        self.core.break_realtime()
        self.dds_397.set(freq, amplitude=amp)
        t_count = self.pmt.gate_rising(1*ms)
        pmt_count = self.pmt_count(t_count)
        self.append("pmt_counts", pmt_count)
        self.append("pmt_counts_866_off", -1)

    # @rpc(flags={"async"})
    def append(self, dataset_name, data_to_append):
        if not dataset_name in self.dataset_length.keys():
            self.dataset_length[dataset_name] = 0

        if self.dataset_length[dataset_name] % 1000 == 0:
            self.set_dataset(dataset_name, [], broadcast=True)

        self.append_to_dataset(dataset_name, data_to_append)
        self.dataset_length[dataset_name] += 1

    def set_dc_freq(self):
        peak_freq_index = np.abs(self.freq_list - self.peak_freq_397).argmin()
        dc_freq = self.freq_list[peak_freq_index // 2] * 1e-6
        self.set_parameter("DopplerCooling", "doppler_cooling_amplitude_397", U(dc_freq, "MHz"))

    def set_dc_amp(self):
        peak_amp_index = np.abs(self.amp_list - self.peak_amp_397).argmin()
        dc_amp = self.freq_list[peak_amp_index // 3]
        self.set_parameter("DopplerCooling", "doppler_cooling_frequency_397", U(dc_amp, ""))

    def analyze(self):
        if self.completed:
            self.set_parameter("StateReadout", "amplitude_397", U(self.peak_amp_397, ""))
            freq = (self.peak_freq_397 - 3*MHz) * 1e-6
            self.set_parameter("StateReaodut", "frequency_397", U(freq, "MHz"))
        self.cxn.disconnect()