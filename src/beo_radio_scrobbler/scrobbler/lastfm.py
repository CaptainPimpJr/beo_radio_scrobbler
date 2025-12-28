import pylast
import arrow
import asyncio
import os
from ..config import logger, local_time


async def most_recent_scrobble(network: pylast.LastFMNetwork) -> tuple:
    '''
    Fetches the most recent scrobble from Last.fm for the configured user.
    Returns None, None if there was an error.
    Returns "-", "-" if no scrobbles exist. 
    At least that is the plan. I checked for a far distant past where no scrobbles existed and it returned an empty list.
    Now: IndexError -> "-", "-"
    Different Error -> None, None
    '''
    try:
        most_recent_artist = network.get_user(os.environ['USERNAME']).get_recent_tracks(limit=1)[0].track.artist.name
        most_recent_title = network.get_user(os.environ['USERNAME']).get_recent_tracks(limit=1)[0].track.title
    except IndexError:
        logger.info("No existing scrobble found.")
        return "-", "-"
    except Exception as e:
        logger.error(f"Error fetching most recent scrobble: {e}")
        return None, None
    return most_recent_artist.strip(), most_recent_title.strip()

async def scrobbler_action(artist: str, title: str, timestamp: str) -> None:
    try:
        network = pylast.LastFMNetwork(
            api_key=os.environ['API_KEY'],
            api_secret=os.environ['API_SECRET'],
            username=os.environ['USERNAME'],
            password_hash=pylast.md5(os.environ['PASSWORD']),
        )
    except Exception as e:
        logger.error(f"Error connecting to Last.fm: {e}")
        logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")
        return
    
    # check for double scrobble
    most_recent_artist, most_recent_title = await most_recent_scrobble(network)
    if most_recent_artist and most_recent_title:
        if most_recent_artist == artist and most_recent_title == title:
            logger.info(f"Duplicate scrobble detected for: {artist} - {title}. Skipping scrobble.")
            return
    else:
        logger.error("Could not verify recent scrobble due to error fetching recent scrobbles.")
        logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")
        return

    timestamp = arrow.get(
                timestamp, 
                'YYYY-MM-DDTHH:mm:ss.SSSSSS'
            ).to(local_time).timestamp()

    # start scrobbling
    logger.debug(f"Scrobbling: {artist} - {title} at {arrow.get(timestamp).format('YYYY-MM-DD HH:mm:ss')}")
    try:
        network.scrobble(
            artist,
            title, 
            timestamp
        )
    except Exception as e:
        logger.error(f"Error scrobbling track: {e}")
        logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")
        return

    # wait a moment to allow Last.fm to process the scrobble
    await asyncio.sleep(2)
    
    # check if scrobble was successful
    most_recent_artist, most_recent_title = await most_recent_scrobble(network)

    if most_recent_artist and most_recent_title:
        
        if most_recent_artist.casefold() == artist.casefold() and most_recent_title.casefold() == title.casefold():
            logger.log("SCROBBLE", f"Successfully scrobbled: {artist} - {title}")
        else:
            logger.error(f"Scrobble verification failed for:")
            logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")
            logger.error(f"Expected: {artist} - {title}, Got: {most_recent_artist} - {most_recent_title}")
    else:
        logger.error("Could not verify scrobble due to error fetching recent scrobbles.")
        logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")
        return

    return
