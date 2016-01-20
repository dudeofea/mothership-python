# Modular Synth Program controller by wireless BLE Mothership Pedal
# modified from adafruit ble library github repo
import Adafruit_BluefruitLE
import time, uuid, bitarray, signal
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
effs = engine.get_effects()
# for e in effs:
# 	print e.__name__
# 	print list(e.color_raw)

# state variables for processing commands
op_bytes = 0				#how many operand bytes are left
current_command = None		#the current command we are processing
current_module = None		#the currently selected module

# for handing device
stay_connected = True
#function to catch SIGINT and quit
def signal_handler(signal, frame):
	global stay_connected
	print "Signal handler called"
	stay_connected = False
signal.signal(signal.SIGINT, signal_handler)

# ble listen thread
def main():
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
	device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
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
			global op_bytes, current_command, current_module
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
							tx.write_value(e.__name__+'\n')
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
					else:
						print "Unknown command:", bits[:2].to01()
				else:									#something else entirely
					if current_command == CMD_MOD_SELECT:
						print "Selecting module #", bits
					op_bytes -= 1
			# global data_split
			# for d in data:
			# 	if d == '\n':
			# 		print('Received: {0}'.format(list(data_split)))
			# 		if data_split.startswith('LIST'):	#list effect names
			# 			effs = engine.get_effects()
			# 			#pad first packet to 20 bytes to ensure it's separate
			# 			p1 = [len(effs)] + [' '] * 18 + ['\n']
			# 			tx.write_value(p1)	#send length first
			# 			for e in effs:
			# 				tx.write_value(e.__name__+'\n')
			# 			for e in effs:
			# 				c = e.color_raw
			# 				c.append('\n')
			# 				tx.write_value(c)
			# 		if data_split.startswith('U'):	#effect argument update
			# 			print list(data_split)
			# 		data_split = ""
			# 	else:
			# 		data_split += d
		rx.start_notify(received)

		while stay_connected:
			time.sleep(1)
	finally:
		# Make sure device is disconnected on exit.
		print "disconnecting..."
		device.disconnect()

ble.initialize()				# Initialize the BLE system.  MUST be called before other BLE calls!
ble.run_mainloop_with(main)		# Start the mainloop to process BLE events
