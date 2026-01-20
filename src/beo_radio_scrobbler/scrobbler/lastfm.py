import pylast
import arrow
import asyncio
import os
from ..config import logger, LOCAL_TIMEZONE, LASTFM_USERNAME, LASTFM_PASSWORD, LASTFM_API_KEY, LASTFM_API_SECRET


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
        most_recent_artist = network.get_user(LASTFM_USERNAME).get_recent_tracks(limit=1)[0].track.artist.name
        most_recent_title = network.get_user(LASTFM_USERNAME).get_recent_tracks(limit=1)[0].track.title
    except IndexError:
        logger.info("No existing scrobble found.")
        return "-", "-"
    except Exception as e:
        logger.error(f"Error fetching most recent scrobble: {e}")
        return None, None
    return most_recent_artist.strip(), most_recent_title.strip()

async def double_scrobble_check(artist: str, title: str, network: pylast.LastFMNetwork) -> bool:
    '''
    Checks if the given artist and title match the most recent scrobble.
    Returns True:
        if the most recent scrobble equals the given artist and title.
        
    Returns False: 
        if the most recent scrobble does not match the given artist and title.
    
    Raises Exception:
        if there was an error fetching the most recent scrobble.
    '''
    most_recent_artist, most_recent_title = await most_recent_scrobble(network)
    if most_recent_artist and most_recent_title:
        if most_recent_artist.casefold() == artist.casefold() and most_recent_title.casefold() == title.casefold():
            return True
        else:
            logger.debug(f"Most recent scrobble: {most_recent_artist} - {most_recent_title}; Current track: {artist} - {title}")
            return False
    else:
        raise Exception("Error fetching recent scrobble")


async def scrobbler_action(artist: str, title: str, timestamp: str) -> None:
    try:
        network = pylast.LastFMNetwork(
            api_key=LASTFM_API_KEY,
            api_secret=LASTFM_API_SECRET,
            username=LASTFM_USERNAME,
            password_hash=pylast.md5(LASTFM_PASSWORD),
        )
    except Exception as e:
        logger.error(f"Error connecting to Last.fm: {e}")
        logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")
        return
    
    # check for double scrobble
    try:
        if await double_scrobble_check(artist, title, network):
            # either duplicate or error
            logger.info(f"Track already scrobbled: {artist} - {title}")
            return
    except Exception as e:
        logger.error(f"Error during double scrobble check: {e}")
        logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")
        return

    timestamp = arrow.get(
                timestamp, 
                'YYYY-MM-DDTHH:mm:ss.SSSSSS'
            ).to(LOCAL_TIMEZONE).timestamp()

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
    try:
        if await double_scrobble_check(artist, title, network):
            # either duplicate or error
            logger.log("SCROBBLE", f"Successfully scrobbled: {artist} - {title}")
        else:
            logger.error(f"Scrobble verification failed for:")
            logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")
    except Exception as e:
        logger.error(f"Error during scrobble verification: {e}")
        logger.log("SCROBBLE", f"Scrobble not confirmed: {artist} - {title}")


    return


async def love_track():
    logger.debug("Loving track...")
    try:
        network = pylast.LastFMNetwork(
            api_key=LASTFM_API_KEY,
            api_secret=LASTFM_API_SECRET,
            username=LASTFM_USERNAME,
            password_hash=pylast.md5(LASTFM_PASSWORD),
        )
    except Exception as e:
        logger.error(f"Error connecting to Last.fm: {e}")
        return
    
    most_recent_artist, most_recent_title = await most_recent_scrobble(network)
    try:
        network.get_track(most_recent_artist, most_recent_title).love()
        logger.info(f"Loved track: {most_recent_artist} - {most_recent_title}")
    except Exception as e:
        logger.error(f"Error loving track: {e}")
        
    return