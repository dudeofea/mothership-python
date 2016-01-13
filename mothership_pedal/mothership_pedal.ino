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

#define VERBOSE_MODE				   true  // If set to 'true' enables debug output
#define FACTORYRESET_ENABLE		       1
#define MINIMUM_FIRMWARE_VERSION	   "0.6.6"
#define MODE_LED_BEHAVIOUR		       "MODE"
#define BUTTON_LEFT				       51
#define BUTTON_CENTER			       52
#define BUTTON_RIGHT				   53

//pedal state variables
int r,g,b;
char name_buf[128];
int effects_len = -1;

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
    lcd.begin(16,2);
}

void loop() {
    // put your main code here, to run repeatedly:
    delay(150);
    //initialize if needed
    if(effects_len < 0){
    ble.print("AT+BLEUARTTX=");
    ble.println("LIST");
    // check response status
    if (! ble.waitForOK() ) {
        Serial.println(F("Failed to send?"));
    }
    // wait for response
    ble.println("AT+BLEUARTRX");
    ble.readline();
    if (strcmp(ble.buffer, "OK") == 0) {
        // no data
        return;
    }
    // Some data was found, its in the buffer
    Serial.print(F("[Recv] ")); Serial.println(ble.buffer);
        ble.waitForOK();
    }
}
