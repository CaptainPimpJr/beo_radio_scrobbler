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
   ```bash
   RUN_MODE=detect python -m beo_radio_scrobbler
   ```

2. **Play your radio station** on the BeoSound Radio

3. **Check the log file** at `appdata/logs/log_detections.log`
   - You'll see the complete notification stream data
   - Look for the `NOW_PLAYING_NET_RADIO` notification type

### Step 2: Identify the Metadata Pattern

Examine the log entries to understand how your station formats the metadata:

**Example notification structure:**
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

**Common patterns:**
- `Artist - Song Title`
- `Song Title - Artist`
- `Artist: Song Title`
- `Song Title | Artist`

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

1. **Switch to `detect_smpl` mode** for cleaner logs:
   ```bash
   RUN_MODE=detect_smpl python -m beo_radio_scrobbler
   ```

2. **Verify the parsing** by checking the logs
   - The simplified log will show: `Station Name: Artist - Title`

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

## Tips & Tricks

### Using `detect` vs `detect_smpl`

- **Use `detect`** when:
  - Setting up a new station for the first time
  - Debugging parsing issues
  - You need to see the complete API response

- **Use `detect_smpl`** when:
  - You just need to verify the station name and description
  - Testing your parsing rules
  - You want cleaner, more readable logs

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
2. Verify your Last.fm credentials in `.env` file
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
