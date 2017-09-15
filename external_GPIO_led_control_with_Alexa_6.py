'''

   Arthur: Michael Li
   Company: Contractor
   Date:  September 15th, 2017
   
   Project: GPIO with Diagnostics Intelligence
   
   Workflow Description: se Amazon Alexa to control external LEDs 
   connected to the Groves J3 and J4 on the Renesas S5D9 board.
   
   Valid requests which users speak to Alexa:
   
   (Sensor Reading Intent)
   What is the current temperature?
   What is the current pressure?

	(Turn on/off GPIO LEDs Intent)
   Turn on red light.
   Turn off red light.
   Turn on green light.
   Turn off green light.
   
   *"Turn on the green light" is acceptable.  I found that "the" may cause Alexa's misinterpretation.

	(Blink GPIO LEDs Intent)
    Blink red light 0 time.
    Blink red light 1 time.
    Blink red light 3 times.
    Blink green light 0 time.
    Blink green light 1 time.
    Blink green light 3 times.

	*"Blink the green light 5 times" is acceptable.  I found that "the" may cause Alexa's misinterpretation.
   
   Error Detection:  For any violation such as "Turn on yellow light.", an appropriate response text message is 
                     sent back to Alexa.   So, users get a message that they would understand what the problem was. 
'''

import Alexa
import Analytics
import MQTT
import time

greenledpin = 'G4:11' # Grove UART J3 P4_11
redledpin   = 'G1:1'  # Grove I2C J4 P1_01

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

errorflag = False     #  set flag if the request cannot be met by this workflow.

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
                errorflag = True
                response_txt = "I could not find any recent " + sensor_data + " values"
        else:
            errorflag = True;
            response_txt = "Problem.  It is neither temperature nor pressure data request."
            log ("Error: Not temperature or pressure.")
    #######################################################
    #         LED Control Request                         #
    #######################################################
    elif request['intent']['name'] == 'ledControlIntent' or request['intent']['name'] == 'ledBlinkIntent':
        log ("Intent value: {0}.".format(request['intent']['slots']['led_Selection']['value']))
        led = request['intent']['slots']['led_Selection']['value']
        log (led)
        #
        #  Map the physical GPIO pin name according to the led selection specification.
        #
        if led == 'red':
            ledpin = redledpin
        elif led == 'green':
            ledpin = greenledpin
        elif led == 'yellow':
            errorflag = True
            response_txt = "Problem.  The external yellow l e d does not exist."           
            log ("Error: no external yellow led.")
        else:
            errorflag = True
            response_txt = "Problem.  The external l e d does not exist."           
            log ("Error: Unknown led.")
        #
        #   Turn on or off the LED
        #
        if request['intent']['name'] == 'ledControlIntent' and errorflag == False:
            action = request['intent']['slots']['led_onoff']['value']
            log (action)              
            if action == 'on':
                MQTT.publish_event_to_client('s5d9', ledpin + ':0')
            elif action == 'off':
                MQTT.publish_event_to_client('s5d9', ledpin + ':1')             
            else:
                errorflag = True
                response_txt = "Problem.  The request action for l e d does not exist."
                log ("Error: Unknown action.")
            if (errorflag == False):    
                response_txt = "The external " + led + " l e d is turned " + action + "."
        #
        #   Blink the LED for a number of times.
        #
        elif request['intent']['name'] == 'ledBlinkIntent' and errorflag == False:
            blink_number = int(request['intent']['slots']['blink_num']['value'])
            log (blink_number)
            delay = 0.7;   # 1.4 sec per blink
            log ("blink number = {0}".format(blink_number))
            log ("delay = {0}".format(delay))
            if blink_number == 0:
                MQTT.publish_event_to_client('s5d9', ledpin + ':1')
                response_txt = "The " + led + " led is turned off."
            else:
                for num in range(1,blink_number+1):
                    log ("number: {0}".format(num))
                    MQTT.publish_event_to_client('s5d9', ledpin + ':0')
                    log("LED turned on")
                    time.sleep(delay)
                    MQTT.publish_event_to_client('s5d9', ledpin + ':1')
                    log("LED turned off")
                    time.sleep(delay)
                response_txt = "The " + led + " l e d blinks " + str(blink_number) + " times."                      
        else:
            if errorflag == False:   
                errorflag == True
                response_txt = "Problem. The intent is unknown."
                log ("Error: Unknown Intent.")
    else:
        errorflag == True
        response_txt = "Problem. The intent is unknown."
        log ("Error: Unknown Intent.")
else:
    errorflag == True
    response_txt = "Problem. The intent is unknown."
    log ("Error: Unknown request type.")
response_json = build_response(request['intent']['name'], response_txt)
log("Error flag = {0}".format(errorflag))
log(response_json)
Alexa.response(uuid_marker, response_json) 
