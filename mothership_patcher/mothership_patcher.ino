#include <LedControl.h>

#define RED_COLOR 0

LedControl leds = LedControl(12,11,10,1);

int cnt = 0;

void setup() {
	//init serial
	Serial.begin(115200);
	//turn on leds
	leds.shutdown(RED_COLOR, false);
	//set brightness
	leds.setIntensity(RED_COLOR, 8);
}

void loop() {
	// put your main code here, to run repeatedly:
	delay(100);
	leds.clearDisplay(RED_COLOR);
	leds.setRow(RED_COLOR, 0, cnt);
	cnt++;
	if(cnt > 255){
		cnt = 0;
	}
}
