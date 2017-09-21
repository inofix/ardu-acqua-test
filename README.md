# ardu-acqua-test

Proof of concept for water quality measurements at the flussbad-berlin project.

## Basic Idea

For now we have one arduino reporting sensor values back over the serial line.
At the other end sits a raspberry pi, collecting the data. The data is then processed and either just printed to the console or a file, or sent over mobile or wired/wireless network to a webserver..

## Outlook

More than one arduino connect to the, e.g., raspberry pi. For each one of them the data processing can be configured individually.

## Example Data for Python Processing

### INPUT: JSON from the arduino over the serial line

  [
    {"name":"light_value","value":"777"},
    {"name":"box_temperature","unit":"°C","value":"22.19"},
    {"name":"env_temperature","unit":"°C","value":"20.00"},
    {"name":"env_humidity","unit":"%","value":"71.00"},
    {"name":"env_heat_index","value":"19.91"},
    {"name":"water_level","threshold":"600","value":"0"},
    {"name":"water_distance","unit":"m","value":"0.92"}
  ]

### OUTPUT: Target JSON from the raspberry pi for the use in web app

  [
    {"name":"light_value","value":"777", "time"="2017-09-20T21:29:42"},
    {"name":"light_value","value":"777", "time"="2017-09-20T21:39:51"},
    {"name":"light_value","value":"777", "time"="2017-09-20T21:49:49"},
    {"name":"box_temperature","unit":"°C","value":"22.19", "time"="2017-09-20T21:49:49"},
    {"name":"env_temperature","unit":"°C","value":"20.00", "time"="2017-09-20T21:49:49"},
    {"name":"env_humidity","unit":"%","value":"71.00", "time"="2017-09-20T21:49:49"},
    {"name":"env_heat_index","value":"19.91", "time"="2017-09-20T21:49:49"},
    {"name":"water_level","threshold":"600","value":"0", "time"="2017-09-20T21:49:49"},
    {"name":"water_distance","unit":"m","value":"0.92", "time"="2017-09-20T21:49:49"}
  ]


