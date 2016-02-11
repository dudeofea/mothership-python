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
		with open('/dev/ttyACM0', 'r+') as arduino:
			buf = ""
			self.arduino = arduino
			while 1:
				chars = self.arduino.read()
				buf += chars
				while 1:
					try:
						i = buf.index('\n')
						line = buf[:i]
						buf = buf[i+1:]		#skip newlin
						self.update(line)
					except ValueError:
						break
	#process input line and possibly respond or update engine
	def update(self, line):
		spl = line.split(' ')
		if spl[0] == "UPD":		#update the current module with given values
			mod = int(spl[1])
			if mod < 0 or mod >= len(self.engine.effects):
				return
			for x in xrange(2, len(spl)-1):
				val = int(spl[x])
				self.engine.effects[mod].args[x-2] = val
		elif spl[0] == "LST":	#send a list of all module information
			#send length
			self.arduino.write(chr(len(self.engine.effects)))
			#send all module names
			for e in self.engine.effects:
				self.arduino.write(e.__class__.__name__+'\n')
			#send all module colors
			for e in self.engine.effects:
				for c in e.color_raw:
					self.arduino.write(chr(c))
		elif spl[0] == "ECHO":
			print line
