"""Config flow for Boldt Blinds."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "boldt_blinds"

class BoldtBlindsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Boldt Blinds."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Boldt Blinds",
                data=user_input
            )
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="localhost"): str,
            })
        ) 