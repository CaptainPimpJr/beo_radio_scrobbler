import asyncio
import arrow
from ..config import logger, LOCAL_TIMEZONE, WORKINGHOURS_START, WORKINGHOURS_END


async def sleeping_routine() -> None:
    '''
    Sleeps according to working hours defined in .env file.
    '''
    working_hours_start = arrow.get(WORKINGHOURS_START, 'HH:mm').format('HH:mm')
    working_hours_end = arrow.get(WORKINGHOURS_END, 'HH:mm').format('HH:mm')
    now = arrow.now().to(LOCAL_TIMEZONE).format('HH:mm')
    
    if working_hours_start < working_hours_end:
        if working_hours_start <= now <= working_hours_end:
            logger.debug(f"Within working hours. Sleeping for 1 minutes. {working_hours_end=}, {working_hours_start=}, {now=}")
            await asyncio.sleep(60)
        else:
            for i in range(30):
                if (arrow.now().to(LOCAL_TIMEZONE).shift(minutes=+1).format('HH:mm') >= working_hours_start) \
                    and (arrow.now().to(LOCAL_TIMEZONE).shift(minutes=+1).format('HH:mm') <= working_hours_end):
                    break
            logger.debug(f"Outside working hours. Sleeping for {i+2} minutes.")
            await asyncio.sleep(60*(i+2))
    else:
        if now >= working_hours_start or now <= working_hours_end:
            logger.debug(f"Within working hours. Sleeping for 1 minutes. {working_hours_end=}, {working_hours_start=}, {now=}")
            await asyncio.sleep(60)
        else:
            for i in range(30):
                if (arrow.now().to(LOCAL_TIMEZONE).shift(minutes=+1).format('HH:mm') <= working_hours_start) \
                    and (arrow.now().to(LOCAL_TIMEZONE).shift(minutes=+1).format('HH:mm') >= working_hours_end):
                    break
            logger.debug(f"Outside working hours. Sleeping for {i+2} minutes.")
            await asyncio.sleep(60*(i+2))
    return
