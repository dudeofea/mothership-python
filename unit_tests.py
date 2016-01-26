#!/usr/bin/python
#
#	Unit tests for mothership engine
#
#	Uses a file of fake effects called "test_effects.py"
#
import unittest
from test_effects import *
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
		ans = numpy.array([1,1,0,0,0,1,1,1,0,0,0,1,1,0,0,0,1,1,1,0,0,0,1,1,0,0,0,1,1,1,0,0,0], 'f')
		self.assertEquals(list(sq.outs[0][0]), list(ans))

class TestEngine(unittest.TestCase):
	def setUp(self):
		self.engine = AudioEngine('test_effects.py')
	#test that all effects are listed
	def test_list_effects(self):
		ans = ['square_wave']
		effs= [e.__class__.__name__ for e in self.engine.get_effects()]
		self.assertEquals(effs, ans)
	#test that patching square_wave to output works
	def test_patch_output1(self):
		#set the hardware info ourselves
		self.engine.buffer_size, self.engine.sample_rate = 20, 20
		self.engine.effects[0].buffer_size, self.engine.effects[0].freq, self.engine.effects[0].sample_rate = self.engine.buffer_size, 4, self.engine.sample_rate
		#run the engine once
		self.engine.add_patch((0,0), self.engine.JACK_GLOBAL)
		out = self.engine.run()
		ans = numpy.array([1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0], 'f')
		self.assertEquals(out[0], ans)

if __name__ == '__main__':
	unittest.main()
