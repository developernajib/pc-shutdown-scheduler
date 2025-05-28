# PC Shutdown Scheduler - Enhanced Batch Version Setup Instructions

## 🚀 Features

### ✅ **Core Functionality**

-   **Automatic PC shutdown at 11:00 PM** on weekdays (Monday-Thursday)
-   **Two-stage warning system** with user-friendly dialogs
-   **Silent background operation** with comprehensive logging
-   **No Python dependencies** - runs natively on Windows

### 🎉 **Friday Weekend Exemption**

-   **No shutdown on Fridays** - script automatically exits with weekend message
-   **Dynamic Friday detection** - monitors day changes during execution
-   **Multiple Friday safeguards** - checks at startup, runtime, and before shutdown

### 💬 **Enhanced Dialog System**

-   **Beautiful HTA-based dialogs** with modern styling and clear messaging
-   **Live countdown timer** in final warning dialog
-   **Intuitive button labeling** - "YES - Cancel Shutdown" vs "NO - Let PC Shutdown"
-   **Always-on-top dialogs** to ensure visibility

### 🛡️ **Smart Cancellation Logic**

-   **Complete script termination** when user cancels shutdown
-   **Proper cleanup** of temporary files and processes
-   **Clear confirmation messages** when shutdown is canceled
-   **No accidental shutdowns** - user must actively choose to proceed

## 📋 **Behavior Summary**

| Day                       | User Action                   | Result                                        |
| ------------------------- | ----------------------------- | --------------------------------------------- |
| **Monday-Thursday**       | No interaction with dialogs   | PC shuts down at 11:00 PM                     |
| **Monday-Thursday**       | Click "YES - Cancel Shutdown" | Shutdown canceled, script exits               |
| **Monday-Thursday**       | Click "NO - Let PC Shutdown"  | PC shuts down at 11:00 PM                     |
| **Friday**                | Any                           | Script exits immediately with weekend message |
| **Day changes to Friday** | Any                           | Script detects change and exits gracefully    |

## 🕐 **Schedule Timeline**

1. **9:30 PM** - First warning dialog appears

    - "Do you want to cancel the shutdown?"
    - User can cancel or proceed

2. **10:50 PM** - Final warning dialog appears (if not canceled)

    - "Your PC will shut down in 10 minutes!"
    - Live countdown timer shows remaining minutes
    - Last chance to cancel

3. **11:00 PM** - Automatic shutdown (if not canceled)
    - PC shuts down automatically with 5-second delay
    - All dialogs are closed automatically

## 🔧 **Installation Instructions**

### 1. Save the Batch Script

-   Copy the entire batch script code
-   Save as a new text file with `.bat` extension
-   **Recommended location:** `C:\Scripts\shutdown_scheduler.bat`
-   Ensure the folder exists before saving

### 2. Set Up Automatic Startup

**Method 1: Windows Startup Folder (Recommended)**

-   Press `Win + R` → type `shell:startup` → press Enter
-   Right-click in the Startup folder → "New" → "Shortcut"
-   Browse to your batch file location
-   Name the shortcut "PC Shutdown Scheduler"

**Method 2: Task Scheduler (Advanced)**

-   Open Task Scheduler → "Create Basic Task"
-   Set trigger to "When I log on"
-   Set action to start your batch file
-   Run with highest privileges for reliable shutdown

### 3. Test the Installation

-   **Modify times** temporarily to test (e.g., 2-3 minutes ahead)
-   **Run the script** manually to verify dialogs appear
-   **Check the log file** at `%USERPROFILE%\shutdown_scheduler.log`
-   **Test cancellation** by clicking "YES - Cancel Shutdown"

## ⚙️ **Configuration**

You can customize the shutdown schedule by editing these variables at the top of the batch file:

```batch
:: Configure times (24-hour format)
set "FIRST_DIALOG_HOUR=21"     :: First dialog at 9:30 PM
set "FIRST_DIALOG_MIN=30"
set "SECOND_DIALOG_HOUR=22"    :: Final dialog at 10:50 PM
set "SECOND_DIALOG_MIN=50"
set "SHUTDOWN_HOUR=23"         :: Shutdown at 11:00 PM
set "SHUTDOWN_MIN=00"
```

### 🕒 **Time Configuration Examples**

**For 10:00 PM shutdown:**

```batch
set "FIRST_DIALOG_HOUR=20"     :: 8:30 PM first dialog
set "FIRST_DIALOG_MIN=30"
set "SECOND_DIALOG_HOUR=21"    :: 9:50 PM final dialog
set "SECOND_DIALOG_MIN=50"
set "SHUTDOWN_HOUR=22"         :: 10:00 PM shutdown
set "SHUTDOWN_MIN=00"
```

