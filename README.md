# 🏠 My Home Assistant MCP Server

A **Model Context Protocol (MCP)** server that allows AI models to interact directly with your Home Assistant instance. 

This project features a **bespoke, hand-made Custom Template API** for Home Assistant, specifically optimized to bridge Home Assistant's data structures with LLMs, enabling AI models to query device states, analyze historical data or trends, and execute actions across your smart home.


## 🚀 Key Features

* **Granular Discovery:** Navigate your home via **Areas** and **Labels** to find exactly the device you need.
* **Deep State Insights:** Retrieve full state objects, core states by condition, or specific entity information.
* **Natural Language Search:** Use the `search_entities` tool to find devices based on descriptions, filtered by area or label.
* **Historical Analysis and Trends:** Access state history to track patterns like energy/power consumption, voltage fluctuations 
or security events (i.e. door or window opened).
* **Direct Control:** Trigger services and commands (e.g., Turn On/Off) directly via entity IDs.


---


## 🛠️ Tools Provided

### Discovery & Organization
| Tool | Description |
| :--- | :--- |
| `get_areas()` | Lists all configured Areas in Home Assistant. |
| `get_labels()` | Lists all user-defined Labels. |
| `get_area_devices(area_name)` | Returns all devices located within a specific area. |
| `get_label_devices(label_name)` | Returns all devices associated with a specific label. |
| `get_device_entities(device_id)` | Returns all entities belonging to a specific physical device. |

### State & Information
| Tool | Description |
| :--- | :--- |
| `get_all_entity_states()` | Retrieves the current state of every entity in the system. |
| `get_states_by_condition(condition)` | Filters states based on a specific condition (e.g., "on"). |
| `get_entity_state(entity_id)` | Fetches the current state and attributes for a specific entity. |
| `get_entity_information(entity_id)` | Returns detailed metadata about a specific entity. |

### Analysis
| Tool | Description |
| :--- | :--- |
| `get_entity_state_history(...)` | Retrieves historical state data for time-series analysis. |
| `calculate_electrical_delta(...)` | Get electrical sensors changes to measure consumption increases, fluctuations in tension and load. |
| `analyze_entity_trends(...)` | Analyzes historical patterns and statistical summaries for any Home Assistant entity. |


### Interaction & Search
| Tool | Description |
| :--- | :--- |
| `search_entities(description, area, label)` | Searches for entities using natural language and optional filters. |
| `run_entity_command(entity_id, command)` | Executes a command (like `turn_on` or `toggle`) on a specific entity. |


---


## 📖 Usage Examples

Here is how an AI model leverages the tools to answer user prompts:

### 1. Complex Discovery
**User:** *"What smart devices do I have in the 'Security' category in the Garage?"*
* **AI Action:** Calls `get_label_devices(label_name="Security")`.
* **AI Action:** Filters results or calls `get_area_devices(area_name="Garage")`.
* **Response:** *"In the Garage, your Security devices include the Motion Sensor and the Side Door Lock."*

### 2. Condition-Based Queries
**User:** *"Is there anything currently turned on in the Living Room?"*
* **AI Action:** Calls `search_entities(description="active devices", area="Living Room")`.
* **Alternative:** Calls `get_states_by_condition(condition="on")` and filters by the Living Room area.
* **Response:** *"Yes, the 'Living Lamp' is currently on."*

### 3. Historical Data Analysis
**User:** *"Did the front door open at all last night?"*
* **AI Action:** Calls `get_entity_state_history(entity_id="binary_sensor.front_door", ...)` for the last 12 hours.
* **Response:** *"Yes, the front door was opened twice: once at 8:15 PM and again at 11:30 PM."*

### 4. Executing Actions
**User:** *"I'm leaving now, turn everything off."*
* **AI Action:** Calls `get_states_by_condition(condition="on")`.
* **AI Action:** Iterates through relevant entities and calls `trigger_service(entity_id=..., command="turn_off")`.
* **Response:** *"Done! I've turned off 5 lights and the living room TV."*

### 5. Energy Trends & Analytics 
**User:** *"Compare my power usage from this afternoon to yesterday afternoon."*
* **AI Action:** Calls `calculate_electrical_delta` for two different time windows.
* **AI Logic:** Gets the average power (W) for both periods and compares the percentage difference.
* **Response:** *"This afternoon you averaged 450W, which is 15% lower than yesterday's 530W average."*


---


## ⚙️ Installation & Setup

### 1. Prerequisites
* Python 3.10+
* A running **Home Assistant** instance.
* A Long-Lived Access Token (LLAT) from your Home Assistant profile.

### 2. Configuration
Add this server to your MCP settings file (e.g., `claude_desktop_config.json`):

```json
{
    "mcpServers": {
        "HA_Bot": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/project/folder",
                "run",
                "HA_bot.py"
            ],
            "env": {
                "HA_URL": "[http://homeassistant.local:8123](http://homeassistant.local:8123)",
                "TOKEN": "your_long_lived_access_token_here"
            }
        }
    }
}