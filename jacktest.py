import jack, numpy

client = jack.Client('qtjackctl')
client.activate()	# start the client

# register and connect to i/o ports
client.register_port('in', jack.IsInput)
client.register_port('out', jack.IsOutput)
out_port_name = client.get_client_name() + ':out'		# build string for output port
for system_playback_port_number in (1, 2):
	client.connect(out_port_name, "system:playback_{}".format(system_playback_port_number))

# build the sound sample
duration = 		3
rate = 			client.get_sample_rate()
length = 		int(duration * rate)
buffer_size = 	client.get_buffer_size()
print "Sample Rate:", rate
print "Duration {}s".format(duration)
print "Samples:", length

time_index = numpy.linspace(0, duration, length)
frequency = 440
_output_samples = numpy.sin(2*numpy.pi * frequency * time_index)
output_samples = numpy.reshape(_output_samples.astype("f"), (1, length))
# add buffer of zeros as an input for jack
print "Buffer Size:", buffer_size
input_samples = numpy.zeros((1,buffer_size), 'f')

# process the i/o buffers with jack
for i in range(0, length - buffer_size, buffer_size):
	out_chunk = output_samples[:,i:i+buffer_size]
	client.process(out_chunk, input_samples)

raw_input()
client.deactivate()	# stop the client
