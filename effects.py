#	Mothership effects file, the audio engine manager takes these
#	as an input when starting up (you can specify another file if you'd like)

from engine import Effect

# classic square wave effect
class square_wave(Effect):
	color = '#F15152'
	def process(self, inp, out):
		inp = []
		out = []

# classic square wave effect
class sine_wave(Effect):
	color = '#EDB183'
	def process(self, inp, out):
		inp = []
		out = []

# classic square wave effect
class triangle_wave(Effect):
	color = '#1E555C'
	def process(self, inp, out):
		inp = []
		out = []

if __name__ == '__main__':
	#print the info of all effects
	print "hey"
