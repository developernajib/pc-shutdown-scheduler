# 🕙 Automatic PC Shutdown Scheduler

A Python-based utility that automatically shuts down your PC at a scheduled time, with configurable notifications, smart features, and weekend exemptions to ensure shutdown policies are enforced while respecting work-life balance.

## 📋 Available Versions

This repository contains multiple versions of the shutdown scheduler:

-   **🌟 Enhanced Normal Version**: Clean implementation with Friday exemption and reliable shutdown
-   **🔥 Enhanced Extended Version**: Advanced features including restart evasion detection, admin overrides, and Friday exemption
-   **📄 Batch Version**: Native Windows batch script version with all enhanced features

---

## 🌟 Enhanced Normal Version

The Enhanced Normal Version provides a simple, reliable automatic shutdown solution with weekend respect and bulletproof shutdown execution.

### ✨ Key Features

| Feature                         | Description                                                                                                                                                                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **🎉 Friday Weekend Exemption** | <ul><li>**No shutdown on Fridays** - script automatically exits</li><li>**Dynamic Friday detection** - monitors day changes during execution</li><li>**Weekend message display** - shows friendly "Enjoy your weekend!" message</li></ul>   |
| **⏱️ Bulletproof Shutdown**     | <ul><li>**Multiple shutdown methods** with fallbacks for Windows 10 Pro</li><li>**Administrator privilege requests** for reliable shutdown execution</li><li>**Absolute shutdown timer** that executes regardless of dialog state</li></ul> |
| **🔔 Enhanced Notifications**   | <ul><li>**Clear dialog messaging** - "YES - Cancel Shutdown" vs "NO - Let PC Shutdown"</li><li>**Modern dialog styling** with better visual hierarchy</li><li>**Always-on-top dialogs** ensuring visibility</li></ul>                       |
| **✅ Smart Cancellation**       | <ul><li>**Complete script termination** when user cancels</li><li>**Confirmation messages** when shutdown is canceled</li><li>**No accidental shutdowns** - user must actively choose to proceed</li></ul>                                  |
| **⏰ Precise Timing**           | <ul><li>**Shutdown time**: 11:00 PM (Monday-Thursday only)</li><li>**First notification**: 9:30 PM</li><li>**Final warning**: 10:50 PM with 10-minute countdown</li></ul>                                                                   |
| **🔲 Background Operation**     | <ul><li>**Hidden console window** with professional background operation</li><li>**Low resource usage** during waiting periods</li><li>**Comprehensive logging** for monitoring and troubleshooting</li></ul>                               |
| **💻 Enhanced Compatibility**   | <ul><li>**Windows 10/11 Pro support** with admin privilege handling</li><li>**Cross-platform compatibility** (Windows, macOS, Linux)</li><li>**Reliable shutdown commands** for all supported platforms</li></ul>                           |

### 📅 Weekly Schedule Behavior

| Day                 | Behavior                                | Result                                         |
| ------------------- | --------------------------------------- | ---------------------------------------------- |
| **Monday-Thursday** | Normal operation                        | Dialogs → 11 PM shutdown (unless canceled)     |
| **Friday**          | Immediate exit                          | "🎉 It's Friday! No shutdown scheduled today." |
| **Saturday-Sunday** | Script not designed for weekend running | -                                              |

---

## 🔥 Enhanced Extended Version

The Enhanced Extended Version includes all normal features plus advanced organizational enforcement capabilities with weekend respect.

### ✨ Advanced Features

