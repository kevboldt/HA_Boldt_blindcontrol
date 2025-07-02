"""Cover platform for Blinds Control."""
import logging
import aiohttp
import json
from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    ATTR_POSITION,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, DEFAULT_HOST, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Blinds Control cover platform."""
    config = config_entry.data
    host = config.get("host", DEFAULT_HOST)
    port = config.get("port", DEFAULT_PORT)
    
    # Load blind configurations from your existing API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:{port}/download_config") as response:
                if response.status == 200:
                    blind_configs = await response.json()
                else:
                    _LOGGER.error(f"Failed to load blind configs: {response.status}")
                    return
    except Exception as e:
        _LOGGER.error(f"Error loading blind configurations: {e}")
        return
    
    entities = []
    for blind_num, config_data in blind_configs.items():
        if isinstance(blind_num, str) and blind_num.isdigit():
            blind_num = int(blind_num)
        entities.append(BlindsCover(blind_num, config_data, host, port))
    
    async_add_entities(entities)

class BlindsCover(CoverEntity):
    """Representation of a Blinds Control cover."""
    
    def __init__(self, blind_num, config, host, port):
        """Initialize the cover."""
        self._blind_num = blind_num
        self._config = config
        self._host = host
        self._port = port
        self._gpio = config.get("gpio")
        self._open_pos = config.get("open")
        self._close_pos = config.get("close")
        self._current_position = 0
        self._is_closed = True
        self._available = True
        
        # Blind names mapping
        blind_names = {
            1: "Living Room Left", 2: "Living Room Right", 3: "Dining Room Left",
            4: "Dining Room Right", 5: "Kitchen Window", 6: "Kitchen Door Left",
            7: "Kitchen Door Right", 8: "Master Bedroom Left", 9: "Master Bedroom Right",
            10: "Guest Bedroom Left", 11: "Guest Bedroom Right", 12: "Office Left",
            13: "Office Right", 14: "Kitchen Door"
        }
        self._name = blind_names.get(blind_num, f"Blind {blind_num}")
    
    @property
    def name(self):
        """Return the name of the cover."""
        return self._name
    
    @property
    def unique_id(self):
        """Return the unique ID of the cover."""
        return f"blinds_control_{self._blind_num}"
    
    @property
    def device_class(self):
        """Return the device class."""
        return CoverDeviceClass.BLIND
    
    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self._is_closed
    
    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self._current_position
    
    @property
    def available(self):
        """Return True if entity is available."""
        return self._available
    
    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self._host}:{self._port}/blind/{self._blind_num}/open") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            self._is_closed = False
                            self._current_position = 100
                            self._available = True
                        else:
                            _LOGGER.error(f"Failed to open blind {self._blind_num}: {data.get('error')}")
                    else:
                        _LOGGER.error(f"HTTP error opening blind {self._blind_num}: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error opening blind {self._blind_num}: {e}")
            self._available = False
    
    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self._host}:{self._port}/blind/{self._blind_num}/close") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            self._is_closed = True
                            self._current_position = 0
                            self._available = True
                        else:
                            _LOGGER.error(f"Failed to close blind {self._blind_num}: {data.get('error')}")
                    else:
                        _LOGGER.error(f"HTTP error closing blind {self._blind_num}: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error closing blind {self._blind_num}: {e}")
            self._available = False
    
    async def async_set_cover_position(self, **kwargs):
        """Set the cover position."""
        position = kwargs.get(ATTR_POSITION, 0)
        try:
            # Calculate servo position based on percentage
            if self._open_pos > self._close_pos:
                # Normal case: open > close
                servo_pos = self._close_pos + int((self._open_pos - self._close_pos) * (position / 100))
            else:
                # Reversed case: close > open (like blind 14)
                servo_pos = self._open_pos + int((self._close_pos - self._open_pos) * (position / 100))
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self._host}:{self._port}/blind/{self._blind_num}/temp/{servo_pos}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success") or data.get("actual_position"):
                            self._current_position = position
                            self._is_closed = (position == 0)
                            self._available = True
                        else:
                            _LOGGER.error(f"Failed to set blind {self._blind_num} position: {data.get('error')}")
                    else:
                        _LOGGER.error(f"HTTP error setting blind {self._blind_num} position: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error setting blind {self._blind_num} position: {e}")
            self._available = False
    
    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self._host}:{self._port}/blind/{self._blind_num}/temp/end") as response:
                    if response.status == 200:
                        self._available = True
                    else:
                        _LOGGER.error(f"HTTP error stopping blind {self._blind_num}: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error stopping blind {self._blind_num}: {e}")
            self._available = False
    
    async def async_update(self):
        """Update the cover state."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{self._host}:{self._port}/blind/{self._blind_num}/position") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("current_position") is not None:
                            # Convert servo position to percentage
                            servo_pos = data.get("current_position")
                            if self._open_pos > self._close_pos:
                                # Normal case
                                if servo_pos >= self._open_pos:
                                    self._current_position = 100
                                    self._is_closed = False
                                elif servo_pos <= self._close_pos:
                                    self._current_position = 0
                                    self._is_closed = True
                                else:
                                    # Calculate percentage
                                    range_size = self._open_pos - self._close_pos
                                    position_from_close = servo_pos - self._close_pos
                                    self._current_position = int((position_from_close / range_size) * 100)
                                    self._is_closed = False
                            else:
                                # Reversed case
                                if servo_pos >= self._close_pos:
                                    self._current_position = 0
                                    self._is_closed = True
                                elif servo_pos <= self._open_pos:
                                    self._current_position = 100
                                    self._is_closed = False
                                else:
                                    # Calculate percentage
                                    range_size = self._close_pos - self._open_pos
                                    position_from_open = servo_pos - self._open_pos
                                    self._current_position = int((position_from_open / range_size) * 100)
                                    self._is_closed = False
                            self._available = True
                        else:
                            _LOGGER.warning(f"Could not get position for blind {self._blind_num}: {data.get('error')}")
                    else:
                        _LOGGER.error(f"HTTP error updating blind {self._blind_num}: {response.status}")
        except Exception as e:
            _LOGGER.error(f"Error updating blind {self._blind_num}: {e}")
            self._available = False 