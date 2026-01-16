import asyncio

from ..parser import parser
from .lastfm import scrobbler_action, love_track
from ..config import logger
from ..state import love_state

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

async def love_detection() -> None:

    try:
        await asyncio.sleep(1) # wait to see if more data comes in

        # Analyze the deque for love detection logic:
        if len(love_state._love_detection_deque) < 2:
            # since we have waited for 1 second, deque will be cleared and base volume set again.
            love_state._base_volume = love_state._love_detection_deque.pop()
            love_state._love_detection_deque.clear()
            return
        elif len(love_state._love_detection_deque) == 2:
            # Its a match: Vol up, then down.
            if love_state._base_volume < love_state._love_detection_deque[0] > love_state._love_detection_deque[1] and \
                (-2 <= (love_state._base_volume - love_state._love_detection_deque[1]) <= 2):
                await love_track()

            love_state._base_volume = love_state._love_detection_deque.pop()
            love_state._love_detection_deque.clear()
            return
            
        elif len(love_state._love_detection_deque) == 3:
            # Its a match: Vol up, up, down.
            # Or:          Vol up, down, down.
            # And:  the last vol is close to base vol.
            if (love_state._base_volume < love_state._love_detection_deque[0] < love_state._love_detection_deque[1] > love_state._love_detection_deque[2] or \
                love_state._base_volume < love_state._love_detection_deque[0] > love_state._love_detection_deque[1] > love_state._love_detection_deque[2]) and \
                (-2 <= (love_state._base_volume - love_state._love_detection_deque[2]) <= 2):
                await love_track()

            love_state._base_volume = love_state._love_detection_deque.pop()
            love_state._love_detection_deque.clear()
            return
            
        elif len(love_state._love_detection_deque) == 4:
            # Its a match: Vol up, up, up, down.
            # Or:          Vol up, up, down, down.
            # Or:          Vol up, down, down, down.
            # And:  the last vol is close to base vol.
            if (love_state._base_volume < love_state._love_detection_deque[0] < love_state._love_detection_deque[1] < love_state._love_detection_deque[2] > love_state._love_detection_deque[3] or \
                love_state._base_volume < love_state._love_detection_deque[0] < love_state._love_detection_deque[1] > love_state._love_detection_deque[2] > love_state._love_detection_deque[3] or \
                love_state._base_volume < love_state._love_detection_deque[0] > love_state._love_detection_deque[1] > love_state._love_detection_deque[2] > love_state._love_detection_deque[3]) and \
                (-2 <= (love_state._base_volume - love_state._love_detection_deque[3]) <= 2):
                await love_track()

            love_state._base_volume = love_state._love_detection_deque.pop()
            love_state._love_detection_deque.clear()
            return
        
        elif len(love_state._love_detection_deque) == 5:
            # Its a match: Vol up, up, up, up, down.
            # Or:          Vol up, up, up, down, down.
            # Or:          Vol up, up, down, down, down.
            # Or:          Vol up, down, down, down, down.
            # And:  the last vol is close to base vol.
            if (love_state._base_volume < love_state._love_detection_deque[0] < love_state._love_detection_deque[1] < love_state._love_detection_deque[2] < love_state._love_detection_deque[3] > love_state._love_detection_deque[4] or \
                love_state._base_volume < love_state._love_detection_deque[0] < love_state._love_detection_deque[1] < love_state._love_detection_deque[2] > love_state._love_detection_deque[3] > love_state._love_detection_deque[4] or \
                love_state._base_volume < love_state._love_detection_deque[0] < love_state._love_detection_deque[1] > love_state._love_detection_deque[2] > love_state._love_detection_deque[3] > love_state._love_detection_deque[4] or \
                love_state._base_volume < love_state._love_detection_deque[0] > love_state._love_detection_deque[1] > love_state._love_detection_deque[2] > love_state._love_detection_deque[3] > love_state._love_detection_deque[4]) and \
                (-2 <= (love_state._base_volume - love_state._love_detection_deque[4]) <= 2):
                await love_track()

            love_state._base_volume = love_state._love_detection_deque.pop()
            love_state._love_detection_deque.clear()
            return
        
        else:
            # Too much data, reset.
            love_state._base_volume = love_state._love_detection_deque.pop()
            love_state._love_detection_deque.clear()
            return

    except asyncio.CancelledError:
        # This happens when the task is cancelled
        print("Wait was interrupted!")
        raise  # Re-raise to properly clean up


async def _save_volume(vol: int) -> None:

    if love_state._base_volume is None:
        love_state._base_volume = vol
        print(f'Setting base volume to {love_state._base_volume}')
        return
    
    love_state._love_detection_deque.append(vol)    
    print(f'Appended volume: {vol}, deque: {love_state._love_detection_deque}')
    if love_state._love_detection_task and not love_state._love_detection_task.done():
        print('Cancelling existing love detection task...')
        love_state._love_detection_task.cancel()
        try:
            await love_state._love_detection_task  # Wait for cancellation to complete
        except asyncio.CancelledError:
            pass
    
    love_state._love_detection_task = asyncio.create_task(love_detection())