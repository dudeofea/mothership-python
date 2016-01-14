#	Mothership audio engine, runs all effects (in the order added) and
#	processes inputs (from effects / global input) and outputs (same)

import sys, inspect

#effect class to override
class Effect(object):
	color = None
	color_raw = [255, 255, 255]
	def process(self, inp, out):
		inp = []
		out = []

class AudioEngine(object):
	effects = []
	def __init__(self, effects_path):
		effects_namespace = {}
		execfile(effects_path, effects_namespace)
		#add the effects to ourselves
		for name, obj in effects_namespace.iteritems():
			#find all items that are classes and have Effect as subclass
			if inspect.isclass(obj) and obj.__bases__[0].__name__ == 'Effect':
				self.effects.append(obj)
		#compute the raw colors given the hex string
		for i in xrange(0, len(self.effects)):
			if self.effects[i].color:
				string = self.effects[i].color.replace('#', '')
				comp = [string[j:j+2] for j in range(0, len(string), 2)]
				self.effects[i].color_raw = [int(c, 16) for c in comp]
	def get_effects(self):
		return self.effects
