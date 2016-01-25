#	Mothership audio engine, runs all effects (in the order added) and
#	processes inputs (from effects / global input) and outputs (same)

import sys, inspect, time, numpy, jack
from threading import Thread

#effect class to override
class Effect(object):
	color = None
	color_raw = [255, 255, 255]
	inps = ()
	outs = ()
	def process(self):
		pass

class AudioEngine(object):
	effects = []
	patches = []
	running = True
	jack_client = None
	def __init__(self, effects_path):
		effects_namespace = {}
		execfile(effects_path, effects_namespace)
		# --- add the effects to ourselves
		for name, obj in effects_namespace.iteritems():
			#find all items that are classes and have Effect as subclass
			if inspect.isclass(obj) and obj.__bases__[0].__name__ == 'Effect':
				self.effects.append(obj)
		# --- compute the raw colors given the hex string
		for i in xrange(0, len(self.effects)):
			if self.effects[i].color:
				string = self.effects[i].color.replace('#', '')
				comp = [string[j:j+2] for j in range(0, len(string), 2)]
				self.effects[i].color_raw = [int(c, 16) for c in comp]
		# --- start the jack client and get relevant info
		self.jack_client = jack.Client('qtjackctl')
		self.jack_client.activate()	# start the client
		# register and connect to i/o ports
		self.jack_client.register_port('in', jack.IsInput)
		self.jack_client.register_port('out', jack.IsOutput)
		out_port_name = self.jack_client.get_client_name() + ':out'		# build string for output port
		for system_playback_port_number in (1, 2):
			self.jack_client.connect(out_port_name, "system:playback_{}".format(system_playback_port_number))
		# get info
		self.sample_rate = self.jack_client.get_sample_rate()
		self.buffer_size = self.jack_client.get_buffer_size()
		# --- set jackd info in each effect
		for i in xrange(0, len(self.effects)):
			self.effects[i].sample_rate = self.sample_rate
			self.effects[i].buffer_size = self.buffer_size
	def get_effects(self):
		return self.effects
	def activate(self):
		#start the audio thread
		self.audio_thread = Thread(target = self.audio_thread_fn)
		self.audio_thread.start()
	def deactivate(self):
		#stop the audio thread
		self.running = False
		if self.jack_client != None:
			self.jack_client.deactivate()
		if self.audio_thread != None:
			self.audio_thread.join()
	# i_ind / o_ind are length 2 tuples with the effect index and the port index
	def add_patch(self, i_ind, o_ind):
		self.patches.append((i_ind, o_ind))
	def audio_thread_fn(self):
		print "Starting audio...."
		while self.running:
			input_buffer = numpy.zeros((1,self.buffer_size), 'f')
			output_buffer= numpy.zeros((1,self.buffer_size), 'f')
			#run effects
			for x in xrange(0, len(self.effects)):
				self.effects[x].process()
			#transfer data across effects
			for p in self.patches:
				if p[0][0] < 0:
					pass
				else:				#input is an effect
					if p[1][0] < 0:		#ouput is global
						output_buffer += self.effects[p[0][0]].outs[p[0][1]]
					else:
						pass
			self.jack_client.process()
		print "Done audio"
