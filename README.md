# Renesas_s5d9_gpio_alexa
Demo to show how to control GPIO LEDs with Amazon Alexa

This is a tutorial demo to show how you can speak requests to Amazon Alexa for turning on/off the LED's.   The green and red LEDs are connected to the white connectors of the newest Renesas S5D9 (Synergy family) board.  

1. Say to Alexa: "Alexa, ask Medium One.  Turn on red light"
 
2. The Amazon Alexa will extract which LED (red) and what action (on) your request specified.   It sends that information to Medium One IOT cloud server.

3. Medium One IOT cloud server process information.  It looks up which output pin is connected to the red LED.   Then, it changes the pin level "0" or "1" to turn off or on the LED.

Examples:
Say to Alexa: "Alexa, ask Medium One.  Turn on red light"
Say to Alexa: "Alexa, ask Medium One.  Turn off red light"
Say to Alexa: "Alexa, ask Medium One.  Turn on green light"
Say to Alexa: "Alexa, ask Medium One.  Turn off green light"
Say to Alexa: "Alexa, ask Medium One.  Blink red light 3 times"
Say to Alexa: "Alexa, ask Medium One.  Blink green light 5 times"

PS: The S5D9 board has both temperature and pressure sensors.

Say to Alexa: "Alexa, ask Medium One.  What is the current temperature?"
Say to Alexa: "Alexa, ask Medium One.  What is the current pressure?"
