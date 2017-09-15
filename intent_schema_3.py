{
  "intents": [
    {
      "slots": [
        {
          "name": "Sensor_Selection",
          "type": "Sensor_Options"
        }
      ],
      "intent": "SensorStatusIntent"
    },
    {
      "slots": [
        {
          "name": "led_Selection",
          "type": "led_Options"
        },
        {
          "name": "led_onoff",
          "type": "led_onoff_Options"
        }
      ],
      "intent": "ledControlIntent"
    },
    {
      "slots": [
        {
          "name": "led_Selection",
          "type": "led_Options"
        },
        {
          "name": "blink_num",
          "type": "AMAZON.NUMBER"
        }
      ],
      "intent": "ledBlinkIntent"
    }


  ]
}
