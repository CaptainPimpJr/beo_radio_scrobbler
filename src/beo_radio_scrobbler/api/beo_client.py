import json
import httpx

from ..config import BEO_IP, logger, RUN_MODE
from ..scrobbler.processor import station_logic, _save_volume


async def check_standby() -> bool:
    url = f"http://{BEO_IP}:8080/BeoDevice/powerManagement/standby"
    headers = {
    'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        resp = await client.request('GET', url, headers=headers)
            
    d = resp.json()
        
    return d['standby']['powerState'] == 'on'
        

async def check_radio_active() -> bool:
    url = f"http://{BEO_IP}:8080/BeoZone/Zone/ActiveSources"
    headers = {
      'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        resp = await client.request('GET', url, headers=headers)

    d = resp.json()
    return d['primaryExperience']['source']['friendlyName'] == 'B&O Radio' and d['primaryExperience']['source']['inUse'] == True

async def get_stream() -> None:

    url = f"http://{BEO_IP}:8080/BeoNotify/Notifications"

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', url, headers=None) as resp:
                async for line in resp.aiter_lines():
                    if line:
                        l = json.loads(line)

                        if RUN_MODE == 'notify_me':
                            if l['notification']['type'] != 'PROGRESS_INFORMATION':
                                logger.log("NOTIFICATION", l)
                        else:
                            if l['notification']['type'] == 'NOW_PLAYING_NET_RADIO':
                                
                            
                                logger.log("STATION", l)
                                try:
                                    logger.log("STATION", f"Detected station: [data][name]: {l['notification']['data']['name']}; [data][liveDescription]: {l['notification']['data']['liveDescription']}")
                                except KeyError:
                                    pass
                                
                                if RUN_MODE in ['detect',]:
                                    pass
                                else:
                                    await station_logic(station_name=l['notification']['data']['name'],
                                                live_description=l['notification']['data']['liveDescription'],
                                                timestamp=l['notification']['timestamp'])
                                    
                            elif l['notification']['type'] == 'VOLUME':
                                if RUN_MODE in ['detect',]:
                                    pass
                                else:
                                    await _save_volume(l['notification']['data']['speaker']['level'])
    except httpx.ReadTimeout:
        return
    except Exception as e:
        logger.error(f"Error in get_stream: {e}")
        return
    
                   
