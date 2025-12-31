import os
from dotenv import load_dotenv
from loguru import logger
from pathlib import Path

#.env file
if os.getenv("IN_PROD") == "1":
    pass  # In production, assume environment variables are set externally
else:
    load_dotenv()

#variables
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY", default='abcd1234')
LASTFM_API_SECRET=os.getenv("LASTFM_API_SECRET", default='1234abcd')
LASTFM_USERNAME=os.getenv("LASTFM_USERNAME", default='your_username')
LASTFM_PASSWORD=os.getenv("LASTFM_PASSWORD", default='your_password')
LOCAL_TIMEZONE=os.getenv("LOCAL_TIMEZONE", default='UTC')
RUN_MODE=os.getenv("RUN_MODE", default='detect')
BEO_IP=os.getenv("BEO_IP", default='192.168.1.100')
LOGLEVEL=os.getenv("LOGLEVEL", default='INFO').upper()

# logging
logger.level("SCROBBLE", no=25, color="<yellow>", icon="🎵")
logger.level("STATION", no=26, color="<green>", icon="📻")
logger.level("NOTIFICATION", no=27, color="<blue>", icon="🔔")

logger.add(
    Path(Path.cwd() / "appdata" / "logs" / "log_radio_scrobbler.log"),
    rotation="00:00",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
if RUN_MODE == 'production':
    logger.add(
        Path(Path.cwd() / "appdata" / "logs" / "log_scrobbles.log"),
        rotation="w1",
        retention="5 years",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        filter=lambda record: record["level"].no == 25)
elif RUN_MODE in ['detect', 'detect_smpl']:
    logger.add(
        Path(Path.cwd() / "appdata" / "logs" / "log_detections.log"),
        rotation="00:00",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        filter=lambda record: record["level"].no == 26)
elif RUN_MODE == 'notify_me':
    logger.add(
        Path(Path.cwd() / "appdata" / "logs" / "log_notifications.log"),
        rotation="00:00",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        level="NOTIFICATION")
else:
    pass
