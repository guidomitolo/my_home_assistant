import os


# API Configuration
HA_URL = os.getenv('HA_URL', "http://homeassistant.local:8123/api/")
HA_TOKEN =  os.getenv('HA_TOKEN')