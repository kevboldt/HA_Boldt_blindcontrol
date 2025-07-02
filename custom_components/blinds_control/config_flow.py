"""Config flow for Blinds Control."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "blinds_control"

class BlindsControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Blinds Control."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Blinds Control",
                data=user_input
            )
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host", default="localhost"): str,
                vol.Required("port", default=80): int,
            })
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BlindsControlOptionsFlow(config_entry)

class BlindsControlOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""
    
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
    
    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("host", default=self.config_entry.data.get("host", "localhost")): str,
                vol.Required("port", default=self.config_entry.data.get("port", 80)): int,
            })
        ) 