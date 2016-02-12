#!/usr/bin/python
#
#	Modular Synth Program controlled by wired mothership controller
#
import time, uuid, bitarray, signal, numpy
from engine import AudioEngine
from controller import AudioController

# setup audio engine to run effects
engine = AudioEngine('effects.py')
engine.activate()
#engine.add_patch(('sequencer', 0), ('sawtooth_wave', 0))
engine.add_patch(('sawtooth_wave', 0), ('enveloper', 0))
engine.add_patch(('square_wave', 0), ('enveloper', 1))
engine.add_patch(('enveloper', 0), engine.JACK_GLOBAL)
# for x in numpy.logspace(0, 3, 1000):
# 	engine.effects[4].inps[0] = x
# 	time.sleep(0.1)

# setup audio controller and pass it the engine
controller = AudioController(engine)

print engine.get_effects()