| Feature                                   | Description                                                                                                                                                                                                                                                                                                              |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **🎉 Friday Weekend Exemption**           | <ul><li>**Complete Friday exemption** across all features including restart evasion</li><li>**Smart weekend detection** that overrides all enforcement mechanisms</li><li>**Runtime Friday monitoring** with graceful script termination</li></ul>                                                                       |
| **🔒 Advanced Restart Evasion Detection** | <ul><li>**Friday-aware evasion detection** - respects weekend even during evasion</li><li>**Emergency shutdown dialogs** with shorter timeouts (30 seconds)</li><li>**Immediate shutdown enforcement** (2-minute warning) for evasion attempts</li><li>**System policy violation alerts** with clear messaging</li></ul> |
| **🔑 Enhanced Admin Override**            | <ul><li>**Password-protected admin override** (default: "admin123")</li><li>**Friday exemption for admin overrides** - no override needed on Friday</li><li>**Proper admin authentication flow** with access denied handling</li></ul>                                                                                   |
| **⚡ Bulletproof Shutdown System**        | <ul><li>**Triple-fallback shutdown methods** for maximum reliability</li><li>**Administrator privilege auto-elevation** on Windows</li><li>**Enhanced Windows 10 Pro compatibility**</li><li>**Subprocess and system command fallbacks**</li></ul>                                                                       |
| **🔔 Advanced Dialog System**             | <ul><li>**Auto-timeout dialogs** with user-friendly countdowns</li><li>**Enhanced visual styling** with color-coded buttons</li><li>**Friday-aware dialog logic** - no dialogs shown on Friday</li><li>**Proper dialog threading** to prevent blocking</li></ul>                                                         |
| **📊 Comprehensive Monitoring**           | <ul><li>**Detailed event logging** with emoji-coded status messages</li><li>**Friday detection logging** with clear weekend messages</li><li>**Admin action tracking** with override attempt logs</li><li>**Error logging with fallback handling**</li></ul>                                                             |
| **🛡️ Multi-Layer Protection**             | <ul><li>**Startup Friday check** - exits immediately if Friday</li><li>**Runtime Friday monitoring** - exits if day changes to Friday</li><li>**Pre-shutdown Friday verification** - final safety check</li><li>**Cancellation-aware timers** that respect user choice</li></ul>                                         |

### 🔄 Advanced Behavior Matrix

| Scenario              | Monday-Thursday    | Friday               | Result                       |
| --------------------- | ------------------ | -------------------- | ---------------------------- |
| **Normal Operation**  | Dialogs → Shutdown | Script exits         | Respects weekend             |
| **User Cancellation** | Shutdown canceled  | N/A (no dialogs)     | User choice respected        |
| **Restart Evasion**   | Emergency shutdown | Script exits         | Friday overrides enforcement |
| **Admin Override**    | Override possible  | N/A (no enforcement) | Balanced control             |

---

## 📄 Batch Version Features

### 🚀 Native Windows Implementation

| Feature                         | Description                                                                                                                                                                                   |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **🎉 Friday Weekend Exemption** | <ul><li>**Native Windows date detection** using wmic commands</li><li>**Immediate Friday exit** with weekend messages</li><li>**Runtime Friday monitoring** during script execution</li></ul> |
| **💬 Beautiful HTA Dialogs**    | <ul><li>**Modern HTML-based dialogs** with CSS styling</li><li>**Live countdown timers** in final warning dialog</li><li>**Professional button styling** with clear action labels</li></ul>   |
| **⚡ No Dependencies**          | <ul><li>**Pure Windows batch script** - no Python required</li><li>**Built-in HTA technology** for rich dialogs</li><li>**Native Windows shutdown commands**</li></ul>                        |
| **🔧 Enhanced Reliability**     | <ul><li>**Multiple Friday safety checks** throughout execution</li><li>**Proper process cleanup** when user cancels</li><li>**Comprehensive temp file management**</li></ul>                  |

---

## 🛠️ Installation & Setup

### 1. **Python Versions (Normal & Extended)**

```bash
# Clone the repository
git clone https://github.com/developernajib/pc-shutdown-scheduler.git
cd pc-shutdown-scheduler

# Choose your version:
# - shutdown_scheduler_normal.py (Enhanced Normal)
# - shutdown_scheduler_extended.py (Enhanced Extended)
```

### 2. **Windows Startup Integration**

**Method 1: Startup Folder (Recommended)**

```bash
# Press Win + R, type: shell:startup
# Create shortcut with target:
C:\Python\pythonw.exe "C:\path\to\shutdown_scheduler.py"
```

**Method 2: Task Scheduler (Advanced)**

-   Create task that runs at startup
-   Set to run with highest privileges
-   Use pythonw.exe to run silently

### 3. **Batch Version**

```bash
# Save as shutdown_scheduler.bat
# Add to startup folder or Task Scheduler
# Run with administrator privileges for reliable shutdown
```

---

## ⚙️ Configuration

### 🕐 Time Settings

```python
# Modify these variables for custom timing:
first_dialog_time = datetime.time(21, 30)    # 9:30 PM first warning
second_dialog_time = datetime.time(22, 50)   # 10:50 PM final warning
shutdown_time = datetime.time(23, 0)         # 11:00 PM shutdown
```

### 🔐 Admin Override (Extended Version Only)

