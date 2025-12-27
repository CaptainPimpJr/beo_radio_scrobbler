import asyncio
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import pylast
from loguru import logger
import arrow
import yaml
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path

#.env file
load_dotenv()

#variables
ip_beo = "192.168.178.94"
local_time = os.getenv("LOCAL_TIMEZONE", default='UTC')  #e.g. "Europe/Berlin"
run_mode = os.getenv("RUN_MODE", default='detect_smpl')  #development or production
station_rules_file = Path(Path.cwd(), 'station_rules.yaml')

# logging
logger.level("SCROBBLE", no=25, color="<yellow>", icon="🎵")
logger.level("STATION", no=26, color="<green>", icon="📻")
logger.level("NOTIFICATION", no=27, color="<blue>", icon="🔔")

logger.add(
    "log_radio_scrobbler.log",
    rotation="00:00",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
if run_mode == 'production':
    logger.add('log_scrobbles.log',
            rotation="w1",
            retention="5 years",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            level="SCROBBLE")
elif run_mode == 'detect':
    logger.add('log_detections.log',
            rotation="00:00",
            retention="1 week",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            level="STATION")
elif run_mode == 'notify_me':
    logger.add('log_notifications.log',
            rotation="00:00",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
            level="NOTIFICATION")
else:
    pass



class StationConfig(BaseModel):
    parser_type: str
    skip_if_contains: List[str]
    delimiter: Optional[str] = None
    artist_first: Optional[bool] = True
    pattern: Optional[str] = None
    field_mapping: Optional[List[str]] = None

class MetadataParser:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        self.stations = {
            name: StationConfig(**cfg) 
            for name, cfg in raw_config['stations'].items()
        }
    
    def parse(self, station_name: str, live_desc: str):
        if station_name not in self.stations:
            return 'Station Rule Not defined', None
        
        config = self.stations[station_name]
        
        # Check skip conditions
        for skip_pattern in config.skip_if_contains:
            if skip_pattern in live_desc:
                return None, None
        
        # Apply parser strategy
        if config.parser_type == "delimiter_split":
            return self._parse_delimiter(live_desc, config)
        elif config.parser_type == "regex_match":
            return self._parse_regex(live_desc, config)
        
        return None, None
    
    def _parse_delimiter(self, live_desc: str, config: StationConfig):
        if config.delimiter not in live_desc:
            return None, None
        
        parts = live_desc.split(config.delimiter, 1)
        if len(parts) != 2:
            return None, None
        
        if config.artist_first:
            return parts[0].strip(), parts[1].strip()
        else:
            return parts[1].strip(), parts[0].strip()
    
    def _parse_regex(self, live_desc: str, config: StationConfig):
        import re
        match = re.match(config.pattern, live_desc)
        if not match:
            return None, None
        
        groups = match.groups()
        # Map to artist, title based on field_mapping
        mapping = {field: groups[i] for i, field in enumerate(config.field_mapping)}
        return mapping.get('artist'), mapping.get('title')


parser = MetadataParser(station_rules_file)

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


async def get_stream() -> None:
    url = f"http://{ip_beo}:8080/BeoNotify/Notifications"
    s = requests.Session()

    with s.get(url, headers=None, stream=True) as resp:
        
        for line in resp.iter_lines():
            if line:
                l = json.loads(line.decode('utf-8'))

                if run_mode == 'notify_me':
                    if l['notification']['type'] != 'PROGRESS_INFORMATION':
                        logger.log("NOTIFICATION", l)
                else:
                    if l['notification']['type'] == 'NOW_PLAYING_NET_RADIO':
                        
                        if not run_mode == 'detect_smpl':
                            logger.log("STATION", l)
                        try:
                            logger.log("STATION", f"Detected station: [data][name]: {l['notification']['data']['name']}; [data][liveDescription]: {l['notification']['data']['liveDescription']}")
                        except KeyError:
                            pass
                        
                        if run_mode != 'detect':
                            await station_logic(station_name=l['notification']['data']['name'],
                                        live_description=l['notification']['data']['liveDescription'],
                                        timestamp=l['notification']['timestamp'])
    
    return

async def sleeping_routine() -> None:
    '''
    Sleeps according to working hours defined in .env file.
    '''
    working_hours_start = arrow.get(os.environ.get("WORKING_HOURS_START", "06:00"), 'HH:mm').format('HH:mm')
    working_hours_end = arrow.get(os.environ.get("WORKING_HOURS_END", "23:00"), 'HH:mm').format('HH:mm')
    now = arrow.now().to(local_time).format('HH:mm')
    
    if working_hours_start < working_hours_end:
        if working_hours_start <= now <= working_hours_end:
            logger.info(f"Within working hours. Sleeping for 1 minutes. {working_hours_end=}, {working_hours_start=}, {now=}")
            await asyncio.sleep(60)
        else:
            for i in range(30):
                if (arrow.now().to(local_time).shift(minutes=+1).format('HH:mm') >= working_hours_start) \
                    and (arrow.now().to(local_time).shift(minutes=+1).format('HH:mm') <= working_hours_end):
                    break
            logger.info(f"Outside working hours. Sleeping for {i+2} minutes.")
            await asyncio.sleep(60*(i+2))
    else:
        if now >= working_hours_start or now <= working_hours_end:
            logger.info(f"Within working hours. Sleeping for 1 minutes. {working_hours_end=}, {working_hours_start=}, {now=}")
            await asyncio.sleep(60)
        else:
            for i in range(30):
                if (arrow.now().to(local_time).shift(minutes=+1).format('HH:mm') <= working_hours_start) \
                    and (arrow.now().to(local_time).shift(minutes=+1).format('HH:mm') >= working_hours_end):
                    break
            logger.info(f"Outside working hours. Sleeping for {i+2} minutes.")
            await asyncio.sleep(60*(i+2))
    return




async def main():
    logger.info(f"Starting Radio Scrobbler...")
    while True:
        if await check_standby():
            try:
                if await check_radio_active():
                    logger.info("Radio is active.")
                    await get_stream()
                    if run_mode in ['detect', 'notify_me']:
                        logger.info("Run mode is 'detect' or 'notify_me'. Exiting after one round of detection.")
                        break
                else:
                    logger.info("Radio is not active. Going to sleep.")
                    
            except KeyError:
                logger.error("KeyError checking radio status. - Should be none-critical")
        else:
            logger.info("Device is in standby mode. Going to sleep")
            
        await sleeping_routine()


if __name__ == "__main__":
    asyncio.run(main())
