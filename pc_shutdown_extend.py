import tkinter as tk
from tkinter import messagebox
import datetime
import time
import threading
import os
import sys
import subprocess
import ctypes

# Try to import Windows-specific modules if available
try:
    import win32gui
    import win32con
    windows_available = True
except ImportError:
    windows_available = False

# Real times for the shutdown schedule
first_dialog_time = datetime.time(21, 30)    # 9:30 PM
second_dialog_time = datetime.time(22, 50)   # 10:50 PM (10 minutes before shutdown)
shutdown_time = datetime.time(23, 0)         # 11:00 PM

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Status tracking
first_dialog_shown = False
second_dialog_shown = False
immediate_shutdown = False
shutdown_canceled = False

def is_friday():
    """Check if today is Friday (weekday 4)"""
    return datetime.datetime.now().weekday() == 4

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the script with administrator privileges"""
    if is_admin():
        return True
    else:
        log_message("🔐 Requesting administrator privileges for reliable shutdown")
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            return False
        except:
            log_message("❌ Failed to get administrator privileges")
            return False

def log_startup_info():
    with open("shutdown_scheduler.log", "a") as f:
        f.write(f"Shutdown Scheduler: Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def log_message(message):
    """Log a message to file instead of printing to console"""
    try:
        with open(os.path.join(SCRIPT_DIR, "shutdown_scheduler.log"), "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp}: {message}\n")
    except Exception as e:
        try:
            with open(os.path.join(SCRIPT_DIR, "shutdown_error.log"), "a") as f:
                f.write(f"{datetime.datetime.now()}: Failed to write to main log: {str(e)}\n")
        except:
            pass

def check_restart_evasion():
    """
    Check if the PC has been restarted to evade shutdown.
    Returns True if we need to shut down immediately.
    """
    # First check if it's Friday - no shutdown on Friday regardless of evasion
    if is_friday():
        log_message("🎉 Friday detected during restart evasion check - no shutdown needed")
        return False
    
    now = datetime.datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    # If it's already past shutdown time on the same day, immediate shutdown is needed
    if current_time >= shutdown_time:
        log_message("⚠️ Detected script start after shutdown time - possible restart evasion")
        return True
        
    return False

def show_restart_evasion_dialog():
    """Shows a special dialog when restart evasion is detected"""
    global shutdown_canceled
    
    # Double-check it's not Friday
    if is_friday():
        log_message("🎉 Restart evasion detected but it's Friday - no shutdown")
        return False
    
    root = tk.Tk()
    root.withdraw()
    
    # Set a timeout for the dialog (30 seconds - shorter for evasion attempts)
    timeout_response = [False]  # Default: proceed with shutdown
    
    def on_response(response):
        timeout_response[0] = response
        root.quit()
    
    def on_timeout():
        log_message("⏰ Evasion dialog timeout - no user response. Proceeding with immediate shutdown.")
        root.quit()
    
    # Create custom dialog with timeout
    dialog_frame = tk.Toplevel(root)
    dialog_frame.title("⚠️ Emergency Shutdown Warning")
    dialog_frame.geometry("450x200")
    dialog_frame.protocol("WM_DELETE_WINDOW", lambda: on_response(False))  # Handle window close
    
    # Keep dialog on top with higher priority
    dialog_frame.attributes('-topmost', True)
    
    # Message
    tk.Label(dialog_frame, text="🚨 System Policy Violation Detected! 🚨", pady=10, font=("Arial", 12, "bold"), fg="red").pack()
    tk.Label(dialog_frame, text="Your PC should have been shut down at 11:00 PM.", pady=5).pack()
    tk.Label(dialog_frame, text="Possible restart evasion detected.", pady=5, font=("Arial", 10), fg="orange").pack()
    tk.Label(dialog_frame, text="The system will shut down in 2 minutes unless overridden.", pady=5).pack()
    
    # Buttons
    button_frame = tk.Frame(dialog_frame)
    button_frame.pack(pady=15)
    tk.Button(button_frame, text="Override (Admin Only)", width=20, 
             command=lambda: on_response(True), bg="orange", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Shut Down Now", width=15, 
             command=lambda: on_response(False), bg="red", fg="white").pack(side=tk.RIGHT, padx=10)
    
    # Set timeout (30 seconds for evasion attempts)
    dialog_frame.after(30000, on_timeout)
    
    # Center dialog
    dialog_frame.update_idletasks()
    width = dialog_frame.winfo_width()
    height = dialog_frame.winfo_height()
    x = (dialog_frame.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog_frame.winfo_screenheight() // 2) - (height // 2)
    dialog_frame.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Run dialog
    root.mainloop()
    
    # Process result
    if timeout_response[0]:
        log_message("🔐 Admin override requested after restart evasion detection.")
        
        # Ask for admin password (this is just a deterrent, not real security)
        admin_root = tk.Tk()
        admin_root.withdraw()
        admin_check = messagebox.askstring("Admin Verification", 
                                         "Enter admin password to override shutdown:",
                                         show='*')
        admin_root.destroy()
        
        # Simple check - in a real app, you'd use proper authentication
        if admin_check == "admin123":  # Replace with a better method in production
            log_message("✅ Admin override accepted - shutdown canceled.")
            shutdown_canceled = True
            messagebox.showinfo("Override Accepted", "Shutdown has been overridden by administrator.")
            return False  # Don't shut down
        else:
            log_message("❌ Invalid admin override attempt.")
            messagebox.showinfo("Access Denied", "Invalid credentials. Shutdown will proceed.")
            return True  # Shut down
    else:
        log_message("🔴 Immediate shutdown will proceed after restart evasion detection.")
        return True  # Shut down

def show_first_dialog():
    """Shows the first confirmation dialog (9:30 PM - 11:00 PM)"""
    global first_dialog_shown, shutdown_canceled
    
    if first_dialog_shown or shutdown_canceled:
        return
    
    log_message("📢 Displaying first shutdown warning dialog")
    
    root = tk.Tk()
    root.withdraw()
    
    # Keep the dialog on top
    root.attributes('-topmost', True)
    
    response = messagebox.askyesno(
        "Shutdown Confirmation",
        "Your PC is scheduled to shut down at 11:00 PM.\n\nDo you want to cancel the shutdown?",
        icon="warning"
    )
    
    if response:  # User clicked YES to cancel shutdown
        shutdown_canceled = True
        log_message("✅ SHUTDOWN CANCELED by user at first dialog (clicked YES)")
        root.destroy()
        
        # Show confirmation that shutdown was canceled
        confirm_root = tk.Tk()
        confirm_root.withdraw()
        messagebox.showinfo("Shutdown Canceled", 
                          "✅ The scheduled shutdown has been canceled!\n\nYour PC will NOT shut down at 11:00 PM today.")
        confirm_root.destroy()
        
        log_message("🛑 Script terminating - shutdown canceled by user")
        os._exit(0)  # Force exit the script
    else:
        log_message("⏭️ User clicked NO - will proceed with scheduled shutdown")
    
    first_dialog_shown = True
    root.destroy()

def show_second_dialog():
    """Shows the final confirmation dialog (10:50 PM)"""
    global second_dialog_shown, shutdown_canceled
    
    if second_dialog_shown or shutdown_canceled:
        return
    
    log_message("📢 Displaying final shutdown warning dialog (10 minutes remaining)")
    
    root = tk.Tk()
    root.withdraw()
    
    # Set a timeout for the dialog (60 seconds)
    timeout_response = [False]  # Default: proceed with shutdown
    
    def on_response(response):
        timeout_response[0] = response
        root.quit()
    
    def on_timeout():
        log_message("⏰ Final dialog timeout - no user response. Proceeding with shutdown.")
        root.quit()
    
    # Create custom dialog with timeout
    dialog_frame = tk.Toplevel(root)
    dialog_frame.title("🚨 FINAL SHUTDOWN WARNING")
    dialog_frame.geometry("450x220")
    dialog_frame.protocol("WM_DELETE_WINDOW", lambda: on_response(False))  # Handle window close
    
    # Keep dialog on top
    dialog_frame.attributes('-topmost', True)
    
    # Message
    tk.Label(dialog_frame, text="🚨 FINAL WARNING 🚨", font=("Arial", 16, "bold"), fg="red").pack(pady=10)
    tk.Label(dialog_frame, text="Your PC will shut down in 10 minutes!", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Label(dialog_frame, text="(at exactly 11:00 PM)", font=("Arial", 10)).pack(pady=5)
    tk.Label(dialog_frame, text="Click 'YES' to CANCEL the shutdown.", font=("Arial", 11, "bold"), fg="green").pack(pady=8)
    tk.Label(dialog_frame, text="Click 'NO' or do nothing to proceed with shutdown.", font=("Arial", 9), fg="gray").pack(pady=5)
    
    # Buttons
    button_frame = tk.Frame(dialog_frame)
    button_frame.pack(pady=15)
    tk.Button(button_frame, text="YES (Cancel Shutdown)", width=20, 
             command=lambda: on_response(True), bg="green", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="NO (Let PC Shutdown)", width=20, 
             command=lambda: on_response(False), bg="red", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=10)
    
    # Set timeout (60 seconds)
    dialog_frame.after(60000, on_timeout)
    
    # Center dialog
    dialog_frame.update_idletasks()
    width = dialog_frame.winfo_width()
    height = dialog_frame.winfo_height()
    x = (dialog_frame.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog_frame.winfo_screenheight() // 2) - (height // 2)
    dialog_frame.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Run dialog
    root.mainloop()
    
    # Process result
    if timeout_response[0]:  # User clicked YES to cancel
        shutdown_canceled = True
        log_message("✅ SHUTDOWN CANCELED by user at final dialog (clicked YES)")
        
        # Show confirmation that shutdown was canceled
        root.destroy()
        cancel_root = tk.Tk()
        cancel_root.withdraw()
        messagebox.showinfo("Shutdown Canceled", 
                          "✅ The scheduled shutdown has been canceled!\n\nYour PC will NOT shut down at 11:00 PM today.")
        cancel_root.destroy()
        
        log_message("🛑 Script terminating - shutdown canceled by user")
        os._exit(0)  # Force exit the script
    else:
        log_message("⏭️ User clicked NO or timeout - will proceed with scheduled shutdown")
    
    second_dialog_shown = True
    root.destroy()

def execute_shutdown(delay_minutes=1):
    """Actually shuts down the PC with specified delay"""
    global shutdown_canceled
    
    # Final check if shutdown was canceled or if it's Friday
    if shutdown_canceled:
        log_message("⚠️ Shutdown was canceled, not executing shutdown command")
        return
    
    if is_friday():
        log_message("🎉 Friday detected during shutdown execution - aborting shutdown")
        return
    
    log_message(f"🔴 INITIATING SYSTEM SHUTDOWN with {delay_minutes} minute delay...")
    
    try:
        if os.name == 'nt':  # Windows
            # Enhanced shutdown with multiple methods for reliability
            delay_seconds = delay_minutes * 60
            
            # Method 1: Standard shutdown command
            result = subprocess.run([
                "shutdown", "/s", "/t", str(delay_seconds), "/f", 
                "/c", "Scheduled shutdown at 11:00 PM"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                log_message("✅ Primary shutdown command executed successfully.")
            else:
                log_message(f"⚠️ Primary shutdown failed, trying alternative: {result.stderr}")
                # Method 2: Fallback
                os.system(f"shutdown /s /t {delay_seconds} /f")
                
    except Exception as e:
        log_message(f"❌ Error during shutdown: {e}")
        try:
            # Last resort method
            os.system('wmic os where "Primary=\'True\'" call shutdown')
            log_message("🔄 Emergency shutdown method executed")
        except Exception as e2:
            log_message(f"💥 All shutdown methods failed: {e2}")
    
    log_message("⚡ Shutdown command execution completed.")
    # Exit the script after initiating shutdown
    os._exit(0)

def schedule_checker():
    """Main function that checks time and shows dialogs at appropriate times"""
    global immediate_shutdown, shutdown_canceled
    
    # Check if today is Friday - if so, skip shutdown entirely
    if is_friday():
        log_message("🎉 Today is Friday - NO SHUTDOWN scheduled! Enjoy your weekend!")
        log_message("📅 Shutdown scheduler will resume on Monday")
        return  # Exit the function, no shutdown on Friday
    
    log_message("✅ Shutdown scheduler started and running in background")
    log_message(f"📅 Today is {datetime.datetime.now().strftime('%A')} - shutdown is scheduled")
    log_message(f"🕘 Schedule: First warning at {first_dialog_time.strftime('%I:%M %p')}, "
              f"Final warning at {second_dialog_time.strftime('%I:%M %p')}, "
              f"Shutdown at {shutdown_time.strftime('%I:%M %p')}")
    
    # Check if PC was restarted to evade shutdown
    if check_restart_evasion():
        immediate_shutdown = show_restart_evasion_dialog()
        
        if immediate_shutdown:
            # If we need immediate shutdown (restart evasion detected)
            execute_shutdown(delay_minutes=2)  # 2-minute warning for restart evasion
            return
    
    while not shutdown_canceled:
        now = datetime.datetime.now().time()
        
        # Double-check it's not Friday (in case day changed during execution)
        if is_friday():
            log_message("🎉 Day changed to Friday - canceling shutdown")
            shutdown_canceled = True
            break
        
        # If we're already past shutdown time with no first dialog shown, handle special case
        if now >= shutdown_time and not first_dialog_shown:
            log_message("⚠️ Current time is already past shutdown time with no prior dialogs shown.")
            # In this case, we assume it's a restart evasion if we didn't already check
            if not immediate_shutdown:
                immediate_shutdown = show_restart_evasion_dialog()
                
                if immediate_shutdown:
                    execute_shutdown(delay_minutes=2)  # 2-minute warning for restart evasion
                    break
            else:
                # We already decided to shut down
                execute_shutdown(delay_minutes=2)
                break
        
        # Check if it's time to show first dialog (9:30 PM - 11:00 PM)
        if first_dialog_time <= now < shutdown_time and not first_dialog_shown and not shutdown_canceled:
            log_message("🔔 Showing first confirmation dialog...")
            show_first_dialog()
        
        # Check if it's time to show second dialog (10:50 PM)
        if (second_dialog_time <= now < shutdown_time and 
            not second_dialog_shown and first_dialog_shown and not shutdown_canceled):
            log_message("⚠️ Showing second (final) confirmation dialog...")
            show_second_dialog()
        
        # Check if it's shutdown time
        if now >= shutdown_time and first_dialog_shown and not shutdown_canceled:
            log_message("⏰ Shutdown time reached - executing shutdown")
            execute_shutdown()
            break
        
        # Check time every minute for better responsiveness
        time.sleep(60)

def hide_console_window():
    """Hide the console window on Windows"""
    if os.name == 'nt':
        try:
            import win32gui
            import win32con
            hwnd = win32gui.GetConsoleWindow()
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                log_message("🫥 Console window hidden")
        except:
            # Alternative method if win32gui is not available
            pass

def run_in_background():
    """Run the script in background mode (platform-specific)"""
    if os.name == 'nt':  # Windows
        if not windows_available:
            # If win32gui is not available, use the alternative method
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen([sys.executable, __file__, "--background"], 
                            startupinfo=startupinfo, 
                            creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            # Use win32gui method
            hide_console_window()
    else:  # Linux/macOS
        # Redirect output to log file
        os.system(f"nohup {sys.executable} {__file__} --background > shutdown_scheduler.log 2>&1 &")
    
    # Exit the current instance
    sys.exit(0)

if __name__ == "__main__":
    try:
        # First check if it's Friday - exit early if so
        if is_friday():
            log_message("🎉 TODAY IS FRIDAY - Shutdown scheduler disabled for the weekend!")
            log_message("📅 The scheduler will resume automatically on Monday")
            print("🎉 It's Friday! No shutdown scheduled today. Enjoy your weekend!")
            sys.exit(0)
        
        # Check if the script should run in background mode
        if "--background" not in sys.argv:
            # Check for administrator privileges on Windows
            if os.name == 'nt':
                if not is_admin():
                    log_message("🔐 Script needs administrator privileges for reliable shutdown")
                    if not run_as_admin():
                        log_message("❌ Failed to get administrator privileges, continuing anyway")
                    else:
                        sys.exit(0)  # Exit this instance, the elevated one will run
            
            # If not run with --background flag, restart in background mode
            run_in_background()
        else:
            # Hide console window
            if os.name == 'nt' and windows_available:
                hide_console_window()
            
            # Run scheduler in hidden mode
            # Log startup information
            log_startup_info()
            log_message("🚀 Enhanced Shutdown Scheduler started with restart evasion detection")
            log_message(f"👑 Running with admin privileges: {is_admin()}")
            log_message(f"📅 Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
            
            # Run the scheduler
            schedule_checker()
            
    except KeyboardInterrupt:
        log_message("🛑 Shutdown scheduler stopped by user")
    except Exception as e:
    log_message(f"💥 Critical error in shutdown scheduler: {e}")
    try:
        with open(os.path.join(SCRIPT_DIR, "shutdown_error.log"), "a") as f:
            f.write(f"{datetime.datetime.now()}: Critical error: {str(e)}\n")
    except:
        pass