**For midnight shutdown:**

```batch
set "FIRST_DIALOG_HOUR=22"     :: 10:30 PM first dialog
set "FIRST_DIALOG_MIN=30"
set "SECOND_DIALOG_HOUR=23"    :: 11:50 PM final dialog
set "SECOND_DIALOG_MIN=50"
set "SHUTDOWN_HOUR=00"         :: 12:00 AM shutdown (next day)
set "SHUTDOWN_MIN=00"
```

## 📊 **Logging & Monitoring**

### Log File Location

-   **Path:** `%USERPROFILE%\shutdown_scheduler.log`
-   **Access:** Navigate to `C:\Users\[YourUsername]\shutdown_scheduler.log`

### Log Contents Include

-   Script startup and day detection
-   Dialog display events
-   User interactions (cancel/proceed)
-   Friday detection and exemptions
-   Shutdown execution status
-   Error conditions and cleanup operations

### Sample Log Entries

```
[12/06/2024 21:25:30]: ✅ Shutdown scheduler started and running in background
[12/06/2024 21:25:30]: 📅 Today is Thursday - shutdown is scheduled
[12/06/2024 21:30:15]: 📢 Displaying first shutdown warning dialog
[12/06/2024 21:32:45]: ⏭️ User clicked NO - will proceed with scheduled shutdown
[12/06/2024 22:50:10]: 📢 Displaying final shutdown warning dialog (10 minutes remaining)
[12/06/2024 23:00:00]: 🔴 PC SHUTDOWN INITIATED at scheduled time (11:00 PM)
```

## 🛠️ **Technical Details**

### System Requirements

-   **Windows 7/8/10/11** (any version)
-   **Administrator privileges** recommended for reliable shutdown
-   **HTA support** (built into Windows)

### Files Created

-   `%TEMP%\shutdown_dialog.hta` - First dialog interface
-   `%TEMP%\shutdown_final_dialog.hta` - Final warning dialog
-   `%TEMP%\shutdown_*.tmp` - Temporary status files
-   `%USERPROFILE%\shutdown_scheduler.log` - Event log

### Background Operation

-   Script runs **hidden** in background after initial startup
-   **Minimal CPU usage** - only checks time every 30 seconds
-   **Automatic cleanup** of temporary files on exit

## 🔍 **Troubleshooting**

### Script Doesn't Start

-   **Check file extension:** Must be `.bat` not `.txt`
-   **Run as Administrator:** Right-click → "Run as administrator"
-   **Check startup folder:** Verify shortcut is in correct location

### Dialogs Don't Appear

-   **Check system time:** Ensure PC clock is accurate
-   **Review log file:** Look for error messages
-   **Test manually:** Run script directly to see immediate results

### Shutdown Doesn't Work

-   **Administrator privileges:** Script needs admin rights for shutdown
-   **Check Task Manager:** Look for mshta.exe processes (dialogs)
-   **Windows updates:** Restart may be required for some Windows updates

### Friday Issues

-   **Time zone:** Script uses local system time
-   **Regional settings:** Uses Windows date/time format
-   **Manual override:** Temporarily edit script to test on other days

## 🎯 **Best Practices**

### For Optimal Performance

1. **Place script in permanent location** (not Desktop or Downloads)
2. **Run with administrator privileges** for reliable shutdown
3. **Monitor log file** occasionally to verify proper operation
4. **Test configuration changes** before relying on them

### For Security

1. **Keep script location secure** from unauthorized modification
2. **Regular log review** to detect any issues
3. **Backup your configuration** before making changes

## 📝 **Advanced Customization**

### Modify Dialog Messages

Edit the HTA dialog creation sections to customize messages:

-   Look for lines containing `echo` and dialog text
-   Modify the text between quotes
-   Maintain the HTA syntax structure

### Change Visual Styling

Modify the CSS styles in the HTA sections:

-   Background colors, fonts, button styles
-   Dialog size and positioning
-   Color schemes and animations

### Add Email Notifications

Extend the script to send emails when shutdown occurs:

-   Use `blat` or similar command-line email tools
-   Add email sending logic before shutdown execution
-   Include log information in email body

---

## 💡 **Need Help?**

If you encounter issues:

1. **Check the log file** for detailed error information
2. **Test with modified times** (2-3 minutes ahead) for immediate results
3. **Run manually** from command prompt to see any error messages
4. **Verify administrator privileges** by running as administrator

**Remember:** This script will shut down your PC automatically. Always save your work before the scheduled shutdown time!
