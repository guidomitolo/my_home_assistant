from string import Template


class HomeAssistantTemplates:
    """
    A collection of Jinja2 templates for Home Assistant, 
    formatted to return clean JSON strings.
    """

    # 1. Global Discovery: Areas
    LIST_AREAS = """
        {% set ns_areas = namespace(all=[]) %}
        {% for area in areas() %}
            {% set ns_areas.all = ns_areas.all + [{
                'area_id': area,
                'area_name': area_name(area),
            }] %}
        {% endfor %}
        {{ ns_areas.all | tojson }}
    """

    # 2. Global Discovery: Labels
    LIST_LABELS = """
        {% set ns_labels = namespace(all=[]) %}
        {% for label in labels() %}
            {% set ns_labels.all = ns_labels.all + [{
                'label_id': label,
                'label_name': label_name(label),
                'label_description': label_description(label)
            }] %}
        {% endfor %}
        {{ ns_labels.all | tojson }}
    """

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
                            
            {% set ns_labels = namespace(current=[]) %}
            {% for label in labels(device) %}
                {% set ns_labels.current = ns_labels.current + [{
                    'label_id': label,
                    'label_name': label_name(label),
                    'label_description': label_description(label)
                }] %}
            {% endfor %}

            {% set ns_devices.all = ns_devices.all + [{
                'device_name': device_name(device),
                'device_id': device,
                'area_id': '$target',
                'area_name': area_name('$target'),
                'entities': ns_entities.current,
                'labels': ns_labels.current,
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
                             
            {% set ns_labels = namespace(current=[]) %}
            {% for label in labels(device) %}
                {% set ns_labels.current = ns_labels.current + [{
                    'label_id': label,
                    'label_name': label_name(label),
                    'label_description': label_description(label)
                }] %}
            {% endfor %}
                                                          
            {% set ns_devices.all = ns_devices.all + [{
                'device_name': device_name(device),
                'device_id': device,
                'labels': ns_labels.current,
                'entities': ns_entities.current,
                'area_name': area_name(device),
                'area_id': area_id(device)
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
                    'area_name': area_name(state.entity_id) | default('Unassigned'),
                    'area_id': area_id(state.entity_id) | default('Unassigned'),
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
                'device_id': '$target',
                'device_name': device_name('$target'),
                'entity_id': entity,
                'entity_state': states(entity),
                'area_id': area_id(entity),
                'area_name': area_name(entity)
            }] %}
        {% endfor %}
        {{ ns_entities.all | tojson }}
    """)

    # 7. Detail: Comprehensive Single Entity Info
    SINGLE_ENTITY_INFO = Template("""
        {% set ent = '$target' %}
        {% set dev_id = device_id(ent) %}
                                  
        {% set ns_labels = namespace(current=[]) %}
        {% for label in labels(dev_id) %}
            {% set ns_labels.current = ns_labels.current + [{
                'id': label,
                'name': label_name(label),
                'description': label_description(label)
            }] %}
        {% endfor %}
                                
        {{ {
            'id': ent,
            'name': device_name(ent),
            'state': states(ent),
            'name': state_attr(ent, 'friendly_name') or ent,
            'area_id': area_id(ent),
            'area_name': area_name(ent),
            'labels': ns_labels.current,
            'device_id': dev_id,
            'device_name': device_name(dev_id),
            'last_changed': states[ent].last_changed | string if states[ent] else 'unknown',
            'attributes': states[ent].attributes if states[ent] else {}
        } | tojson }}
    """)

    ALL_ENTITITES = Template("""
        {% set ns = namespace(on_entities=[]) %}
        {% for state in states %}

            {% set device_id = device_id(state.entity_id) %}

            {% set ns_labels = namespace(current=[]) %}
            {% for label in labels(device_id) %}
                {% set ns_labels.current = ns_labels.current + [{
                    'label_id': label,
                    'label_name': label_name(label),
                    'label_description': label_description(label)
                }] %}
            {% endfor %}

            {% set ns.on_entities = ns.on_entities + [{
                'entity_id': state.entity_id,
                'name': state.attributes.friendly_name,
                'area_name': area_name(state.entity_id),
                'area_id': area_id(state.entity_id),
                'labels': ns_labels.current
            }] %}

        {% endfor %}
        {{ ns.on_entities | tojson }}
    """)

    AREA_ENTITIES = Template("""
        {% set ns_entities = namespace(current=[]) %}
        {% for device in area_devices('$target') %}
            {% for entity in device_entities(device) %}

                {% set ns_labels = namespace(current=[]) %}
                {% for label in labels(entity) %}
                    {% set ns_labels.current = ns_labels.current + [{
                        'label_id': label,
                        'label_name': label_name(label),
                        'label_description': label_description(label)
                    }] %}
                {% endfor %}
              
                {% set ns_entities.current = ns_entities.current + [{
                    'device_id': device,
                    'device_name': device_name(device),
                    'entity_id': entity,
                    'entity_state': states(entity),
                    'area_id': area_id(entity),
                    'area_name': area_name(entity),
                    'labels': ns_labels.current,
                    'name': state_attr(entity, 'friendly_name'),
                    'area_name': area_name(entity),
                    'area_id': area_id(entity),
                    'labels': ns_labels.current
                }] %}
                             
            {% endfor %}
        {% endfor %}
        {{ ns_entities.current | tojson }}
    """)

    LABEL_ENTITIES = Template("""
        {% set ns_entities = namespace(all=[]) %}
        {% for device in label_devices('$target') %}
            {% for entity in device_entities(device) %}

              {% set ns_labels = namespace(current=[]) %}
              {% for label in labels(entity) %}
                  {% set ns_labels.current = ns_labels.current + [{
                      'label_id': label,
                      'label_name': label_name(label),
                      'label_description': label_description(label)
                  }] %}
              {% endfor %}
            
                {% set ns_entities.all = ns_entities.all + [{
                    'device_id': device,
                    'device_name': device_name(device),
                    'entity_id': entity,
                    'entity_state': states(entity),
                    'area_id': area_id(entity),
                    'area_name': area_name(entity),
                    'labels': ns_labels.current,
                    'name': state_attr(entity, 'friendly_name'),
                    'area_name': area_name(entity),
                    'area_id': area_id(entity),
                    'labels': ns_labels.current
                }] %}
                              
            {% endfor %}
        {% endfor %}
        {{ ns_entities.all | tojson }}
    """)


def build_payload(template_obj, target_value=None):
    """
    Sends a Jinja template to Home Assistant and returns parsed JSON data.
    """
    rendered_template = template_obj
    if isinstance(template_obj, Template):
        rendered_template = template_obj.safe_substitute(target=target_value)
    return {"template": rendered_template.strip()}