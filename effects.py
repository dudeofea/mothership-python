#	Mothership effects file, the audio engine manager takes these
#	as an input when starting up (you can specify another file if you'd like)

import numpy
from engine import Effect

# classic square wave effect
class square_wave(Effect):
	color = '#FF0000'
	ind = 0		#index to count with
	end_ind = 0	#index to count to
	def setup(self):
		#set inputs for running
		self.inps = [0]
	def process(self):
		if self.inps[0] == 0:
			self.inps[0] = self.args[0]
		if self.inps[0] == 0:
			return
		interval = float(self.sample_rate) / (self.inps[0]*2)		#the length of the plateaus and valleys
		if self.end_ind == 0:
			self.end_ind += interval
		#print "End index", self.end_ind
		self.outs = [numpy.zeros((1, self.buffer_size), 'f')]
		while self.ind < self.buffer_size:
			#print "Setting ind", self.ind
			self.outs[0][0][self.ind] = 1.0
			self.ind += 1
			if self.ind >= self.end_ind:
				#print "Done waveform"
				self.ind += interval
				self.end_ind += 2 * interval
		self.ind -= self.buffer_size
		self.end_ind -= self.buffer_size
		self.inps = [0]

# classic sawtooth wave effect
class sawtooth_wave(Effect):
	color = '#00FF00'
	slope_val = 0	#current value of the slope
	slope = 0		#how much to increment slope val
	ind = 0			#index to count with
	end_ind = 0		#index to count to
	def setup(self):
		#set inputs for running
		self.inps = [0]
	def process(self):
		if self.inps[0] == 0:
			self.inps[0] = self.args[0]
		if self.inps[0] == 0:
			return
		interval = float(self.sample_rate) / (self.inps[0])		#the length of the plateaus and valleys
		self.slope = 1 / interval
		if self.end_ind == 0:
			self.end_ind += interval
		#print "End index", self.end_ind
		self.outs = [numpy.zeros((1, self.buffer_size), 'f')]
		while self.ind < self.buffer_size:
			#print "Setting ind", self.ind
			self.outs[0][0][self.ind] = self.slope_val
			self.ind += 1
			self.slope_val += self.slope
			if self.ind >= self.end_ind:
				#print "Done waveform"
				self.slope_val = 0
				self.end_ind += interval
		self.ind -= self.buffer_size
		self.end_ind -= self.buffer_size
		self.inps = [0]

class sine_wave(Effect):
	color = '#0000FF'
	ind = 0			#index to count with
	end_ind = 0		#index to count to
	def setup(self):
		#set inputs for running
		self.inps = [440]
	def process(self):
		if self.inps[0] == 0:
			return
		interval = float(self.sample_rate) / (self.inps[0])		#the length of the plateaus and valleys

#takes a waveform and an envelope and returns an enveloped waveform
class enveloper(Effect):
	color = '#550000'
	def setup(self):
		#set inputs for running
		self.inps = [numpy.zeros((1, self.buffer_size), 'f')] * 2
	def process(self):
		#multiply
		self.outs = [numpy.multiply(self.inps[0], self.inps[1])]
		#normalize
		m = max(self.outs[0][0])
		if(m > 0):
			self.outs[0] /= m

#takes a waveform and an envelope and returns an enveloped waveform
class sequencer(Effect):
	color = '#005500'
	seq = [987.77, 1318.51, 1174.66]
	ind = 0
	cnt = 0
	period = 2
	def setup(self):
		#set swing offset to 0
		self.inps = [0]
	def process(self):
		self.outs = [self.seq[self.ind]]
		self.cnt += 1
		if self.cnt > self.period:
			self.cnt -= self.period
			self.ind += 1
			if self.ind >= len(self.seq):
				self.ind = 0

#spits out random noise
class white_noise(Effect):
	color = '#000055'
	def process(self):
		self.outs = numpy.random.rand(1, self.buffer_size)
