#
#	Mothership audio engine, runs all effects (in the order added) and
#	processes inputs (from effects / global input) and outputs (same)
#
import sys, inspect, time, numpy, jack
from threading import Thread

#effect class to override
class Effect(object):
	color = None
	color_raw = [255, 255, 255]
	args = []
	inps = []
	outs = []
	def setup(self):
		pass
	def process(self):
		pass

class AudioEngine(object):
	effects = []			#all effects to choose from
	running_effects = []	#currently active effects
	patches = []			#patches between effects
	running = True
	jack_client = None
	JACK_GLOBAL = (-1, 0)	#global input / output port
	audio_thread = None
	def __init__(self, effects_path):
		self.effects = []
		self.patches = []
		self.running = True
		effects_namespace = {}
		execfile(effects_path, effects_namespace)
		# --- add the effects to ourselves
		for name, obj in effects_namespace.iteritems():
			#find all items that are classes and have Effect as subclass
			if inspect.isclass(obj) and obj.__bases__[0].__name__ == 'Effect':
				self.effects.append(obj)
		# --- sort all the effects by name
		self.effects.sort(key=lambda x: x.__name__)
		# --- compute the raw colors given the hex string
		for i in xrange(0, len(self.effects)):
			if self.effects[i].color:
				string = self.effects[i].color.replace('#', '')
				comp = [string[j:j+2] for j in range(0, len(string), 2)]
				self.effects[i].color_raw = [int(c, 16) for c in comp]
			#init arg values seperately from each other
			self.effects[i].args = [0] * 10
	def get_effects(self):
		return self.effects
	def activate(self):
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
		# --- set jackd info in each effect and run setup
		for i in xrange(0, len(self.effects)):
			self.effects[i].sample_rate = self.sample_rate
			self.effects[i].buffer_size = self.buffer_size
			self.effects[i].setup()
		#start the audio thread
		self.audio_thread = Thread(target = self.audio_thread_fn)
		self.audio_thread.start()
	def deactivate(self):
		#stop the audio thread
		self.running = False
		if self.audio_thread != None:
			self.audio_thread.join()
			self.audio_thread = None
		if self.jack_client != None:
			self.jack_client.deactivate()
			self.jack_client = None
	# get the index of a certain effect in self.effects
	def get_index(self, name):
		possible_inds = [i for i in xrange(0, len(self.effects)) if self.effects[i].__name__ == name]
		if len(possible_inds) == 0:
			raise ValueError('Could not find an effect named '+name)
		return possible_inds[0]
	# get the index of a certain running effect in self.running_effects
	def get_running_index(self, name):
		possible_inds = [i for i in xrange(0, len(self.running_effects)) if self.running_effects[i].__class__.__name__ == name]
		if len(possible_inds) == 0:
			raise ValueError('Could not find an effect named '+name)
		return possible_inds[0]
	# add an array of effects to running_effects from available effects
	def add_effect(self, effs):
		print effs
		for to_add in effs:
			ind = self.get_index(to_add)
			print "index for", to_add, ind
			self.running_effects.append(self.effects[ind]())
	# i_ind / o_ind are length 2 tuples with the effect index and the port index
	# effect index can also be replace with the string name
	def add_patch(self, i_ind, o_ind):
		#if input is string
		if type(i_ind[0]) == str:
			i_ind = (self.get_running_index(i_ind[0]), i_ind[1])
		#if output is string
		if type(o_ind[0]) == str:
			o_ind = (self.get_running_index(o_ind[0]), o_ind[1])
		self.patches.append((i_ind, o_ind))
	#continually call run and process the i/o to the audio buffers
	def audio_thread_fn(self):
		print "Starting audio...."
		try:
			while self.running:
			#for x in xrange(0, 40):
				input_buffer = numpy.zeros((1,self.buffer_size), 'f')
				output_buffer= self.run()
				#print sum(output_buffer)
				self.jack_client.process(output_buffer, input_buffer)
		except IndexError as err:
			#go through effects to see if one is missing a buffer
			for e in self.effects:
				if len(e.outs) == 0:
					print 'Effect "'+e.__class__.__name__+'" doesn\'t have an output_buffer'
					return
		print "Done audio"
	#run all effects, in any order, once and return the output buffer
	def run(self):
		output_buffer = numpy.zeros((1,self.buffer_size), 'f')
		for x in xrange(0, len(self.effects)):
			self.effects[x].process()
			#print self.effects[x].outs
		#transfer data across effects
		#print "Patches", self.patches
		for p in self.patches:
			if p[0][0] < 0:
				pass
			else:					#input is an effect
				#print "Patch", p[0][1], "effect", self.effects[p[0][0]].__class__.__name__
				if len(self.effects[p[0][0]].outs) > p[0][1]:	#if we have something to output
					if p[1][0] < 0:		#ouput is global
						output_buffer += self.effects[p[0][0]].outs[p[0][1]]
					else:				#output goes to another effect's input
						if len(self.effects[p[1][0]].inps) > p[1][1]:	#don't bother unless the spot exists
							self.effects[p[1][0]].inps[p[1][1]] = self.effects[p[0][0]].outs[p[0][1]]
							#print "patch:", p[1][1], self.effects[p[1][0]].inps
		return output_buffer
