#
#	Mothership Audio Controller
#
#	Uses a seria monitor to read data from mothership arduino
#	pedal and select modules / edit their arguments
#
import sys

class AudioController(object):
	def __init__(self, engine):
		self.engine = engine
		with open('/dev/ttyACM0', 'r') as arduino:
			while 1:
				line = arduino.read()
				if len(line) > 0:
					sys.stdout.write(line)
	def update(self):
		self.engine.effects = ["hey"]
