# How-To Guides 📖

This document provides step-by-step guides for common tasks and workflows with the BeoRadio Scrobbler.

---

## From Notification Stream to Station Filter

This guide walks you through the process of setting up station-specific filters to parse artist and title information from the BeoNetRemote API notification stream.

### Overview

The BeoSound Radio sends notifications through its API containing metadata about currently playing tracks. However, different radio stations format this metadata differently. This guide shows you how to identify these patterns and create custom parsing rules.

### Step 1: Capture Raw Notification Data

First, you need to see what data your radio station is sending.

1. **Set run mode to `detect`:**
   Set the environment variable `RUN_MODE` to `detect`

2. **Play your radio station** on the BeoSound Radio
   Change stations, wait a bit, and move on to the next station.  
   Some messages appear only when news are broadcasted.  
   The B&O App shows what is sent via notifications stream.  
   The stream stops after 5 min. 

3. **Check the log file** at `appdata/logs/log_detections.log`
   - You'll see the complete notification stream data
   - Look for the `NOW_PLAYING_NET_RADIO` notification type

### Step 2: Identify the Metadata Pattern

Examine the log entries to understand how your station formats the metadata:



**Example notification structure:**
2026-01-01 13:31:46 | {'notification': {'timestamp': '2026-01-01T12:31:46.280063', 'type': 'NOW_PLAYING_NET_RADIO', 'kind': 'playing', 'data': {'name': 'Schwarzwaldradio', 'genre': 'Pop', 'country': '', 'languages': '', 'image': [{'url': 'http://static.airable.io/00/34/193476.png', 'size': 'large', 'mediatype': 'image/png'}], 'liveDescription': 'George Michael - Faith', 'stationId': '3542750323191285', 'playQueueItemId': 'beoradio'}}}

below the parts of interest: 

```json
{
  "notification": {
    "type": "NOW_PLAYING_NET_RADIO",
    "data": {
      "name": "Station Name",
      "liveDescription": "Artist - Song Title"
    }
  }
}
```

Find `type`: `NOW_PLAYING_NET_RADIO`.  
Inside `data` there is a field `name`, showing the name of the radio station. This field is needed for the `station_rules.yaml`.  
Identify patterns in `liveDescription` to make rules that filter out `artist`and `title`.  
1) Character that separates Artist and Title
2) Is Artist first or Title
3) Are there any messages that would be identified as a Track and need to be blocked

**Common patterns:**
- `Artist - Song Title`
- `Song Title - Artist`
- `Artist: Song Title`
- `Song Title / Artist`

Taking the example above. 
1) Artist and Song Title are separated by ' - ', leading to `separator: " - "`
2) Artist is first, leading to `artist_first: true`
3) From one entry no `skip_patterns` to determine, but it is always a good idea to add the station name.  
Be aware that a station called 'George Michael' would prevent the example above being scrobbled...  

### Step 3: Create Station Rules

Once you've identified the pattern, create or update your station rules configuration file:

1. **Locate the configuration file:**
   - Path: `appdata/config/station_rules.yaml`
   - If it doesn't exist, a sample file will be created automatically

2. **Add your station rule:**
   ```yaml
   stations:
     "Your Station Name":
       separator: " - "
       artist_first: true
       skip_patterns:
         - "Advertisement"
         - "Station ID"
   ```

### Step 4: Configuration Options

**Available options for each station:**

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| `separator` | string | Character(s) separating artist and title | `" - "`, `" \| "` |
| `artist_first` | boolean | Whether artist comes before title | `true` or `false` |
| `skip_patterns` | list | Strings to skip (e.g., ads, station IDs) | `["Advertisement"]` |

### Step 5: Test Your Configuration

1. **Run `detect` mode** again for updated logs:
   ```bash
   RUN_MODE=detect python -m beo_radio_scrobbler
   ```

2. **Verify the parsing** by checking the logs
   - The log will now show: 
      * first line - the known pattern from above
      * second line - a second entry parsing `Station Name: Artist - Title` from first line

3. **Adjust rules if needed** based on the results

### Step 6: Run in Production

Once you're satisfied with the parsing:

1. **Switch to production mode:**
   ```bash
   RUN_MODE=production python -m beo_radio_scrobbler
   ```

2. **Monitor the scrobbles** in your Last.fm account

3. **Check `appdata/logs/log_scrobbles.log`** for scrobble history

---

### Adding "loved" to a last.fm track that is currently running on the radio

1. **Turn Volume Up**
2. **Turn Volume Down**
3. **Each step is allowed to take one second**


---

## Tips & Tricks

### Handling Multiple Stations

You can define rules for multiple stations in the same `station_rules.yaml` file:

```yaml
stations:
  "Jazz FM":
    separator: " - "
    artist_first: true
  
  "Rock Radio":
    separator: ": "
    artist_first: false
    skip_patterns:
      - "Coming up next"
  
  "Classical Station":
    separator: " | "
    artist_first: true
    skip_patterns:
      - "Station ID"
      - "Support message"
```

### Troubleshooting

**Problem:** Scrobbles not appearing on Last.fm

**Solutions:**
1. Check `appdata/logs/log_scrobbles.log` (production mode) or `appdata/logs/log_radio_scrobbler.log` for errors
2. Verify your Last.fm credentials in `.env` file or -e for the Docker run
3. Ensure the station rule matches the exact station name from the API

**Problem:** Artist and title are swapped

**Solution:**
- Toggle the `artist_first` option in your station rule

**Problem:** Advertisements are being scrobbled

**Solution:**
- Add the advertisement text patterns to `skip_patterns` in your station rule

---

## More Help

For additional information, see:
- [Run Modes Documentation](RUN_MODE.md)
- [Feature Requests](FEATURE_REQUEST.md)

Need help? Open an issue on GitHub!
