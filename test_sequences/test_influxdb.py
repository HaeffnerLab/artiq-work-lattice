import random
import time
from artiq.experiment import *


class FloppingF(EnvExperiment):
	"""InfluxExample"""

	def run(self):
		while True:
			x = 1*random.random()
			# InfluxDB bridge processes datasets with persist=True
			self.set_dataset("rand.x1", x*1, persist=True, save=False, broadcast=False)
			self.set_dataset("rand.x2", x*2, persist=True, save=False, broadcast=False)
			self.set_dataset("rand.x3", x*3, persist=True, save=False, broadcast=False)
			time.sleep(1)
