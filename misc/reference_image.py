import labrad
import numpy as np
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
        N = p.get_parameter("StateReadout", "repeat_each_measurement")
        self.N = int(N)
        self.duration = p.get_parameter("StateReadout", "camera_readout_duration")["s"]
        self.ctw = p.get_parameter("StateReadout", "camera_trigger_width")["s"]
        self.cta = p.get_parameter("StateReadout", "camera_transfer_additional")["s"]
        self.freq_397 = p.get_parameter("StateReadout", "frequency_397")["Hz"]
        self.freq_866 = p.get_parameter("StateReadout", "frequency_866")["Hz"]
        self.amp_397 = p.get_parameter("StateReadout", "amplitude_397")[""]
        self.amp_866 = p.get_parameter("StateReadout", "amplitude_866")[""]
        self.att_397 = p.get_parameter("StateReadout", "att_397")["dBm"]
        self.att_866 = p.get_parameter("StateReadout", "att_866")["dBm"]

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
        self.initialize_camera()
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        self.dds_397.set(self.freq_397, amplitude=self.amp_397)
        self.dds_397.set_att(self.att_397)
        self.dds_866.set(self.freq_866, amplitude=self.amp_866)
        self.dds_866.set_att(self.att_866)
        self.dds_866.sw.on()
        self.dds_397.sw.on()
        self.dds_854.sw.pulse(200*us)
        self.prepare_camera()
        self.core.break_realtime()
        for i in range(self.N * 2):
            self.core.break_realtime()
            self.camera_ttl.pulse(self.ctw)
            delay(self.duration)
            # delay(self.duration + self.cta)
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

    def initialize_camera(self):
        camera = self.camera
        # self.total_camera_confidences = []
        camera.abort_acquisition()
        self.initial_exposure = camera.get_exposure_time()
        exposure = self.duration
        horizontal_bin  = self.p.get_parameter("IonsOnCamera", "horizontal_bin")
        vertical_bin = self.p.get_parameter("IonsOnCamera", "vertical_bin")
        horizontal_min = self.p.get_parameter("IonsOnCamera", "horizontal_min")
        horizontal_max = self.p.get_parameter("IonsOnCamera", "horizontal_max")
        vertical_min = self.p.get_parameter("IonsOnCamera", "vertical_min")
        vertical_max = self.p.get_parameter("IonsOnCamera", "vertical_max")
        camera.set_exposure_time(exposure)
        self.image_region = [int(horizontal_bin),
                             int(vertical_bin),
                             int(horizontal_min),
                             int(horizontal_max),
                             int(vertical_min),
                             int(vertical_max)]
        camera.set_image_region(*self.image_region)
        camera.set_acquisition_mode("Kinetics")
        self.initial_trigger_mode = camera.get_trigger_mode()
        camera.set_trigger_mode("External")
        print(*self.image_region, self.N, self.duration)
        camera.set_number_kinetics(self.N)
        camera.start_acquisition()

    def prepare_camera(self):
        self.camera.abort_acquisition()
        self.camera.set_number_kinetics(self.N)
        self.camera.start_acquisition()

    def analyze(self):
        done = self.camera.wait_for_kinetic()
        if not done:
            print("uhohs")
            self.close_camera()
            return

        images = self.camera.get_acquired_data(int(self.N))
        image_region = self.image_region
        x_pixels = int((image_region[3] - image_region[2] + 1) / image_region[0])
        y_pixels = int((image_region[5] - image_region[4] + 1) / image_region[1])
        images = np.reshape(images, (self.N, y_pixels, x_pixels))
        self.close_camera()
        print(images)

    def close_camera(self):
        self.camera.abort_acquisition()
        self.camera.set_trigger_mode(self.initial_trigger_mode)
        self.camera.set_exposure_time(self.initial_exposure)
        self.camera.set_image_region(1, 1, 1, 658, 1, 496)
        self.camera.start_live_display()
        self.cxn.disconnect()

