#	Mothership effects file, the audio engine manager takes these
#	as an input when starting up (you can specify another file if you'd like)

import numpy
from scipy import signal
from engine import Effect

# helper function to turn freq. to note
def freq2note(freq):
	#0th octave notes
	notes = [('C', 16.35), ('Db', 17.32), ('D', 18.35), ('Eb', 19.45), ('E', 20.60), ('F', 21.83), ('Gb', 23.12), ('G', 24.50), ('Ab', 25.96), ('A', 27.50), ('B', 30.87)]
	octave_mul = 1
	octave = 0
	for x in xrange(0, 10):
		for n in notes:
			if freq < octave_mul*n[1]:
				return (n[0]+str(octave), octave_mul*n[1])
		octave_mul *= 2
		octave += 1

# classic square wave effect
class square_wave(Effect):
	color = '#EB4B98'
	ind = 0		#index to count with
	end_ind = 0	#index to count to
	def setup(self):
		#set inputs for running
		self.inps = [0]
	def process(self):
		freq = self.inps[0]
		if freq == 0 and len(self.args) >= 1:
			freq = self.args[0]
		if freq == 0:
			return
		interval = float(self.sample_rate) / (freq*2)		#the length of the plateaus and valleys
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
	def on_arg_change(self, ind, new_val):
		if ind == 0:
			self.args[ind] = float(new_val) / 10
			return str(self.args[ind])+"Hz"

# classic sawtooth wave effect
class sawtooth_wave(Effect):
	color = '#02394A'
	slope_val = 0	#current value of the slope
	slope = 0		#how much to increment slope val
	ind = 0			#index to count with
	end_ind = 0		#index to count to
	def setup(self):
		#set inputs for running
		self.inps = [0]
	def process(self):
		freq = self.inps[0]
		if freq == 0 and len(self.args) >= 1:
			freq = self.args[0]
		if freq == 0:
			return
		interval = float(self.sample_rate) / (freq)		#the length of the plateaus and valleys
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
	def on_arg_change(self, ind, new_val):
		if ind == 0:
			self.args[ind] = float(new_val) / 10
			return str(self.args[ind])+"Hz"

class sine_wave(Effect):
	color = '#043565'
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
	color = '#5158BB'
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
	color = '#F26DF9'
	ind = 0
	seq_len = 8
	cnt = 0
	def setup(self):
		self.inps = [0]
	def process(self):
		#takes default BPM from input, followed by arg #8
		bpm = self.inps[0]
		if bpm == 0:
			bpm = self.args[8]
		if bpm == 0:
			return
		period = 60 / (bpm)
		self.outs = [self.args[self.ind]]
		self.cnt += 1
		if self.cnt > period:
			self.cnt -= period
			self.ind += 1
			if self.ind >= self.seq_len:
				self.ind = 0
	def on_arg_change(self, ind, new_val):
		if ind < 8:
			note = freq2note(float(new_val) / 5)
			self.args[ind] = note[1]
			return "Beat "+str(ind+1)+": "+note[0]
		elif ind == 8:
			self.args[ind] = float(new_val) / 5
			return "BPM: "+str(self.args[ind])
		return super(sequencer, self).on_arg_change(ind, new_val)

#a multi-pole low pass filter
class low_pass(Effect):
	color = '#824C71'
	def setup(self):
		self.inps = [numpy.zeros((1, self.buffer_size), 'f')]
	def process(self):
		a = [1]				#a vector for y's
		b = [float(self.args[0]) / 1024]	#b vector for x's
		self.outs = [signal.lfilter(b, a, self.inps[0])]

#TODO: beat generator
#TODO: chordifier

#spits out random noise
class white_noise(Effect):
	color = '#000055'
	def process(self):
		self.outs = numpy.random.rand(1, self.buffer_size)
