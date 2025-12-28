# production
Reads the notification stream of BeoNetClient API indefinitely. The type of the stream needs to be 'NOW_PLAYING_NET_RADIO'.  
Parses artist and title information based on pre-defined rules (use RUN_MODE 'detect' or 'detect_smpl' to identify those rules first)  
and scrobbles the data to Last.fm.  

# detect
Writes the current value of the notification stream with type 'NOW_PLAYING_NET_RADIO' of BeoNetClient API to the detections log. 
And in addition the simplified form which contains just the station name and live description to the stations log.
Which is currently to be thought enough to determine station name, artist and title information.

# detect_smpl
Just like 'detect' but only writes the simplified form to the stations log. Not every information of the notification stream.

# notify_me
Logs all notifications except 'PROGRESS_INFORMATION' to a separate log file. Useful to get a wider picture of the changes on the BeoSound Radio.  
But...I don't know yet what for. :)