from artiq import *
from artiq.language import *

class test_save_data(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")

    def run(self):
        self.core.reset()
        self.set_dataset("test", [1,2,3], broadcast=True)
