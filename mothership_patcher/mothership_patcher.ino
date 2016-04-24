#include <Adafruit_LEDBackpack.h>
#include <Adafruit_GFX.h>
#include <LedControl.h>

#define RED_COLOR 0
#define GREEN_COLOR 1

LedControl leds = LedControl(12,11,10,2);				//LEDs for switchboard
Adafruit_AlphaNum4 anum = Adafruit_AlphaNum4();		//Alphanumeric Displays

int cnt = 0;

void setup() {
	//init serial
	Serial.begin(115200);
	//turn on leds
	leds.shutdown(RED_COLOR, false);
	leds.shutdown(GREEN_COLOR, false);
	//leds.shutdown(GREEN_COLOR, true);
	//set brightness
	leds.setIntensity(RED_COLOR, 8);
	leds.setIntensity(GREEN_COLOR, 8);
	leds.clearDisplay(RED_COLOR);
	leds.clearDisplay(GREEN_COLOR);
	//leds.setIntensity(GREEN_COLOR, 8);

	//init alphanumeric
	anum.begin(0x70);  // pass in the address
}

void loop() {
	// //LED Matrix test code (MAX7219)
	// delay(100);
	// leds.setRow(RED_COLOR, 0, cnt-3);
	// leds.setRow(RED_COLOR, 1, cnt-2);
	// leds.setRow(RED_COLOR, 2, cnt-1);
	// leds.setRow(RED_COLOR, 3, cnt);
	//
	// leds.setRow(GREEN_COLOR, 0, cnt-3);
	// leds.setRow(GREEN_COLOR, 1, cnt-2);
	// leds.setRow(GREEN_COLOR, 2, cnt-1);
	// leds.setRow(GREEN_COLOR, 3, cnt);
	// cnt++;
	// Serial.println(cnt);
	// if(cnt > 255){
	// 	cnt = 0;
	// }

	//Alphanumeric display test code (HT16K33V)
	// display every character,
	for (uint8_t i='!'; i<='z'; i++) {
		anum.writeDigitAscii(0, i);
		anum.writeDigitAscii(1, i+1);
		anum.writeDigitAscii(2, i+2);
		anum.writeDigitAscii(3, i+3);
		anum.writeDigitAscii(4, i+4);
		anum.writeDigitAscii(5, i+5);
		anum.writeDigitAscii(6, i+6);
		anum.writeDigitAscii(7, i+7);
		anum.writeDisplay();

		delay(300);
	}
}
