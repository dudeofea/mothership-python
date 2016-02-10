#!/usr/bin/python
# Modular Synth Program controller by wireless BLE Mothership Pedal
# modified from adafruit ble library github repo
import Adafruit_BluefruitLE
import time, uuid, bitarray, signal, numpy
from engine import AudioEngine

# Define service and characteristic UUIDs used by the UART service.
UART_SERVICE_UUID = uuid.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
TX_CHAR_UUID      = uuid.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')
RX_CHAR_UUID      = uuid.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')

# Define pedal requests / commands
CMD_UPDATE		= '1'
CMD_LIST		= '001'
CMD_MOD_SELECT	= '010'

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

# setup audio engine to run effects
engine = AudioEngine('effects.py')
engine.activate()
engine.add_patch(('sequencer', 0), ('sawtooth_wave', 0))
engine.add_patch(('sawtooth_wave', 0), ('enveloper', 0))
engine.add_patch(('square_wave', 0), ('enveloper', 1))
engine.add_patch(('enveloper', 0), engine.JACK_GLOBAL)
# for x in numpy.logspace(0, 3, 1000):
# 	engine.effects[4].inps[0] = x
# 	time.sleep(0.1)

# state variables for processing commands
op_bytes = 0				#how many operand bytes are left
current_command = None		#the current command we are processing
current_module = None		#the currently selected module
total_bits = None

# for handing device
stay_connected = True

def bits2int(array):
	val = 0
	pos = 1		#weight of position
	for x in xrange(len(array)-1,-1,-1):	#count backwards to 0
		if array[x]:
			val += pos
		pos *= 2
	return val

# ble listen thread
def main():
	#function to catch SIGINT and quit
	# def signal_handler(signal, frame):
	# 	global stay_connected
	# 	print "Quitting..."
	# 	stay_connected = False
	# 	engine.deactivate()
	# 	ble.disconnect_devices([UART_SERVICE_UUID])
	# 	exit(0)
	# signal.signal(signal.SIGINT, signal_handler)

	global stay_connected
	# Clear any cached data because both bluez and CoreBluetooth have issues with caching data and it going stale.
	ble.clear_cached_data()
	# Get the first available BLE network adapter and make sure it's powered on.
	adapter = ble.get_default_adapter()
	adapter.power_on()
	print('Using adapter: {0}'.format(adapter.name))

	# Disconnect any currently connected UART devices.  Good for cleaning up and
	# starting from a fresh state.
	print('Disconnecting any connected UART devices...')
	ble.disconnect_devices([UART_SERVICE_UUID])

	# Scan for UART devices.
	print('Searching for UART device...')
	try:
		adapter.start_scan()
		# Search for the first UART device found (will time out after 60 seconds
		# but you can specify an optional timeout_sec parameter to change it).
		device = ble.find_device(service_uuids=[UART_SERVICE_UUID])
		if device is None:
			raise RuntimeError('Failed to find UART device!')
	finally:
		# Make sure scanning is stopped before exiting.
		adapter.stop_scan()

	print('Connecting to device...')
	try:
		device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
	except dbus.exceptions.DBusException:
		print "dbus exception"
		exit(0)
	# to change the timeout.
	try:
		print('Discovering services...')
		device.discover([UART_SERVICE_UUID], [TX_CHAR_UUID, RX_CHAR_UUID])

		# Find the UART service and its characteristics.
		uart = device.find_service(UART_SERVICE_UUID)
		rx = uart.find_characteristic(RX_CHAR_UUID)
		tx = uart.find_characteristic(TX_CHAR_UUID)

		#function to receive data from device
		def received(data):
			global op_bytes, current_command, current_module, total_bits
			for d in data:
				bits = bitarray.bitarray()
				bits.frombytes(bytes(d))
				print('Received: {0}'.format(bits.to01()))
				if op_bytes == 0:		#new command
					current_command = None
					cmd_bits = bits.to01()
					if cmd_bits[:3] == CMD_LIST:			#list all effects (0 operands)
						print "LIST"
						effs = engine.get_effects()
						#send length first
						p1 = [len(effs)] + ['\n']
						tx.write_value(p1)
						#then names
						for e in effs:
							tx.write_value(e.__class__.__name__+'\n')
						#then colors
						for e in effs:
							c = e.color_raw
							c.append('\n')
							tx.write_value(c)
					elif cmd_bits[:3] == CMD_MOD_SELECT:	#select a new module
						op_bytes = 1	#the module itself
						current_command = CMD_MOD_SELECT
					elif cmd_bits[:1] == CMD_UPDATE:
						print "Update:", cmd_bits
						op_bytes = 1
						current_command = CMD_UPDATE
						total_bits = bits
					else:
						print "Unknown command:", bits[:2].to01()
				else:									#something else entirely
					if current_command == CMD_MOD_SELECT:
						mod = bits2int(bits) - 1
						current_module = mod
						print "Selecting module #", mod
					if current_command == CMD_UPDATE:
						total_bits += bits
						val = bits2int(total_bits[5:15])
						arg = bits2int(total_bits[1:5])
						print "Updating...", arg, val
						if current_module != None:
							if arg >= 0 and arg < len(engine.effects[current_module].inps):
								engine.effects[current_module].inps[arg] = val
					op_bytes -= 1
		rx.start_notify(received)

		while stay_connected:
			time.sleep(1)
	finally:
		# Make sure device is disconnected on exit.
		print "disconnecting..."
		device.disconnect()

ble.initialize()				# Initialize the BLE system.  MUST be called before other BLE calls!
ble.run_mainloop_with(main)		# Start the mainloop to process BLE events
