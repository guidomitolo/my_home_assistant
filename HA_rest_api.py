import requests
import json
import os
from HA_templates import HomeAssistantTemplates, build_payload


URL = "http://homeassistant.local:8123/api/"
TOKEN = os.getenv('TOKEN')

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "content-type": "application/json",
}


def get_ha_data(payload):
    """
    Sends a Jinja template to Home Assistant and returns parsed JSON data.
    """
    try:
        response = requests.post(
            url=URL + "template", 
            headers=HEADERS,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        result_data = response.json()
        
        if isinstance(result_data, str):
            return json.loads(result_data)
        return result_data

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except json.JSONDecodeError:
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")



def get_states(condition):
    if condition:
        payload = build_payload(HomeAssistantTemplates.ENTITIES_BY_STATE, condition)
    else:
        payload = build_payload(HomeAssistantTemplates.ALL_ENTITIES)
    return get_ha_data(payload)

def get_entity_info(entity_id):
    payload = build_payload(HomeAssistantTemplates.SINGLE_ENTITY_INFO, entity_id)
    return get_ha_data(payload)

def get_labels():
    payload = build_payload(HomeAssistantTemplates.LIST_LABELS)
    return get_ha_data(payload)

def get_label_devices(device_id):
    payload = build_payload(HomeAssistantTemplates.LABEL_DEVICES, device_id)
    return get_ha_data(payload)

def get_areas():
    payload = build_payload(HomeAssistantTemplates.LIST_AREAS)
    return get_ha_data(payload)

def get_area_devices(area_name):
    payload = build_payload(HomeAssistantTemplates.AREA_DEVICES, area_name)
    return get_ha_data(payload)

def get_device_entities(device_id):
    payload = build_payload(HomeAssistantTemplates.DEVICE_ENTITIES, device_id)
    return get_ha_data(payload)