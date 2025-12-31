import requests
import json
from ..config import BEO_IP, logger, RUN_MODE
from ..scrobbler.processor import station_logic


async def check_standby() -> bool:
    url = f"http://{BEO_IP}:8080/BeoDevice/powerManagement/standby"
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
    url = f"http://{BEO_IP}:8080/BeoZone/Zone/ActiveSources"
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
    

async def get_stream() -> None:
    
    url = f"http://{BEO_IP}:8080/BeoNotify/Notifications"
    s = requests.Session()

    with s.get(url, headers=None, stream=True) as resp:
        
        for line in resp.iter_lines():
            if line:
                l = json.loads(line.decode('utf-8'))

                if RUN_MODE == 'notify_me':
                    if l['notification']['type'] != 'PROGRESS_INFORMATION':
                        logger.log("NOTIFICATION", l)
                else:
                    if l['notification']['type'] == 'NOW_PLAYING_NET_RADIO':
                        
                        if not RUN_MODE == 'detect_smpl':
                            logger.log("STATION", l)
                        try:
                            logger.log("STATION", f"Detected station: [data][name]: {l['notification']['data']['name']}; [data][liveDescription]: {l['notification']['data']['liveDescription']}")
                        except KeyError:
                            pass
                        
                        if RUN_MODE != 'detect':
                            await station_logic(station_name=l['notification']['data']['name'],
                                        live_description=l['notification']['data']['liveDescription'],
                                        timestamp=l['notification']['timestamp'])
    
    return
