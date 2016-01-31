#!/usr/bin/python
#
#	Unit tests for mothership engine
#
#	Uses a file of fake effects called "test_effects.py"
#
import unittest
from effects import *
from engine import *

class TestEffects(unittest.TestCase):
	#test square wave with a variety of inputs
	def test_square_wave1(self):
		buffer_size, freq, sample_rate = 4, 1, 4
		sq = square_wave()
		sq.buffer_size, sq.freq, sq.sample_rate = buffer_size, freq, sample_rate
		sq.process()
		ans = numpy.array([1,1,0,0], 'f')
		self.assertEquals(len(sq.outs), 1)
		self.assertEquals(list(sq.outs[0][0]), list(ans))
	#larger buffer
	def test_square_wave2(self):
		buffer_size, freq, sample_rate = 8, 1, 4
		sq = square_wave()
		sq.buffer_size, sq.freq, sq.sample_rate = buffer_size, freq, sample_rate
		sq.process()
		ans = numpy.array([1,1,0,0,1,1,0,0], 'f')
		self.assertEquals(list(sq.outs[0][0]), list(ans))
	#slower frequency
	def test_square_wave3(self):
		buffer_size, freq, sample_rate = 8, 0.5, 4
		sq = square_wave()
		sq.buffer_size, sq.freq, sq.sample_rate = buffer_size, freq, sample_rate
		sq.process()
		ans = numpy.array([1,1,1,1,0,0,0,0], 'f')
		self.assertEquals(list(sq.outs[0][0]), list(ans))
	#slower freq and larger buffer
	def test_square_wave4(self):
		buffer_size, freq, sample_rate = 16, 0.5, 4
		sq = square_wave()
		sq.buffer_size, sq.freq, sq.sample_rate = buffer_size, freq, sample_rate
		sq.process()
		ans = numpy.array([1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0], 'f')
		self.assertEquals(list(sq.outs[0][0]), list(ans))
	#mismatch between freq and sample_rate/buffer_size
	def test_square_wave5(self):
		buffer_size, freq, sample_rate = 33, 2, 11
		sq = square_wave()
		sq.buffer_size, sq.freq, sq.sample_rate = buffer_size, freq, sample_rate
		sq.process()
		ans = numpy.array([1,1,1,0,0,1,1,1,0,0,0,1,1,1,0,0,0,1,1,0,0,0,1,1,1,0,0,1,1,1,0,0,0], 'f')
		self.assertEquals(list(sq.outs[0][0]), list(ans))
	#test that the square wave continues across buffers
	def test_square_wave6(self):
		buffer_size, freq, sample_rate = 8, 3, 16
		sq = square_wave()
		sq.buffer_size, sq.freq, sq.sample_rate = buffer_size, freq, sample_rate
		sq.process()
		ans = numpy.array([1,1,1,0,0,1,1,1], 'f')
		self.assertEquals(list(sq.outs[0][0]), list(ans))
		sq.process()
		ans = numpy.array([0,0,0,1,1,0,0,1], 'f')
		self.assertEquals(list(sq.outs[0][0]), list(ans))
	#test for really big sample rates and small buffers
	def test_square_wave7(self):
		buffer_size, freq, sample_rate = 20, 2, 80
		sq = square_wave()
		sq.buffer_size, sq.freq, sq.sample_rate = buffer_size, freq, sample_rate
		ans1 = numpy.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], 'f')
		ans2 = numpy.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'f')
		sq.process()
		self.assertEquals(list(sq.outs[0][0]), list(ans1))
		sq.process()
		self.assertEquals(list(sq.outs[0][0]), list(ans2))
		sq.process()
		self.assertEquals(list(sq.outs[0][0]), list(ans1))
		sq.process()
		self.assertEquals(list(sq.outs[0][0]), list(ans2))
	#test sawtooth wave similarly to square wave
	def test_sawtooth_wave1(self):
		buffer_size, freq, sample_rate = 4, 1, 4
		sw = sawtooth_wave()
		sw.buffer_size, sw.freq, sw.sample_rate = buffer_size, freq, sample_rate
		sw.process()
		ans = numpy.array([0.00, 0.25, 0.50, 0.75], 'f')
		self.assertEquals(len(sw.outs), 1)
		self.assertEquals(list(sw.outs[0][0]), list(ans))
	#test envelope genrator when using sq as env. and sw as wave
	def test_enveloper1(self):
		ev = enveloper()
		buffer_size, sample_rate = 4, 4
		ev.buffer_size, ev.sample_rate = buffer_size, sample_rate
		in1 = numpy.array([[0.00, 1.00, 1.00, 0.00]], 'f')
		in2 = numpy.array([[0.00, 0.25, 0.50, 0.75]], 'f')
		ans = numpy.array([0.00, 0.50, 1.00, 0.00], 'f')
		ev.inps = [in1, in2]
		ev.process()
		self.assertEquals(len(ev.outs), 1)
		self.assertEquals(list(ev.outs[0][0]), list(ans))

class TestEngine(unittest.TestCase):
	def setUp(self):
		self.engine = AudioEngine('effects.py')
	#test that all effects are listed
	def test_list_effects(self):
		ans = ['square_wave', 'sawtooth_wave', 'enveloper']
		effs= [e.__class__.__name__ for e in self.engine.get_effects()]
		contains_all = True
		for a in ans:
			self.assertTrue(effs.index(a) >= 0)
	#test that patching square_wave to output works
	def test_patch_output1(self):
		#set the hardware info ourselves
		self.engine.buffer_size, self.engine.sample_rate = 20, 20
		for x in xrange(0, len(self.engine.effects)):
			self.engine.effects[x].buffer_size, self.engine.effects[x].freq, self.engine.effects[x].sample_rate = self.engine.buffer_size, 2, self.engine.sample_rate
			self.engine.effects[x].setup()
		#run the engine once
		self.engine.add_patch((0,0), self.engine.JACK_GLOBAL)
		out = self.engine.run()
		ans = numpy.array([1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0], 'f')
		self.assertEquals(list(out[0]), list(ans))
	#test that patching square_wave / sawtooth_wave to enveloper works
	def test_patch_output2(self):
		#set the hardware info ourselves
		self.engine.buffer_size, self.engine.sample_rate = 20, 20
		for x in xrange(0, len(self.engine.effects)):
			self.engine.effects[x].buffer_size, self.engine.effects[x].freq, self.engine.effects[x].sample_rate = self.engine.buffer_size, 2, self.engine.sample_rate
			self.engine.effects[x].setup()
		#run the engine once
		self.engine.add_patch(('square_wave',0), ('enveloper', 0))
		self.engine.add_patch(('sawtooth_wave',0), ('enveloper', 1))
		self.engine.add_patch(('enveloper',0), self.engine.JACK_GLOBAL)
		self.engine.run()
		out = self.engine.run()
		ans = numpy.array([0,0.25,0.5,0.75,1,0,0,0,0,0,0,0.25,0.5,0.75,1,0,0,0,0,0], 'f')
		self.assertEquals(list(out[0]), list(ans))

if __name__ == '__main__':
	unittest.main()
