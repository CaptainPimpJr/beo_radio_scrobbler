### 2026-01-16
Added feature to love tracks on last.fm by turning volume up and down again within a short timeframe. Currently for testing each step can take one second. 

### 2026-01-20
Somehow uploaded scrobbles had casefold() (sort of lower()) attached to the string. Which leads to stupid looking tracks if you are very unique with your scrobble and nothing else is found. 
In addition, std out informed about debug all the time - and now it reflects the LOGLEVEL environment variable. 
Added WORKINGHOURS(_START & _END) environment variable. Inside workinghours, BeoRadioScrobbler checks every minute if radio is running. Outside workinghours window is extended to 30 min. I really do not know if this has any impact on energy saving or whatsoever, it might be obsolete and waste of code. But here we are.  Maybe one can make use of it...
If the format is not in HH:MM starting time is set to '06:00' and end of schedule is set to '23:00'.