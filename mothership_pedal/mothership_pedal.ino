//Includes for BLE UART library
#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_BLE.h>
#include <Adafruit_BluefruitLE_SPI.h>
#include <Adafruit_BluefruitLE_UART.h>
#include <LiquidCrystal.h>

//<serial_port>, <mode_pin (-1 is unused)>
Adafruit_BluefruitLE_UART ble(Serial1, -1);
LiquidCrystal lcd(22, 23, 27, 26, 25, 24);

#define VERBOSE_MODE				true  // If set to 'true' enables debug output
#define FACTORYRESET_ENABLE			1
#define MINIMUM_FIRMWARE_VERSION	"0.6.6"
#define MODE_LED_BEHAVIOUR			"MODE"
#define BUTTON_LEFT					51
#define BUTTON_CENTER				52
#define BUTTON_RIGHT				53
#define LCD_WIDTH					16

//pedal state variables
int sel_effect = 0;
int effects_len = -1;
char **effect_names = NULL;	 	//array of strings, names of effects
byte **effect_colors = NULL;	//array of 3-tuple bytes for colors

// A small helper
void error(const __FlashStringHelper*err) {
	Serial.println(err);
	while (1);
}

void setup_ble(){
	while (!Serial);  // required for Flora & Micro
	delay(500);

	Serial.begin(115200);
	Serial.println(F("Adafruit Bluefruit Command Mode Example"));
	Serial.println(F("---------------------------------------"));

	/* Initialise the module */
	Serial.print(F("Initialising the Bluefruit LE module: "));

	if ( !ble.begin(VERBOSE_MODE) ){
		error(F("Couldn't find Bluefruit, make sure it's in CoMmanD mode & check wiring?"));
	}
	Serial.println( F("OK!") );

	if ( FACTORYRESET_ENABLE ){
		/* Perform a factory reset to make sure everything is in a known state */
		Serial.println(F("Performing a factory reset: "));
		if ( ! ble.factoryReset() ){
			error(F("Couldn't factory reset"));
		}
	}

	/* Disable command echo from Bluefruit */
	ble.echo(false);

	Serial.println("Requesting Bluefruit info:");
	/* Print Bluefruit information */
	ble.info();

	Serial.println(F("Please use Adafruit Bluefruit LE app to connect in UART mode"));
	Serial.println(F("Then Enter characters to send to Bluefruit"));
	Serial.println();

	ble.verbose(false);  // debug info is a little annoying after this point!

	/* Wait for connection */
	while (! ble.isConnected()) {
		delay(500);
	}

	// LED Activity command is only supported from 0.6.6
	if ( ble.isVersionAtLeast(MINIMUM_FIRMWARE_VERSION) ){
		// Change Mode LED Activity
		Serial.println(F("******************************"));
		Serial.println(F("Change LED activity to " MODE_LED_BEHAVIOUR));
		ble.sendCommandCheckOK("AT+HWModeLED=" MODE_LED_BEHAVIOUR);
		Serial.println(F("******************************"));
	}
}

void setup() {
	//init RGB / Button pins
	// put your setup code here, to run once:
	pinMode(2, OUTPUT);
	pinMode(3, OUTPUT);
	pinMode(4, OUTPUT);
	pinMode(BUTTON_LEFT, INPUT_PULLUP);
	pinMode(BUTTON_CENTER, INPUT_PULLUP);
	pinMode(BUTTON_RIGHT, INPUT_PULLUP);
	//setup the ble controller
	setup_ble();
	//setup lcd screen
	lcd.begin(LCD_WIDTH, 2);
}

void ble_write(String s){
	ble.print("AT+BLEUARTTX=");
	ble.println(s);
	// check response status
	if (! ble.waitForOK() ) {
		Serial.println(F("Failed to send?"));
	}
}

int ble_read(){
	ble.println("AT+BLEUARTRX");
	ble.readline();
	if (strcmp(ble.buffer, "OK") == 0) {
		// no data
		return -1;
	}
	return 0;
}

void color_lcd(byte* colors){
	analogWrite(2, 255 - colors[2]);		//B
	analogWrite(3, 255 - colors[1]);		//G
	analogWrite(4, 255 - colors[0]);		//R
}

void loop() {
	// put your main code here, to run repeatedly:
	delay(150);
	//initialize if needed
	if(effects_len < 0){
		ble_write("LIST");
		//get length first (from hex value, max 255)
		if(ble_read() < 0){ return; }
		int len = ble.buffer[0];
		Serial.print(F("[len] ")); Serial.println(ble.buffer[0], DEC);
		Serial.print(F("[extra] ")); Serial.println(&ble.buffer[1]);
		ble.waitForOK();
		//allocate space (this assumes I either reset / clean up after myself)
		effect_names = (char**)malloc(sizeof(char*) * len);
		effect_colors= (byte**)malloc(sizeof(byte*) * len);
		//get effects names
		int i = 0;
		while(i < len){
			if(ble_read() == 0){
				Serial.print(F("[name] ")); Serial.println(ble.buffer);
				effect_names[i] = (char*)malloc(sizeof(char) * (LCD_WIDTH + 1));
				strncpy(effect_names[i], ble.buffer, LCD_WIDTH);
				ble.waitForOK();
				i++;
			}
		}
		//get effects colors
		i = 0;
		while(i < len){
			if(ble_read() == 0){
				Serial.print(F("[color] "));
				Serial.print(ble.buffer[0], HEX);
				Serial.print(ble.buffer[1], HEX);
				Serial.println(ble.buffer[2], HEX);
				effect_colors[i] = (byte*)malloc(sizeof(byte) * 3);
				memcpy(effect_colors[i], ble.buffer, sizeof(byte) * 3);
				Serial.print(F("[color2] "));
				Serial.print(effect_colors[i][0], DEC); Serial.print(F(" "));
				Serial.print(effect_colors[i][1], DEC); Serial.print(F(" "));
				Serial.println(effect_colors[i][2], DEC);
				ble.waitForOK();
				i++;
			}
		}
		effects_len = len;
	//scroll through possible screens
	}else{
		//color the lcd
		color_lcd(effect_colors[sel_effect]);
		//display name
		lcd.clear();
		lcd.setCursor(0,0);
		lcd.print(effect_names[sel_effect]);
		delay(1000);
	}
}
