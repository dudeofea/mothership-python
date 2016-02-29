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

# setup audio controller and pass it the engine
controller = AudioController(engine)

# setup user console
console = ConsoleController(engine)

# quit
engine.deactivate()
controller.deactivate()
