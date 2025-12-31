import asyncio
from .config import logger, RUN_MODE
from .api.beo_client import check_standby, check_radio_active, get_stream
from .utils.scheduling import sleeping_routine
from .utils.initialization import initialize_logging, initialize_config


async def main():

    await initialize_logging()
    await initialize_config()

    logger.info(f"Starting Radio Scrobbler...")
    while True:
        if await check_standby():
            try:
                if await check_radio_active():
                    logger.info("Radio is active.")
                    await get_stream()
                    if RUN_MODE in ['detect', 'detect_smpl', 'notify_me']:
                        logger.info("Run mode is 'detect' or 'notify_me'. Exiting after one round of detection.")
                        break
                else:
                    logger.info("Radio is not active. Going to sleep.")
                    await sleeping_routine()
                    
            except KeyError:
                logger.error("KeyError checking radio status. - Should be none-critical")
        else:
            logger.info("Device is in standby mode. Going to sleep")
            await sleeping_routine()
    
    quit()


def cli():
    """Entry point for the command-line interface."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Radio Scrobbler stopped by user.")


if __name__ == "__main__":
    cli()
