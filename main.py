import asyncio
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import pylast
from loguru import logger
import arrow

#variables
ip_beo = "192.168.178.94"
local_time = os.getenv("LOCAL_TIMEZONE", default='UTC')  #e.g. "Europe/Berlin"


# logging
logger.level("SCROBBLE", no=25, color="<yellow>", icon="🎵")

logger.add(
    "log_radio_scrobbler.log",
    rotation="00:00",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

logger.add('log_scrobbles.log',
           rotation="w1",
           retention="5 years",
           format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
           level="SCROBBLE")



#.env file
load_dotenv()

async def check_standby() -> bool:
    url = f"http://{ip_beo}:8080/BeoDevice/powerManagement/standby"
    payload = ""
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    d = response.json()
    if d['standby']['powerState'] == 'on':
        return True
    else:
        return False
    

async def check_radio_active() -> bool:
    url = f"http://{ip_beo}:8080/BeoZone/Zone/ActiveSources"
    payload={}
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    d = response.json()
    if d['primaryExperience']['source']['friendlyName'] == 'B&O Radio' and d['primaryExperience']['source']['inUse'] == True:
        return True
    else:
        return False
    

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
    logger.debug(f"Scrobbling: {artist} - {title} at {timestamp}")
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
        
        if most_recent_artist == artist and most_recent_title == title:
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

async def station_logic(station_name: str, live_description: str, timestamp: str) -> None:
    # Implement your station-specific logic here
    if station_name == "SWR1 Rheinland-Pfalz":
        if 'SWR' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif ' / ' in live_description:
            title, artist = live_description.split(' / ', 1)
        else:
            logger.debug(f"{station_name}: {live_description}")
            return
    elif station_name == "SWR3":
        if 'SWR' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif ' / ' in live_description:
            title, artist = live_description.split(' / ', 1)
        else:
            logger.debug(f"{station_name}: {live_description}")
            return
    elif station_name == "WDR 4 Ruhrgebiet":
        if 'WDR' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif ' - ' in live_description:
            artist, title = live_description.split(' - ', 1)
        else:
            logger.debug(f"{station_name}: {live_description}")
            return
    elif station_name == "Schwarzwaldradio":
        if 'Schwarzwaldradio' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif ' - ' in live_description:
            artist, title = live_description.split(' - ', 1)
        else:
            logger.debug(f"{station_name}: {live_description}")
            return
    elif station_name == "COSMO":
        if 'COSMO' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif 'WDR' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif ' - ' in live_description:
            artist, title = live_description.split(' - ', 1)
        else:
            logger.debug(f"{station_name}: {live_description}")
            return
    elif station_name == "1LIVE":
        if '1LIVE' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif ' - ' in live_description:
            artist, title = live_description.split(' - ', 1)
        else:
            logger.debug(f"{station_name}: {live_description}")
            return
    elif station_name == "WDR 2 Rheinland":
        if 'WDR' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif ' - ' in live_description:
            artist, title = live_description.split(' - ', 1)
        else:
            logger.debug(f"{station_name}: {live_description}")
            return
    elif station_name == "The Jazz Groove - Mix #1":
        if 'Jazz Groove' in live_description:
            logger.debug(f"{station_name}: {live_description}")
            return
        elif ' - ' in live_description:
            artist, title = live_description.split(' - ', 1)
        else:
            logger.debug(f"{station_name}: {live_description}")
            return
    else:
        logger.error(f"NO RULES FOR: {station_name}: {live_description}")
        return
    
    await scrobbler_action(artist.strip(), title.strip(), timestamp)
    
    return

async def get_stream() -> None:
    url = f"http://{ip_beo}:8080/BeoNotify/Notifications"
    s = requests.Session()

    with s.get(url, headers=None, stream=True) as resp:
        
        for line in resp.iter_lines():
            if line:
                l = json.loads(line.decode('utf-8'))
                if l['notification']['type'] == 'NOW_PLAYING_NET_RADIO':
                    
                    logger.debug(l)
                    
                    await station_logic(station_name=l['notification']['data']['name'],
                                  live_description=l['notification']['data']['liveDescription'],
                                  timestamp=l['notification']['timestamp'])
    
    return

async def main():
    while True:
        if await check_standby():
            try:
                if await check_radio_active():
                    logger.info("Radio is active.")
                    await get_stream()
                else:
                    logger.info("Radio is not active. Going to sleep.")
                    await asyncio.sleep(60)
            except KeyError:
                logger.error("KeyError checking radio status. - Should be none-critical")
        else:
            logger.info("Device is in standby mode. Going to sleep")
            await asyncio.sleep(60)



if __name__ == "__main__":
    asyncio.run(main())
