from artiq import *
from artiq.language import *
from artiq.experiment import *

class test_line_trigger(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("LTriggerIN")

    def prepare(self):
        self.set_dataset("pmt_counts", [], broadcast=True)

    @kernel
    def run(self):
        self.core.reset()
        start = self.core.mu_to_seconds(self.core.get_rtio_counter_mu())
        for i in range(100):
            try:
                t_count = self.LTriggerIN.gate_rising(16*ms)
                mu_time = self.LTriggerIN.timestamp_mu(t_count)
                time = self.core.mu_to_seconds(mu_time) - start
                if time > 0:
                    self.record_result(time)
                delay(100*us)
            except RTIOUnderflow:
                self.record_result(9999)
                self.core.break_realtime()
        #while True:
        #    while True:
        #        try:
        #            self.LTriggerIN.sample_input()
        #            result = self.LTriggerIN.sample_get()
        #            if result == 1:
        #                break
        #        except RTIOUnderflow:
        #            self.core.break_realtime()
        #            continue
        #    while True:
        #        try:
        #            self.LTriggerIN.sample_input()
        #            result = self.LTriggerIN.sample_get()
        #            if result == 0:
        #                self.record_result(0)
        #                break
        #        except RTIOUnderflow:
        #            self.core.break_realtime()
        #            continue

    @rpc(flags={"async"})
    def record_result(self, x):
        self.append_to_dataset("pmt_counts", x)
