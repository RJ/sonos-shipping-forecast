# Sonos Shipping Forecast

Automatically hijack your Sonos system to play the Shipping Forecast
from BBC Radio 4, then restores Sonos to previous state.

## Instructions

* <code>pip install soco</code>
* Add BBC Radio 4 to your sonos favourite stations
* Edit the script to set the zone names and volumes
* Cron the script to run at 0048 every night, it defaults to 12 minutes
  duration
* Enjoy!

## Crontab Entry

Edit your crontab with <code>crontab -e</code> and add this line:

    48 0 * * *   /path/to/sonos-shipping-forecast/sonosforecast.py

## Depends

Uses the SoCo controller library: https://github.com/SoCo/SoCo
