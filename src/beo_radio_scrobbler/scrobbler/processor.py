from ..parser import parser
from .lastfm import scrobbler_action
from ..config import logger


async def station_logic(station_name: str, live_description: str, timestamp: str) -> None:
    # Implement your station-specific logic here
    
    
    artist, title = parser.parse(station_name, live_description)
    
    if artist and title:
        pass
    elif artist or title:
        logger.error(f"NO RULES FOR: {station_name}: {live_description}")
        return
    else:
        return  # Skipped due to rules
    
    await scrobbler_action(artist.strip(), title.strip(), timestamp)
    
    return
