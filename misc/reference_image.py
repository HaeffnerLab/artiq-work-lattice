import labrad
import numpy as np
import matplotlib.pyplot as plt
import logging
import threading
import time
from artiq.experiment import *
from sipyco.pc_rpc import Client

logger = logging.getLogger(__name__)

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
        self.camera = cxn.nuvu_camera_server
        self.N = 500
        self.duration = p.get_parameter("StateReadout", "camera_readout_duration")["s"]
        self.camera_trigger_width = p.get_parameter("StateReadout", "camera_trigger_width")["s"]
        self.freq_397 = p.get_parameter("StateReadout", "frequency_397")["Hz"]
        self.freq_866 = p.get_parameter("StateReadout", "frequency_866")["Hz"]
        self.amp_397 = p.get_parameter("StateReadout", "amplitude_397")[""]
        self.amp_866 = p.get_parameter("StateReadout", "amplitude_866")[""]
        self.att_397 = p.get_parameter("StateReadout", "att_397")["dBm"]
        self.att_866 = p.get_parameter("StateReadout", "att_866")["dBm"]
        self.initial_xstart = p.get_parameter("PmtReadout", "camera_xstart")
        self.initial_xstop = p.get_parameter("PmtReadout", "camera_xstop")
        self.initial_ystart = p.get_parameter("PmtReadout", "camera_ystart")
        self.initial_ystop = p.get_parameter("PmtReadout", "camera_ystop")
        self.ion_number = self.p.get_parameter("IonsOnCamera", "ion_number")

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

    def run(self):
        self.krun1()
        self.camera.abort_acquisition()
        self.bright_images = self.get_data_from_camera()
        self.krun2()
        self.camera.abort_acquisition()
        self.dark_images = self.get_data_from_camera()
        self.camera.abort_acquisition()
    
    @kernel
    def krun1(self):
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
        for i in range(self.N):
            self.camera_ttl.pulse(self.camera_trigger_width)
            delay(self.duration)
            self.core.wait_until_mu(now_mu())
            delay(5*ms)
    
    @kernel
    def krun2(self):
        self.core.reset()
        for cpld in self.cpld_list:
            cpld.init()
        self.dds_397.set(self.freq_397, amplitude=self.amp_397)
        self.dds_397.set_att(self.att_397)
        self.dds_866.set(self.freq_866, amplitude=0.)
        self.dds_866.set_att(30.0)
        self.dds_866.sw.off()
        self.dds_397.sw.on()
        self.dds_854.sw.pulse(200*us)
        self.prepare_camera()
        self.core.break_realtime()
        for i in range(self.N):
            self.camera_ttl.pulse(self.camera_trigger_width)
            delay(self.duration)
            self.core.wait_until_mu(now_mu())
            delay(5*ms)
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
        camera.abort_acquisition()
        camera.create_bias_image()
        camera.set_processing_mode("bias_subtraction")
        self.initial_exposure = camera.get_exposure_time()
        exposure = self.duration
        horizontal_bin  = self.p.get_parameter("IonsOnCamera", "horizontal_bin")
        vertical_bin = self.p.get_parameter("IonsOnCamera", "vertical_bin")
        horizontal_min = self.p.get_parameter("IonsOnCamera", "horizontal_min")
        horizontal_max = self.p.get_parameter("IonsOnCamera", "horizontal_max")
        vertical_min = self.p.get_parameter("IonsOnCamera", "vertical_min")
        vertical_max = self.p.get_parameter("IonsOnCamera", "vertical_max")
        self.image_region = [int(horizontal_bin),
                             int(vertical_bin),
                             int(horizontal_min),
                             int(horizontal_max),
                             int(vertical_min),
                             int(vertical_max)]
        camera.set_image_region(*self.image_region)
        camera.set_exposure_time(exposure)
        self.initial_trigger_mode = camera.get_trigger_mode()
        camera.set_trigger_mode("EXT_LOW_HIGH")

    def prepare_camera(self):
        self.camera.set_number_images_to_acquire(self.N)
        self.camera.start_acquisition()

    def get_data_from_camera(self):
        acquired_images = []
        try:
            timeout_in_seconds = 60
            acquired_images = np.right_shift(self.camera.get_acquired_data(timeout_in_seconds), 16)
        except Exception as e:
             logger.error(e)
             logger.error("Camera acquisition timed out")
             camera_dock.enable_button()
             camera_dock.close_rpc()
             self.close_camera()
             return
        return acquired_images

    def analyze(self):
        try:
            image_region = self.image_region
            x_pixels = int((image_region[3] - image_region[2] + 1) / image_region[0])
            y_pixels = int((image_region[5] - image_region[4] + 1) / image_region[1])
            bright_images = np.reshape(self.bright_images, (self.N, y_pixels, x_pixels))
            dark_images = np.reshape(self.dark_images, (self.N, y_pixels, x_pixels))
            mapfunc = lambda x, h, v, s: np.sum(x[h:h+s, v:v+s])
            
            # only works for 1-3 ions at the moment
            if int(self.ion_number) == 1:
                dark_counts = list(map(np.sum, dark_images))
                bright_counts = list(map(np.sum, bright_images))
                offset = np.min(dark_counts)
                lb = np.mean(bright_counts) - offset
                ld = np.mean(dark_counts) - offset
                nc = lb / np.log(1 + lb / ld) + offset
                self.p.set_parameter("IonsOnCamera", "threshold1", nc)

            elif int(self.ion_number) == 2:
                tlh1 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_horizontal1")
                tlh2 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_horizontal2")
                tlv1 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_vertical1")
                tlv2 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_vertical2")
                sidelength1 = self.p.get_parameter("IonsOnCamera", "side_length1")
                sidelength2 = self.p.get_parameter("IonsOnCamera", "side_length2")

                dark_counts1 = list(map(np.sum, dark_images))
                bright_counts1 = list(map(np.sum, bright_images))
                offset = np.min(dark_counts1)
                lb = np.mean(bright_counts1) - offset
                ld = np.mean(dark_counts1) - offset
                nc = lb / np.log(1 + lb / ld) + offset
                self.p.set_parameter("IonsOnCamera", "threshold1", nc)

                dark_counts2 = list(map(np.sum, dark_images2))
                bright_counts2 = list(map(np.sum, bright_images2))
                offset = np.min(dark_counts2)
                lb = np.mean(bright_counts2) - offset
                ld = np.mean(dark_counts2) - offset
                nc = lb / np.log(1 + lb / ld) + offset
                self.p.set_parameter("IonsOnCamera", "threshold2", nc)
            
            elif int(self.ion_number) == 3:
                tlh1 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_horizontal1")
                tlh2 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_horizontal2")
                tlh3 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_horizontal3")
                tlv1 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_vertical1")
                tlv2 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_vertical2")
                tlv3 = self.p.get_parameter("IonsOnCamera", "top_left_pixel_vertical3")
                sidelength1 = self.p.get_parameter("IonsOnCamera", "side_length1")
                sidelength2 = self.p.get_parameter("IonsOnCamera", "side_length2")
                sidelength3 = self.p.get_parameter("IonsOnCamera", "side_length3")

                dark_counts1 = list(map(np.sum, dark_images1))
                bright_counts1 = list(map(np.sum, bright_images1))
                offset = np.min(dark_counts1)
                lb = np.mean(bright_counts1) - offset
                ld = np.mean(dark_counts1) - offset
                nc = lb / np.log(1 + lb / ld) + offset
                self.p.set_parameter("IonsOnCamera", "threshold1", nc)

                dark_counts2 = list(map(np.sum, dark_images2))
                bright_counts2 = list(map(np.sum, bright_images2))
                offset = np.min(dark_counts2)
                lb = np.mean(bright_counts2) - offset
                ld = np.mean(dark_counts2) - offset
                nc = lb / np.log(1 + lb / ld) + offset
                self.p.set_parameter("IonsOnCamera", "threshold2", nc)

                dark_counts3 = list(map(np.sum, dark_images3))
                bright_counts3 = list(map(np.sum, bright_images3))
                offset = np.min(dark_counts3)
                lb = np.mean(bright_counts3) - offset
                ld = np.mean(dark_counts3) - offset
                nc = lb / np.log(1 + lb / ld) + offset
                self.p.set_parameter("IonsOnCamera", "threshold3", nc)
            image = np.average(bright_images, axis=0)
        finally:
            try:
                self.close_camera()
            finally:
                camera_dock = Client("::1", 3288, "camera_reference_image")
                camera_dock.plot(image, image_region)
                camera_dock.enable_button()
                camera_dock.close_rpc()

    def close_camera(self):
        self.camera.set_trigger_mode(self.initial_trigger_mode)
        self.camera.set_exposure_time(self.initial_exposure)
        self.camera.set_image_region(1, 1, 
                                    int(self.initial_xstart), 
                                    int(self.initial_xstop), 
                                    int(self.initial_ystart), 
                                    int(self.initial_ystop))
        self.camera.start_live_display()
        self.cxn.disconnect()

    def compute_threshold(
                        self, bright_images, dark_images, parameter,
                        horizontal_start=0, vertical_start=0
                    ):
        dark_counts = list(map(np.sum, dark_images))
        bright_counts = list(map(np.sum, bright_images))
        offset = np.min(dark_counts)
        lb = np.mean(bright_counts) - offset
        ld = np.mean(dark_counts) - offset
        nc = lb / np.log(1 + lb / ld) + offset
        self.p.set_parameter("IonsOnCamera", "threshold1", nc)        


