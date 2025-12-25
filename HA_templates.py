from string import Template


class HomeAssistantTemplates:
    """
    A collection of Jinja2 templates for Home Assistant, 
    formatted to return clean JSON strings.
    """

    # 1. Global Discovery: Areas
    LIST_AREAS = """{{ areas() | tojson }}"""

    # 2. Global Discovery: Labels
    LIST_LABELS = """{{ labels() | tojson }}"""

    # 3. Filter: Devices by Area
    AREA_DEVICES = Template("""
        {% set ns_devices = namespace(all=[]) %}
        {% for device in area_devices('$target') %}
            {% set ns_entities = namespace(current=[]) %}
            {% for entity in device_entities(device) %}
                {% set ns_entities.current = ns_entities.current + [{
                    'entity_id': entity,
                    'entity_state': states(entity)
                }] %}
            {% endfor %}
            {% set ns_devices.all = ns_devices.all + [{
                'device': device_name(device),
                'device_id': device,
                'area': '$target',
                'entities': ns_entities.current,
                'labels': label_devices(device)
            }] %}
        {% endfor %}
        {{ ns_devices.all | tojson }}
    """)

    # 4. Filter: Devices by Label
    LABEL_DEVICES = Template("""
        {% set ns_devices = namespace(all=[]) %}
        {% for device in label_devices('$target') %}
            {% set ns_entities = namespace(current=[]) %}
            {% for entity in device_entities(device) %}
                {% set ns_entities.current = ns_entities.current + [{
                    'entity_id': entity,
                    'entity_state': states(entity)
                }] %}
            {% endfor %}
            {% set ns_devices.all = ns_devices.all + [{
                'device': device_name(device),
                'device_id': device,
                'label': '$target',
                'entities': ns_entities.current,
                'area': area_name(device)
            }] %}
        {% endfor %}
        {{ ns_devices.all | tojson }}
    """)

    # 5. Filter: Entities by State Condition
    STATES_BY_CONDITION = Template("""
        {% set ns = namespace(on_entities=[]) %}
        {% for state in states %}
            {% if state.state == '$target' %}
                {% set ns.on_entities = ns.on_entities + [{
                    'entity_id': state.entity_id,
                    'name': state.attributes.friendly_name | default(state.entity_id),
                    'area': area_name(state.entity_id) | default('Unassigned'),
                    'last_changed': state.last_changed | string,
                    'state': state.state
                }] %}
            {% endif %}
        {% endfor %}
        {{ ns.on_entities | tojson }}
    """)

    # 6. Detail: Entities by Device ID
    DEVICE_ENTITIES = Template("""
        {% set ns_entities = namespace(all=[]) %}
        {% for entity in device_entities('$target') %}
            {% set ns_entities.all = ns_entities.all + [{
                'entity_id': entity,
                'entity_state': states(entity)
            }] %}
        {% endfor %}
        {{ ns_entities.all | tojson }}
    """)

    # 7. Detail: Comprehensive Single Entity Info
    SINGLE_ENTITY_INFO = Template("""
        {% set ent = '$target' %}
        {% set dev_id = device_id(ent) %}
        {{ {
            'entity_id': ent,
            'state': states(ent),
            'name': state_attr(ent, 'friendly_name') or ent,
            'area_id': area_id(ent),
            'area_name': area_name(ent) or 'Unassigned',
            'labels': label_entities(ent),
            'device_id': dev_id or 'None',
            'device_name': device_name(dev_id) if dev_id else 'None',
            'last_changed': states[ent].last_changed | string if states[ent] else 'unknown',
            'attributes': states[ent].attributes if states[ent] else {}
        } | tojson }}
    """)


def build_payload(template_obj, target_value=None):
    """
    Sends a Jinja template to Home Assistant and returns parsed JSON data.
    """
    rendered_template = template_obj
    if isinstance(template_obj, Template):
        rendered_template = template_obj.safe_substitute(target=target_value)
    return {"template": rendered_template.strip()}