from pathlib import Path
import shutil
from ..config import logger

async def initialize_logging():
    if Path(Path.cwd() / "appdata" / "logs").exists():
        pass
    else:
        Path(Path.cwd() / "appdata" / "logs").mkdir(parents=True, exist_ok=True)
        logger.info("Created logs directory.")

    sample_file = Path(Path.cwd() / "appdata" / "logs" / "sample-log_radio_scrobbler.log")
    if sample_file.exists():
        pass
    else:
        shutil.copy(Path(Path.cwd() / "sample-data" / "sample-log_radio_scrobbler.log"), sample_file)
        logger.info("Created sample log file.")
       

async def initialize_config():
    if Path(Path.cwd() / "appdata" / "config").exists():
        pass
    else:
        Path(Path.cwd() / "appdata" / "config").mkdir(parents=True, exist_ok=True)
        logger.info("Created config directory.")

    sample_file = Path(Path.cwd() / "appdata" / "config" / "sample-station_rules.yaml")
    if sample_file.exists():
        pass
    else:
        shutil.copy(Path(Path.cwd() / "sample-data" / "sample-station_rules.yaml"), sample_file)
        logger.info("Created sample station rules file.")