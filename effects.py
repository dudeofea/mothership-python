#	Mothership effects file, the audio engine manager takes these
#	as an input when starting up (you can specify another file if you'd like)

import numpy
from engine import Effect

# classic square wave effect
class square_wave(Effect):
	color = '#000000'
	freq = 2
	up_ind = 0		#floating index for start of plateau
	down_ind = 0	#floating index for end of plateau
	def process(self):
		interval = float(self.sample_rate) / (self.freq*2)		#the length of the plateaus and valleys
		self.outs = (numpy.zeros((1, self.buffer_size), 'f'),)
		while self.up_ind < self.buffer_size and self.down_ind < self.buffer_size:
			self.down_ind = self.up_ind+interval
			self.outs[0][:,int(self.up_ind):int(min(self.down_ind, self.buffer_size))] = 1.0
			self.up_ind = self.down_ind+interval
		print self.up_ind, self.down_ind
		self.up_ind -= self.buffer_size
