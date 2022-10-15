"""Support for Zeptrion  Blinds."""

from __future__ import annotations

import logging
from typing import Any

from pyzeptrion.blind import ZeptrionBlind
from pyzeptrion.exceptions import ZeptrionConnectionError
from pyzeptrion.const import ON_STATE, OFF_STATE
import voluptuous as vol

from homeassistant.components.switch import (
    DOMAIN,
    PLATFORM_SCHEMA,
    SwitchEntity,
)

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Zeptrion Blind"
CONF_CHN = "chn"
DOMAIN = "zeptrion"
#_LOGGER.warning("In setup: %s", chn)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_CHN, default=1): cv.positive_int,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Zeptrion blind integration."""
    host = config.get(CONF_HOST)
    chn = config.get(CONF_CHN)

    blind = await ZeptrionBlind.create(ZeptrionBlind,host, chn)
    async_add_entities([ZeptrionSwitch(blind)], True)

class ZeptrionSwitch(SwitchEntity):
    """Representation of the Zeptrion blind."""

    def __init__(self, blind):
        """Initialize the light."""
        self._blind = blind
        self._host = blind.host
        self._chn = blind.chn
        self._state = None
        self._name = blind.name
        self._attr_unique_id  = blind.dev_id
        self._available = False

    @property
    def is_on(self):
        return self._state
    
    
    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._attr_unique_id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available


    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        try:
           
            #self._attr_is_closed = await self._blind.get_state()
            self._available = True
        except ZeptrionConnectionError:
            _LOGGER.warning("Update: the Zeptrion blind is not online")
            self._available = False

    async def async_turn_off(self):
        """Close the cover."""
        _LOGGER.warning("Close Cover: %s", self._state)
        await self._blind.move_close()
        self._state = False
        

    async def async_turn_on(self):
        """Open the cover."""
        await self._blind.move_open()
        self._state = True

    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        try:
            self._state = await self._blind.get_state()
            self._available = True
        except ZeptrionConnectionError:
            _LOGGER.warning("Turn ON: he Zeptrion bulb is not online")
            self._available = False