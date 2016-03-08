#!/usr/bin/python
#
#	Performance Tests for AudioEngine
#
import time
from engine import AudioEngine

engine = AudioEngine('effects')
engine.activate()

while engine.running:
	try:
		engine.add_effect(['blank'])
	except InputSyncError:
		break
	print len(engine.running_effects), engine.running_time
	time.sleep(0.1)
