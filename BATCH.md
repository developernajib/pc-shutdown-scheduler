# PC Shutdown Scheduler - Batch Version Setup Instructions

### How to Install

1. **Save the Batch Script:**
   - Copy the entire batch script to a new text file
   - Save the file with a `.bat` extension (e.g., `shutdown_scheduler.bat`)
   - Save it to a permanent location (e.g., `C:\Scripts\shutdown_scheduler.bat`)

2. **Add to Windows Startup:**
   - Press `Win + R` to open the Run dialog
   - Type `shell:startup` and press Enter to open the Startup folder
   - Right-click in the folder and select "New > Shortcut"
   - Browse to the location of your batch file
   - Enter the path to your batch file (e.g., `C:\Scripts\shutdown_scheduler.bat`)
   - Name the shortcut "PC Shutdown Scheduler" and click Finish

### How It Works

This batch implementation provides similar functionality to the Python version:

1. **First Dialog (9:30 PM - 10:50 PM):**
   - Shows a dialog asking if you want to cancel the scheduled shutdown
   - Options: "Yes (Cancel Shutdown)" or "No (Proceed with Shutdown)"

2. **Second Dialog (10:50 PM - 11:00 PM):**
   - Shows a final warning that the PC will shut down in 10 minutes
   - Only option: "Yes (Cancel Shutdown)" - dialog stays open until shutdown

3. **Automatic Shutdown:**
   - PC will automatically shut down at 11:00 PM if not canceled

### Configuration

You can modify the shutdown times by editing these lines at the top of the batch file:

```batch
:: Configure times (24-hour format)
set "FIRST_DIALOG_HOUR=21"
set "FIRST_DIALOG_MIN=30"
set "SECOND_DIALOG_HOUR=22"
set "SECOND_DIALOG_MIN=50"
set "SHUTDOWN_HOUR=23"
set "SHUTDOWN_MIN=00"
```

### Notes

- The script runs silently in the background
- Dialog boxes are created using HTA technology (HTML Application)
- Logs are saved to `%USERPROFILE%\shutdown_scheduler.log`