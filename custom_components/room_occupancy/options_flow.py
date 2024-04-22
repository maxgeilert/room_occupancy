from homeassistant import config_entries
from .const import (
    CONF_ACTIVE_STATES,
    CONF_ENTITIES_KEEP,
    CONF_ENTITIES_TOGGLE,
    CONF_TIMEOUT,
    DOMAIN,
)
import voluptuous as vol


class RoomOccupancyBinarySensorOptionsFlow(config_entries.OptionsFlow):
    """Options flow for RoomOccupancyBinarySensor."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                CONF_TIMEOUT,
                default=self.config_entry.options.get(CONF_TIMEOUT),
            ): vol.All(vol.Coerce(int), vol.Range(min=1))
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return await self.async_step_init()
