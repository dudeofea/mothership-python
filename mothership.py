#!/usr/bin/python
#
#	Modular Synth Program controlled by wired mothership controller
#
import time, uuid, bitarray, signal, numpy, sys
from engine import AudioEngine
from controller import AudioController, ConsoleController

def sigint_handler(signal, frame):
	print('Quitting')
	engine.deactivate()
	controller.deactivate()
	exit(0)
signal.signal(signal.SIGINT, sigint_handler)

# setup audio engine to run effects
engine = AudioEngine('effects.py')
engine.activate()
engine.add_effect(['sequencer', 'sawtooth_wave', 'square_wave', 'enveloper'])
engine.add_patch(('sequencer', 0), ('sawtooth_wave', 0))
engine.add_patch(('sawtooth_wave', 0), ('enveloper', 0))
engine.add_patch(('square_wave', 0), ('enveloper', 1))
engine.add_patch(('enveloper', 0), engine.JACK_GLOBAL)
# for x in numpy.logspace(0, 3, 1000):
# 	engine.running_effects[2].inps[0] = x
# 	time.sleep(0.1)

# setup audio controller and pass it the engine
controller = AudioController(engine)

# setup user console
console = ConsoleController(engine)

# wait for a signal
signal.pause()
