import labrad
from datetime import datetime
from artiq import *
from artiq.language import *
from artiq.coredevice.ad9910 import PHASE_MODE_CONTINUOUS

class pmtcollect(EnvExperiment):

    def build(self):
        self.cxn = labrad.connect()
        self.p = self.cxn.parametervault
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.pmt = self.get_device("pmt")
        self.cpld = self.get_device("urukul0_cpld")
        self.dds_866 = self.get_device("866")
        self.dds_397 = self.get_device("397")

    def run(self):
        self.core.reset()
        # Should we use np arrays ??
        self.set_dataset("pmt_counts", [], broadcast=True)
        self.set_dataset("time", [], broadcast=True)
        self.set_dataset("collection_duration", [])
        self.set_dataset("pmt_counts_866_off", [], broadcast=True)
        while True:
            # Must be a better way to pause?
            if not self.scheduler.check_pause():
                detection_time = self.get_detection_time()
                mode = self.get_mode()
                if not mode:
                    pmt_counts = self.run_continuously(detection_time)
                    pmt_counts_866_off = 0
                    diff_counts = pmt_counts
                else:
                    counts = self.run_pulsed(detection_time)
                    pmt_counts, pmt_counts_866_off = counts
                    diff_counts = pmt_counts - pmt_counts_866_off
                # dt = datetime.now().strftime("%H%M%S.%f")
                # t = round(float(dt), 3)
            elif len(self.scheduler.get_status()) > 1:
                print("we paused")
                self.core.close()
                self.scheduler.pause()
            else:
                print("we gone")
                break

    @kernel
    def run_continuously(self, detection_time):
        self.core.break_realtime()
        self.cpld.init()
        self.dds_866.init()
        self.dds_397.init()
        self.dds_397.set(75*MHz)
        self.dds_866.set(80*MHz)
        self.dds_397.set_att(22*dB)
        self.dds_866.set_att(22*dB)
        self.dds_866.sw.on()
        self.dds_397.sw.on()
        t_count = self.pmt.gate_rising(detection_time*ms)
        pmt_counts = self.pmt.count(t_count)
        # self.append_to_dataset("time",  t)
        self.append_to_dataset("pmt_counts", pmt_counts)
        self.append_to_dataset("collection_duration",
                                detection_time)
        return pmt_counts

    @kernel
    def run_pulsed(self, detection_time):
        self.core.break_realtime()
        self.cpld.init()
        self.dds_866.init()
        self.dds_397.init()
        self.dds_397.set(75*MHz)
        self.dds_866.set(80*MHz)
        self.dds_397.set_att(22*dB)
        self.dds_866.set_att(22*dB)
        self.dds_866.sw.on()
        self.dds_397.sw.on()
        t_count = self.pmt.gate_rising(detection_time*ms)
        pmt_counts = self.pmt.count(t_count)
        delay(500*us)
        self.dds_866.sw.off()
        t_count = self.pmt.gate_rising(detection_time*ms)
        pmt_counts_866_off = self.pmt.count(t_count)
        delay(500*us)
        # dt = datetime.now().strftime("%H%M%S.%f")
        # t = round(float(dt), 3)
        # self.append_to_dataset("time",  t)
        self.append_to_dataset("pmt_counts", pmt_counts)
        self.append_to_dataset("collection_duration",
                                detection_time)
        self.append_to_dataset("pmt_counts_866_off",
                                pmt_counts_866_off)
        # self.append_to_dataset("differential", diff_counts)

        return pmt_counts, pmt_counts_866_off

    def get_detection_time(self) -> TFloat:
        val = self.p.get_parameter(["PmtReadout", "duration"])["ms"]
        return val

    def get_mode(self) -> TBool:
        val = self.p.get_parameter(["PmtReadout", "pulsed"])
        return val

