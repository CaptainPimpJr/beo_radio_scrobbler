# Run Modes 🚀

The BeoRadio Scrobbler supports different operation modes depending on your needs.

---

## 🎵 `production`

**Default operation mode for continuous scrobbling.**

### What it does:
- Reads the notification stream of [BeoNetClient API](https://documenter.getpostman.com/view/1053298/T1LTe4Lt) indefinitely
- Filters for stream type: `NOW_PLAYING_NET_RADIO`
- Parses artist and title information based on pre-defined rules
  - ℹ️ *Use `detect` or `detect_smpl` modes first to identify parsing rules for your stations*
- Scrobbles the data to [Last.fm](https://www.last.fm/)

### When to use:
- Running the scrobbler in normal operation
- After you've identified your station patterns
- For continuous, automatic scrobbling

---

## 🔍 `detect`

**Full diagnostic mode for discovering station patterns.**

### What it does:
- Captures the current value of notification stream type `NOW_PLAYING_NET_RADIO`
- Writes **complete notification data** to the `detections.log`
- Additionally writes **simplified form** to `stations.log`
  - Simplified form contains: station name + live description
- Helps determine how to parse station name, artist, and title information

### When to use:
- First time setup
- Adding new radio stations
- Debugging parsing issues
- Need full API response details

### Output files:
- 📄 `detections.log` - Full notification stream data
- 📄 `stations.log` - Simplified station info

---

## 🔍 `detect_smpl`

**Simplified diagnostic mode.**

### What it does:
- Just like `detect` mode, but **only** writes simplified form to `stations.log`
- Skips the full notification stream logging
- Faster and cleaner for basic pattern detection

### When to use:
- Quick station pattern identification
- When full API data isn't needed
- Cleaner logs with just essential info

### Output files:
- 📄 `stations.log` - Simplified station info only

---

## 🔔 `notify_me`

**Experimental notification monitoring mode.**

### What it does:
- Logs **all** notifications from the BeoSound Radio
- **Excludes**: `PROGRESS_INFORMATION` (too noisy)
- Writes to a separate log file
- Useful to get a wider picture of BeoSound Radio events

### When to use:
- Exploring what events the radio broadcasts
- Understanding the full API behavior
- Debugging connectivity issues
- Curiosity about what else is happening 🤔

### Output files:
- 📄 `notifications.log` - All notification events

> ⚠️ **Note**: This mode generates a lot of data. Use sparingly and for diagnostic purposes only.

---

## Configuration

To set the run mode, configure your environment variable or command-line parameter:

```bash
# Example with environment variable
RUN_MODE=production python -m beo_radio_scrobbler

# Example with detect mode
RUN_MODE=detect python -m beo_radio_scrobbler
```

---

## Mode Comparison Table

| Mode | Logs Everything | Scrobbles | Best For | Output Files |
|------|----------------|-----------|----------|--------------|
| `production` | ❌ | ✅ | Normal operation | None |
| `detect` | ✅ | ❌ | Full diagnostics | detections.log, stations.log |
| `detect_smpl` | Simplified | ❌ | Quick diagnostics | stations.log |
| `notify_me` | ✅ | ❌ | API exploration | notifications.log |