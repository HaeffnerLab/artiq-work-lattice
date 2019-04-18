from artiq import *
from artiq.language import *
from artiq.coredevice.exceptions import RTIOUnderflow

class test_line_trigger(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("LTriggerIN")

    def prepare(self):
        self.set_dataset("pmt_counts", [], broadcast=True)

    @kernel
    def run(self):
        self.core.reset()
        while True:
            try:
                self.LTriggerIN.sample_input()
                result = self.LTriggerIN.sample_get()
                if result == 1:
                    break
            except RTIOUnderflow:
                continue
        while True:
            self.core.break_realtime()
            self.LTriggerIN.sample_input()
            result = self.LTriggerIN.sample_get()
            if result == 0:
                break

    @rpc(flags={"async"})
    def record_result(self, x):
        self.append_to_dataset("pmt_counts", x)
