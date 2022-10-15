"""Support for Zeptrion  Blinds."""

from __future__ import annotations

import logging
from typing import Any

from pyzeptrion.blind import ZeptrionBlind
from pyzeptrion.exceptions import ZeptrionConnectionError
from pyzeptrion.const import ON_STATE, OFF_STATE
import voluptuous as vol

from homeassistant.components.cover import (
    DOMAIN,
    PLATFORM_SCHEMA,
    ATTR_POSITION,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_STOP,
    SUPPORT_SET_POSITION,
    DEVICE_CLASS_SHADE,
    CoverEntity,
    CoverEntityFeature,
    CoverDeviceClass,
)

from homeassistant.const import CONF_HOST, STATE_CLOSED, STATE_OPEN
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
    async_add_entities([ZeptrionCover(blind)], True)

class ZeptrionCover(CoverEntity):
    """Representation of the Zeptrion blind."""

    def __init__(self, blind):
        """Initialize the light."""
        self._blind = blind
        self._position = 50
        self._state = None
        self._host = blind.host
        self._chn = blind.chn
        self._name = blind.name
        self._attr_unique_id  = blind.dev_id
        self._attr_device_class = CoverDeviceClass.SHADE
        self._attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP | CoverEntityFeature.SET_POSITION
        #self._state = blind.state
        self._available = False
        self._attr_is_closed = None
        self._attr_position = 50
   

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
            await self._blind.get_state()
            self._available = True
        except ZeptrionConnectionError:
            _LOGGER.warning("Update: the Zeptrion blind is not online")
            self._available = False

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self._blind.move_close()
        #self._attr_is_closed = False
        self._state = STATE_CLOSED
        self._position = 50
        

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self._blind.move_open()
        #self._attr_is_closed = False
        self._state = STATE_OPEN
        self._position = 50

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        await self._blind.stop()
        #self._attr_is_closed = False
        self._position = 50

    @property
    def current_cover_position(self) -> int | None:
        """Return the current position of the cover."""
        return 50