```python
# Change the admin password in show_restart_evasion_dialog():
if admin_check == "your_custom_password":  # Replace "admin123"
    # Admin override accepted
```

### 🎯 Friday Exemption (All Versions)

The Friday exemption is built-in and automatic:

-   **Detects Friday using system weekday**
-   **Cannot be disabled** (by design for work-life balance)
-   **Overrides all other features** including restart evasion

---

## 📊 Logging & Monitoring

### 📝 Log Files Created

| File                     | Purpose        | Location         |
| ------------------------ | -------------- | ---------------- |
| `shutdown_scheduler.log` | Main event log | Script directory |
| `shutdown_error.log`     | Error tracking | Script directory |

### 🔍 Sample Log Entries

```
[2024-12-06 21:25:30]: 🚀 Shutdown Scheduler started with enhanced reliability
[2024-12-06 21:25:30]: 📅 Today is Thursday - shutdown is scheduled
[2024-12-06 21:30:15]: 📢 Displaying first shutdown warning dialog
[2024-12-06 21:32:45]: ⏭️ User clicked NO - will proceed with scheduled shutdown
[2024-12-06 22:50:10]: 📢 Displaying final shutdown warning dialog (10 minutes remaining)
[2024-12-06 23:00:00]: 🔴 PC SHUTDOWN INITIATED at scheduled time (11:00 PM)
```

**Friday Log Example:**

```
[2024-12-08 18:45:12]: 🎉 TODAY IS FRIDAY - Shutdown scheduler disabled for the weekend!
[2024-12-08 18:45:12]: 📅 The scheduler will resume automatically on Monday
```

---

## 🔧 System Requirements

### **Python Versions**

-   **Python 3.6+** (recommended: 3.8+)
-   **tkinter** (usually included with Python)
-   **Windows**: Additional `win32gui` for hidden console (optional)

### **Batch Version**

-   **Windows 7/8/10/11** (any edition)
-   **HTA support** (built into Windows)
-   **Administrator privileges** (recommended)

### **All Versions**

-   **System clock accuracy** for precise timing
-   **Startup permissions** for automatic launch

---

## 🛡️ Security & Best Practices

### ✅ **Recommended Setup**

1. **Run with administrator privileges** for reliable shutdown
2. **Place scripts in secure location** (not Desktop/Downloads)
3. **Monitor log files** occasionally for proper operation
4. **Test configuration changes** before relying on them

### 🔐 **Security Notes**

-   **Admin password in Extended version** should be changed from default
-   **Log files contain timestamps** but no sensitive information
-   **Script respects user cancellation** - not malicious enforcement

---

## 🚨 Important Behavior Notes

### ⚠️ **Automatic Shutdown Behavior**

-   **PC WILL shutdown at 11 PM** on Monday-Thursday if no user interaction
-   **Friday is completely exempt** - no dialogs, no shutdown
-   **User can cancel anytime** by clicking "YES - Cancel Shutdown"
-   **Clicking NO or ignoring dialogs** will result in shutdown

### 🎉 **Friday Weekend Exemption**

-   **Cannot be overridden** - this is intentional for work-life balance
-   **Script exits immediately** on Friday startup
-   **All enforcement mechanisms respect Friday** including restart evasion
-   **Resumes automatically on Monday** when next run

---

## 🐛 Troubleshooting

### **Common Issues**

| Problem                        | Solution                                                 |
| ------------------------------ | -------------------------------------------------------- |
| **Script doesn't shutdown PC** | Run as administrator, check Windows 10 Pro compatibility |
| **Dialogs don't appear**       | Check system time accuracy, verify script is running     |
| **Friday detection issues**    | Check system date/time settings and regional format      |
| **Admin override not working** | Verify password spelling, check Extended version         |

### **Debug Steps**

1. **Check log files** for detailed error information
2. **Test with modified times** (2-3 minutes ahead) for immediate results
3. **Run script manually** from command line to see error messages
4. **Verify admin privileges** especially on Windows 10 Pro

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📜 Author

**Name:** Md. Najib Islam  
**Signature:** DeveloperNajib  
**Profession:** Software Engineer  
**ORCID:** [0009-0005-8578-7790](https://orcid.org/0009-0005-8578-7790)  
**Contact:** [Telegram](https://t.me/developernajib)

---

## 💡 **Remember**

> **This script will automatically shutdown your PC at 11 PM Monday-Thursday. Always save your work before the scheduled time!**
>
> **Fridays are automatically exempt** - enjoy your weekend! 🎉
