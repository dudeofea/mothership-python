# Modular Synth Program controller by wireless BLE Mothership Pedal
# modified from adafruit ble library github repo
import Adafruit_BluefruitLE
import time
from Adafruit_BluefruitLE.services import UART
from engine import AudioEngine

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

# setup audio engine to run effects
engine = AudioEngine('effects.py')
effs = engine.get_effects()
# for e in effs:
# 	print e.__name__
# 	print list(e.color_raw)

# ble listen thread
def main():
	# Clear any cached data because both bluez and CoreBluetooth have issues with
	# caching data and it going stale.
	ble.clear_cached_data()
	adapter = ble.get_default_adapter()		# Get the first available BLE network adapter and make sure it's powered on.
	adapter.power_on()
	#print('Using adapter: {0}'.format(adapter.name))
	print('Disconnecting any connected UART devices...')
	UART.disconnect_devices()
	# Scan for UART devices.
	print('Searching for UART device...')
	try:
		adapter.start_scan()
		# Search for the first UART device found (will time out after 60 seconds)
		device = UART.find_device()
		if device is None:
			raise RuntimeError('Failed to find UART device!')
	finally:
		# Make sure scanning is stopped before exiting.
		adapter.stop_scan()
	device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter to change the timeout.
	#actually start sending / receiving
	try:
		print('Discovering services...')
		UART.discover(device)	# time out after 60 seconds (specify timeout_sec parameter to override).
		#create instance of discovered device
		uart = UART(device)
		#read values from UART
		while True:
			#for some reason, the first message is received twice
			received = uart.read(timeout_sec=60)
			received = uart.read(timeout_sec=60)
			if received is not None:
				# Received data, print it out.
				print('Received: {0}'.format(received))
				if received.startswith('LIST'):	#list effect names
					effs = engine.get_effects()
					#pad first packet to 20 bytes to ensure it's separate
					p1 = [len(effs)] + [' '] * 18 + ['\n']
					uart.write(p1)		#send length first
					for e in effs:
						uart.write(e.__name__+'\n')
					for e in effs:
						c = e.color_raw
						c.append('\n')
						uart.write(c)
				if received.startswith('U'):	#effect argument update
					print received
			else:
				# Timeout waiting for data, None is returned.
				print('Received no data!')
	finally:
		# Make sure device is disconnected on exit.
		device.disconnect()

ble.initialize()				# Initialize the BLE system.  MUST be called before other BLE calls!
ble.run_mainloop_with(main)		# Start the mainloop to process BLE events
