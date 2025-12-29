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
beo_ip = os.getenv("BEO_IP", default='')
local_time = os.getenv("LOCAL_TIMEZONE", default='UTC')  #e.g. "Europe/Berlin"
run_mode = os.getenv("RUN_MODE", default='detect_smpl')  #development or production
station_rules_file = Path(Path.cwd() / "data" / "config" / "station_rules.yaml")

# logging
logger.level("SCROBBLE", no=25, color="<yellow>", icon="🎵")
logger.level("STATION", no=26, color="<green>", icon="📻")
logger.level("NOTIFICATION", no=27, color="<blue>", icon="🔔")

logger.add(
    Path(Path.cwd() / "data" / "logs" / "log_radio_scrobbler.log"),
    rotation="00:00",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
if run_mode == 'production':
    logger.add(
        Path(Path.cwd() / "data" / "logs" / "log_scrobbles.log"),
        rotation="w1",
        retention="5 years",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        filter=lambda record: record["level"].no == 25)
elif run_mode in ['detect', 'detect_smpl']:
    logger.add(
        Path(Path.cwd() / "data" / "logs" / "log_detections.log"),
        rotation="00:00",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        filter=lambda record: record["level"].no == 26)
elif run_mode == 'notify_me':
    logger.add(
        Path(Path.cwd() / "data" / "logs" / "log_notifications.log"),
        rotation="00:00",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        level="NOTIFICATION")
else:
    pass
