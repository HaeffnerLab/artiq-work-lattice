import labrad
from artiq.experiment import *


class ReferenceImage(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")
        self.dds_854 = self.get_device("854")
        self.setattr_device("camera_ttl")
        self.cpld_list = [self.get_device("urukul{}_cpld".format(i)) for i in range(3)]

    def prepare(self):
        cxn = labrad.connect()
        self.cxn = cxn
        p = cxn.parametervault
        self.p = p
        self.camera = cxn.andor_server
        self.cta = p.get_parameter("StateReadout", "camera_transfer_additional")["s"]
        duration = p.get_parameter("StateReadout", "camera_readout_duration")["s"]
        repump_additional = p.get_parameter("DopplerCooling", "doppler_cooling_repump_additional")["s"]
        self.freq_397 = p.get_parameter("StateReadout", "frequency_397")["Hz"]
        self.freq_866 = p.get_parameter("StateReadout", "frequency_866")["Hz"]
        self.amp_397 = p.get_parameter("StateReadout", "amplitude_397")[""]
        self.amp_866 = p.get_parameter("StateReadout", "amplitude_866")[""]
        self.att_397 = p.get_parameter("StateReadout", "att_397")["dBm"]
        self.att_866 = p.get_parameter("StateReadout", "att_866")["dBm"]
        N = p.get_parameter("StateReadout", "repeat_each_measurement")
        self.N = int(N)
        self.duration_397 = duration
        self.duration_866 = duration + repump_additional

        d = dict()
        d["dds_854"] = self.p.get_parameter("dds_cw_parameters", "854")[1]
        d["dds_397"] = self.p.get_parameter("dds_cw_parameters", "397")[1]
        d["dds_866"] = self.p.get_parameter("dds_cw_parameters", "866")[1]
        self.dds_list = list()
        self.freq_list = list()
        self.amp_list = list()
        self.att_list = list()
        self.state_list = list()
        for key, settings in d.items():
            self.dds_list.append(getattr(self, key))
            self.freq_list.append(float(settings[0]) * 1e6)
            self.amp_list.append(float(settings[1]))
            self.att_list.append(float(settings[3]))
            self.state_list.append(bool(float(settings[2])))

    @kernel
    def run(self):
        self.core.reset()
        i = 0
        #self.dds_397.set(self.freq_397, amplitude=self.amp_397)
        #self.dds_397.set_att(self.att_397)
        #self.dds_866.set(self.freq_866, amplitude=self.amp_866)
        #self.dds_866.set_att(self.att_866)
        #self.core.break_realtime()
        #self.dds_854.sw.pulse(200*us)
        #self.core.break_realtime()
        self.dds_866.sw.off()
        self.dds_397.sw.off()
        for i in range(self.N):
            self.core.break_realtime()
            with parallel:
                self.camera_ttl.pulse(self.cta)
                self.dds_397.sw.on()#self.duration_397)
                self.dds_866.sw.on()#self.duration_866)
            delay(1*ms)
            with parallel:
                self.dds_397.sw.off()
                self.dds_866.sw.off()
            delay(1*ms)

        self.reset_cw_settings()

    @kernel
    def reset_cw_settings(self):
        # Return the CW settings to what they were when prepare stage was run
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        with parallel:
            for i in range(len(self.dds_list)):
                self.dds_list[i].init()
                self.dds_list[i].set(self.freq_list[i], amplitude=self.amp_list[i])
                self.dds_list[i].set_att(self.att_list[i]*dB)
                if self.state_list[i]:
                    self.dds_list[i].sw.on()
                else:
                    self.dds_list[i].sw.off()

    def analyze(self):
        self.cxn.disconnect()

