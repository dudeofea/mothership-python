#
#	Mothership Audio Controller
#
#	Uses a seria monitor to read data from mothership arduino
#	pedal and select modules / edit their arguments
#
import sys, serial, os
from threading import Thread

class AudioController(object):
	def __init__(self, engine):
		self.engine = engine
		#start the serial listener thread
		self.serial_thread = Thread(target = self.serial_thread_fn)
		self.serial_thread.start()
	def deactivate(self):
		self.serial_thread.kill()
	def serial_thread_fn(self):
		#get first ttyACM* serial port
		serial_port = '/dev/ttyACM0'
		for l in os.listdir('/dev/'):
			if l.startswith('ttyACM'):
				serial_port = '/dev/' + l
		with serial.Serial(serial_port, 115200) as arduino:
			buf = ""
			self.arduino = arduino
			while 1:
				chars = self.arduino.readline()
				buf += chars
				while 1:
					try:
						i = buf.index('\n')
						line = buf[:i]
						buf = buf[i+1:]		#skip newline
						self.update(line.replace('\r', ''))
					except ValueError:
						break
	#process input line and possibly respond or update engine
	def update(self, line):
		spl = line.split(' ')
		if spl[0] == "UPD":		#update the current module with given values
			mod = int(spl[1])
			if mod < 0 or mod >= len(self.engine.running_effects):
				return
			for x in xrange(2, len(spl)-1):
				val = int(spl[x])
				self.engine.running_effects[mod].args[x-2] = val
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
			#print "Adding effect", spl[1]
			self.engine.add_effect([spl[1]])
		elif spl[0] == "ECHO":
			print line
		else:
			print "Unknown Command", line

class ConsoleController(object):
	def __init__(self, engine):
		self.engine = engine
		while 1:
			sys.stdout.write(">> ")
			cmd = raw_input()
			cmd = cmd.split(' ')
			if cmd[0] == "ls":
				for x in xrange(0, len(self.engine.running_effects)):
					print x, self.engine.running_effects[x].__class__.__name__
			elif cmd[0] == "lsall":
				for x in xrange(0, len(self.engine.effects)):
					print x, self.engine.effects[x].__name__
			elif cmd[0] == "patch" and len(cmd) == 3:
				i = cmd[1].split(',')
				o = cmd[2].split(',')
				self.engine.add_patch((int(i[0]), int(i[1])), (int(o[0]), int(o[1])))
			elif cmd[0] == "unpatch" and len(cmd) == 2:
				ind = int(cmd[1])
				self.engine.del_patch(ind)
			elif cmd[0] == "patches":
				for p in self.engine.patches:
					print p
			elif cmd[0] == "quit":
				return
			else:
				print "Unkown Command"
