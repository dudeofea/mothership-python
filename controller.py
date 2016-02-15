#
#	Mothership Audio Controller
#
#	Uses a seria monitor to read data from mothership arduino
#	pedal and select modules / edit their arguments
#
import sys, serial

class AudioController(object):
	def __init__(self, engine):
		self.engine = engine
		with serial.Serial('/dev/ttyACM0', 115200) as arduino:
			buf = ""
			self.arduino = arduino
			while 1:
				chars = self.arduino.readline()
				buf += chars
				while 1:
					try:
						i = buf.index('\n')
						line = buf[:i]
						buf = buf[i+1:]		#skip newlin
						self.update(line.replace('\r', ''))
					except ValueError:
						break
	#process input line and possibly respond or update engine
	def update(self, line):
		spl = line.split(' ')
		if spl[0] == "UPD":		#update the current module with given values
			print line
			mod = int(spl[1])
			if mod < 0 or mod >= len(self.engine.effects):
				return
			for x in xrange(2, len(spl)-1):
				val = int(spl[x])
				self.engine.effects[mod].args[x-2] = val
		elif spl[0] == "LST":	#send a list of all modules we have
			#send length
			self.arduino.write(chr(len(self.engine.effects)))
			#send all module names
			for e in self.engine.effects:
				self.arduino.write(e.__name__+'\n')
			#send all module colors
			for e in self.engine.effects:
				for c in e.color_raw:
					self.arduino.write(chr(c))
		elif spl[0] == "CUR":	#send a list of current modules running
			#send length
			self.arduino.write(chr(len(self.engine.running_effects)))
			#send all module names
			for e in self.engine.running_effects:
				self.arduino.write(e.__class__.__name__+'\n')
			#send all module colors
			for e in self.engine.running_effects:
				for c in e.color_raw:
					self.arduino.write(chr(c))
		elif spl[0] == "ADD":	#add a new module to current modules
			print "Adding effect", spl[1]
			self.engine.add_effect([spl[1]])
		elif spl[0] == "ECHO":
			print line
		else:
			print "Unknown Command", line
