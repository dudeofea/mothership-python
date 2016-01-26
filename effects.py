#	Mothership effects file, the audio engine manager takes these
#	as an input when starting up (you can specify another file if you'd like)

from engine import Effect

# classic square wave effect
class square_wave(Effect):
	color = '#F15152'
	freq = 440
	def process(self):
		value = 0.0
		interval = self.sample_rate / self.freq
		self.outs = (numpy.zeros((1, self.buffer_size), 'f'),)
		for x in xrange(0, self.buffer_size - interval, interval):
			self.outs[0][:,x:x+self.buffer_size] = value
			if value == 0.0:
				value = 1.0
			else:
				value = 0.0
