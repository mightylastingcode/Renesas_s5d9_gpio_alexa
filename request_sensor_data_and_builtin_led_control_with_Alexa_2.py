'''

   Arthur: Michael Li
   Company: Contractor
   Date:  September 15th, 2017
   
   Project: GPIO with Diagnostics Intelligence
   
   Workflow Description: se Amazon Alexa to control built-in LEDs 
   (red/green/yellow leds) on the Renesas S5D9 board.
   
   Valid requests which users speak to Alexa:
   
   (Sensor Reading Intent)
   What is the current temperature?
   What is the current pressure?

    (Turn on/off GPIO LEDs Intent)
   Turn on red light.
   Turn off red light.
   Turn on green light.
   Turn off green light.
   Turn on yellow light.
   Turn off yellow light.

   
   *"Turn on the green light" is acceptable.  I found that "the" may cause Alexa's misinterpretation.

    (Blink GPIO LEDs Intent)
    Blink red light 0 time.
    Blink red light 1 time.
    Blink red light 3 times.
    Blink green light 0 time.
    Blink green light 1 time.
    Blink green light 3 times.
    Blink yellow light 0 time.
    Blink yellow light 1 time.
    Blink yellow light 3 times.

    *"Blink the green light 5 times" is acceptable.  I found that "the" may cause Alexa's misinterpretation.
   
   Error Detection:  For any violation such as "Turn on yellow light.", an appropriate response text message is 
                     sent back to Alexa.   So, users get a message that they would understand what the problem was. 
'''


import Alexa
import Analytics
import MQTT

# This function construct the response message back to 
# Amazon.  Amazon will translate this text message into 
# a voice message.
def build_response(title, output):
    return {
        'version': '1.0',
        'sessionAttributes': {},
        'response' : {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'card': {
                'type': 'Simple',
                'title': 'SessionSpeechlet - ' + title,
                'content': 'SessionSpeechlet - ' + output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': ""
                }
            },
            'shouldEndSession': True
        }
    }

################################################################################
#               Main Program Start                                             #
################################################################################

# Get the user request from Alexa

event = IONode.get_event()
request = event['request']
uuid_marker = event.get("uuid", "")

###################################
# Processing the request intent   # 
###################################

log ("Request type: {0}.".format(request['type']))
if request['type'] == 'IntentRequest':
    log ("Intent name: {0}.".format(request['intent']['name']))
    #######################################################
    #         Sensor Reading Request                      #
    #######################################################
    if request['intent']['name'] == 'SensorStatusIntent':
        log ("Sensor value: {0}.".format(request['intent']['slots']['Sensor_Selection']['value']))
        sensor_data = request['intent']['slots']['Sensor_Selection']['value']
        log (sensor_data)
        if sensor_data in ['temperature', 'pressure']:
            if sensor_data == 'temperature':
                tag_name = "raw.temp3.avg"
            else: 
                tag_name = "raw.pressure.avg"
            val = Analytics.last_n_values(tag_name,1)
            if val:
                response_txt = "The most recent " + sensor_data + " is " + str(int(val[0][tag_name]))
                log (response_txt)
            else:
                response_txt = "I could not find any recent " + sensor_data + " values"
        else:
            log ("Error: Not temperature or pressure.")
    #######################################################
    #         LED Control Request                         #
    #######################################################
    elif request['intent']['name'] == 'ledControlIntent' or request['intent']['name'] == 'ledBlinkIntent':
        log ("Intent value: {0}.".format(request['intent']['slots']['led_Selection']['value']))
        led = request['intent']['slots']['led_Selection']['value']
        log (led)
        #
        #  Map the logical led number according to the led selection specification.
        #
        if led == 'red':
               led_number = 4
        elif led == 'green':
            led_number = 1
        elif led == 'yellow':
            led_number = 2  
        else:
            log ("Error: Unknown led.")
        #
        #   Turn on or off the LED
        # 
        if request['intent']['name'] == 'ledControlIntent':
            action = request['intent']['slots']['led_onoff']['value']
            log (action)            
            if action == 'on':
                MQTT.publish_event_to_client('s5d9', 'L'+ str(led_number) + ':1')
            elif action == 'off':
                MQTT.publish_event_to_client('s5d9', 'L'+ str(led_number) + ':0')
            else:
                log ("Error: Unknown action.")
            response_txt = "The " + led + " led is turned " + action + "."
        #
        #   Blink the LED for a number of times.
        #
        elif request['intent']['name'] == 'ledBlinkIntent':
        	blink_number = int(request['intent']['slots']['blink_num']['value'])
            log (blink_number)
            if blink_number == 0:
            	MQTT.publish_event_to_client('s5d9', 'L'+ str(led_number) + ':0')
                response_txt = "The " + led + " led is turned off."
            elif blink_number <= 5:
                MQTT.publish_event_to_client('s5d9', 'B'+ str(led_number) + ':' + str(blink_number))
                response_txt = "The " + led + " led blinks " + str(blink_number) + " times."
            else:
                  response_txt = "The number of blinks requested exceeds the limit of 5.  Your request has been denied."
        else:
            log ("Error: Unknown Intent.")
    else:
        log ("Error: Unknown Intent.")
    log (response_txt)
    response_json = build_response(request['intent']['name'], response_txt)
    log(response_json)
    Alexa.response(uuid_marker, response_json) 
else:
    log ("Error: Unknown request type.")
