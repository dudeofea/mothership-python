#	Mothership audio engine, runs all effects (in the order added) and
#	processes inputs (from effects / global input) and outputs (same)

import sys, inspect

#effect class to override
class Effect(object):
	def process(self, inp, out):
		inp = []
		out = []

class AudioEngine(object):
	effects_namespace = {}
	def __init__(self, effects_path):
		execfile(effects_path, self.effects_namespace)
	def effect_names(self):
		names = []
		for name, obj in self.effects_namespace.iteritems():
			#find all items that are classes and have Effect as subclass
			if inspect.isclass(obj) and obj.__bases__[0].__name__ == 'Effect':
				names.append(obj.__name__)
		return names
