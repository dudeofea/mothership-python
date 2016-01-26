#
#	Mothership unit tests effect file
#
#	"unit_tests.py" uses this to test the validity of the mothership engine
#	as well as the validity of some of these effects
#
import numpy
from engine import Effect

# classic square wave effect
class square_wave(Effect):
	color = '#000000'
	freq = 440
	up_ind = 0		#floating index for start of plateau
	def process(self):
		interval = float(self.sample_rate) / (self.freq*2)		#the length of the plateaus and valleys
		self.outs = (numpy.zeros((1, self.buffer_size), 'f'),)
		while self.up_ind < self.buffer_size:
			self.outs[0][:,int(self.up_ind):int(min(self.up_ind+interval, self.buffer_size))] = 1.0
			self.up_ind += 2 * interval
		self.up_ind -= self.buffer_size
