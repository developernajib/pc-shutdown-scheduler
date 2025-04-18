# 🕙 Automatic PC Shutdown Scheduler

A Python-based utility that automatically shuts down your PC at a scheduled time, with configurable notifications and smart features to ensure shutdown policies are enforced.

### 📋 Available Versions

This repository contains two versions of the shutdown scheduler:

- **Normal Version**: Simple, clean implementation with minimal logging and straightforward notifications
- **Extended Version**: More advanced features including restart evasion detection and admin overrides

### 🚀 Normal Version

The Normal Version provides a simple, reliable automatic shutdown solution that runs silently in the background until notification times.

#### ✨ Features

| Feature | Description |
|---------|-------------|
| **⏱️ Precise Timed Shutdown** | <ul><li>Automatically shuts down the PC at exactly 11:00 PM</li><li>No delay between scheduled time and actual shutdown execution</li></ul> |
| **🔔 Two-Phase Notifications** | <ul><li>First dialog shown precisely from 9:30 PM to 10:50 PM</li><li>Second dialog shown precisely from 10:50 PM until 11:00 PM shutdown</li></ul> |
| **⏳ Time-Based Dialog Transition** | <ul><li>First dialog automatically closes at exactly 10:50 PM</li><li>Second dialog appears immediately at 10:50 PM</li></ul> |
| **⚠️ 10-Minute Final Warning** | <ul><li>Clear 10-minute warning before shutdown (10:50 PM to 11:00 PM)</li><li>Persistent warning remains visible for the entire 10-minute period</li></ul> |
| **⏰ Pre-Configured Timing** | <ul><li>Shutdown time: 11:00 PM (23:00)</li><li>First notification: 9:30 PM (21:30)</li><li>Final warning: 10:50 PM (22:50)</li></ul> |
| **❌ Simple Cancellation** | <ul><li>Shutdown can be canceled at any point between 9:30 PM and 11:00 PM</li><li>Single-click cancellation through dialog interface</li></ul> |
| **🔲 Background Operation** | <ul><li>Runs invisibly until scheduled notification times</li><li>Only becomes visible at 9:30 PM when first dialog appears</li></ul> |
| **💻 Cross-Platform** | <ul><li>Works on Windows, macOS, and Linux</li><li>Instant shutdown execution at 11:00 PM on all platforms</li></ul> |
| **📝 Minimal Logging** | <ul><li>Logs script startup time</li><li>Logs the exact time when shutdown is initiated at 11:00 PM</li></ul> |
| **🔄 Startup Integration** | <ul><li>Designed to run silently from system startup until 9:30 PM</li><li>Low resource usage during waiting periods</li></ul> |
| **🖥️ Hidden Console** | <ul><li>No visible console window at any time</li><li>Clean user experience with dialogs appearing only at scheduled times</li></ul> |
| **⚕️ Error Handling** | <ul><li>Ensures reliable 11:00 PM shutdown even if errors occur</li><li>Maintains timing accuracy in all scenarios</li></ul> |

### 🔥 Extended Version

The Extended Version includes advanced features for organizations that need to strictly enforce shutdown policies, including restart evasion detection and admin overrides.

#### ✨ Features

| Feature | Description |
|---------|-------------|
| **⏱️ Scheduled Shutdown** | <ul><li>Automatically shuts down the PC at 11:00 PM</li><li>Can be configured to use different shutdown times</li></ul> |
| **🔔 Two-Step Confirmation** | <ul><li>First confirmation dialog at 9:30 PM</li><li>Final confirmation dialog at 10:50 PM (10 minutes before shutdown)</li></ul> |
| **❌ User Cancellation Options** | <ul><li>Users can cancel the shutdown at either confirmation dialog</li><li>Clear "Yes/No" options with explanatory text</li></ul> |
| **⏲️ Auto-Timeout on Dialogs** | <ul><li>Final confirmation dialog automatically closes after 60 seconds if no response</li><li>Default behavior proceeds with shutdown if user doesn't respond</li></ul> |
| **🔒 Restart Evasion Detection** | <ul><li>Detects if PC was restarted around shutdown time to avoid shutdown</li><li>Shows special dialog with shorter timeout (30 seconds) for evasion attempts</li><li>Enforces more immediate shutdown (2-minute warning) for evasion attempts</li></ul> |
| **🔑 Admin Override Capability** | <ul><li>Allows administrators to override shutdown with password verification</li><li>Can be customized with organization-specific authentication</li></ul> |
| **🔲 Background Operation** | <ul><li>Runs invisibly in the background</li><li>Only shows dialog boxes when needed</li><li>No console window or visible UI during operation</li></ul> |
| **💻 Cross-Platform Compatibility** | <ul><li>Works on Windows, macOS, and Linux</li><li>Uses platform-specific shutdown commands</li></ul> |
| **📝 Detailed Logging** | <ul><li>Records all events in shutdown_scheduler.log</li><li>Logs errors to shutdown_error.log</li><li>Includes timestamps for tracking</li></ul> |
| **⚕️ Graceful Error Handling** | <ul><li>Handles exceptions without crashing</li><li>Logs errors for troubleshooting</li></ul> |
| **👁️ Always-on-Top Dialogs** | <ul><li>Ensures confirmation dialogs are visible to users</li><li>Centers dialogs on screen for visibility</li></ul> |
| **🕙 Configurable Time Format** | <ul><li>Supports easy configuration using 12-hour time format</li></ul> |

### 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/developernajib/pc-shutdown-scheduler.git
   ```

2. Add to Windows startup:
   - Press `Win + R` to open the Run dialog
   - Type `shell:startup` and press Enter to open the Startup folder
   - Right-click in the folder and select "New > Shortcut"
   - Browse to the location of your Python script (or use the full path)
   - Example path: `C:\Python\pythonw.exe C:\path\to\shutdown_scheduler.py`
   - Name the shortcut "PC Shutdown Scheduler" and click Finish
   
   For other operating systems:
   - **macOS**: Add to System Preferences > Users & Groups > Login Items
   - **Linux**: Add to startup applications through your desktop environment settings

### ⚙️ Configuration

You can configure the shutdown and notification times by modifying these lines in the script:

```python
# Times in 12-hour format (converted to datetime.time objects)
first_dialog_time = datetime.time(21, 30)    # 9:30 PM
second_dialog_time = datetime.time(22, 50)   # 10:50 PM (10 minutes before shutdown)
shutdown_time = datetime.time(23, 0)         # 11:00 PM
```

### 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

### 📜 Author

**Name:** Md. Najib Islam  
**Signature:** DeveloperNajib  
**Profession:** Software Engineer  
**ORCID:** [Md. Najib Islam](https://orcid.org/0009-0005-8578-7790)
**Contact:** [Telegram](https://t.me/developernajib)  