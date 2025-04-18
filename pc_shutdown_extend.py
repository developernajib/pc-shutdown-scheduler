import tkinter as tk
from tkinter import messagebox
import datetime
import time
import threading
import os
import sys
import subprocess

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

# Status tracking
first_dialog_shown = False
second_dialog_shown = False
immediate_shutdown = False

# Log startup information to file rather than console
def log_startup_info():
    with open("shutdown_scheduler.log", "a") as f:
        f.write(f"Shutdown Scheduler: Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def log_message(message):
    """Log a message to file instead of printing to console"""
    try:
        with open("shutdown_scheduler.log", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp}: {message}\n")
    except:
        pass  # Silent fail if logging isn't possible

def check_restart_evasion():
    """
    Check if the PC has been restarted to evade shutdown.
    Returns True if we need to shut down immediately.
    """
    now = datetime.datetime.now()
    current_date = now.date()
    current_time = now.time()
    
    # If it's already past shutdown time on the same day, immediate shutdown is needed
    if current_time >= shutdown_time:
        log_message("⚠️ Detected script start after shutdown time - possible restart evasion")
        
        # Create immediate confirmation dialog with shorter timeout
        return True
        
    return False

def show_restart_evasion_dialog():
    """Shows a special dialog when restart evasion is detected"""
    root = tk.Tk()
    root.withdraw()
    
    # Set a timeout for the dialog (30 seconds - shorter for evasion attempts)
    timeout_response = [False]  # Default: proceed with shutdown
    
    def on_response(response):
        timeout_response[0] = response
        root.quit()
    
    def on_timeout():
        log_message("⏰ Dialog timeout - no user response. Proceeding with immediate shutdown.")
        root.quit()
    
    # Create custom dialog with timeout
    dialog_frame = tk.Toplevel(root)
    dialog_frame.title("⚠️ Emergency Shutdown Warning")
    dialog_frame.geometry("450x180")
    dialog_frame.protocol("WM_DELETE_WINDOW", lambda: on_response(False))  # Handle window close
    
    # Keep dialog on top with higher priority
    dialog_frame.attributes('-topmost', True)
    
    # Message
    tk.Label(dialog_frame, text="System policy violation detected!", pady=10, font=("Arial", 12, "bold")).pack()
    tk.Label(dialog_frame, text="Your PC should have been shut down.", pady=5).pack()
    tk.Label(dialog_frame, text="The system will shut down in 2 minutes unless canceled.", pady=5).pack()
    
    # Buttons
    button_frame = tk.Frame(dialog_frame)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Override (Admin Only)", width=20, command=lambda: on_response(True)).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Shut Down Now", width=15, command=lambda: on_response(False)).pack(side=tk.RIGHT, padx=10)
    
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
        log_message("✅ Shutdown override by admin after restart evasion.")
        
        # Ask for admin password (this is just a deterrent, not real security)
        admin_root = tk.Tk()
        admin_root.withdraw()
        admin_check = messagebox.askstring("Admin Verification", 
                                         "Enter admin password to override shutdown:",
                                         show='*')
        admin_root.destroy()
        
        # Simple check - in a real app, you'd use proper authentication
        if admin_check == "admin123":  # Replace with a better method in production
            log_message("✓ Admin override accepted.")
            return False  # Don't shut down
        else:
            log_message("✗ Invalid admin override attempt.")
            messagebox.showinfo("Access Denied", "Invalid credentials. Shutdown will proceed.")
            return True  # Shut down
    else:
        log_message("❌ Immediate shutdown will proceed after restart evasion.")
        return True  # Shut down

def show_first_dialog():
    """Shows the first confirmation dialog (9:30 PM - 11:00 PM)"""
    global first_dialog_shown
    
    root = tk.Tk()
    root.withdraw()
    
    # Keep the dialog on top
    root.attributes('-topmost', True)
    
    response = messagebox.askyesno(
        "Shutdown Confirmation",
        "Your PC is scheduled to shut down at 11:00 PM.\n\nDo you want to cancel the shutdown?",
        icon="warning"
    )
    
    if response:
        log_message("✅ Shutdown canceled by user at first dialog.")
        messagebox.showinfo("Shutdown Canceled", "The scheduled shutdown has been canceled.")
        # Terminate the script
        root.destroy()
        os._exit(0)  # Force exit the script
    else:
        log_message("❌ User confirmed shutdown will proceed (will show second dialog at 10:50 PM)")
    
    first_dialog_shown = True
    root.destroy()

def show_second_dialog():
    """Shows the final confirmation dialog (10:50 PM)"""
    global second_dialog_shown
    
    root = tk.Tk()
    root.withdraw()
    
    # Set a timeout for the dialog (60 seconds)
    timeout_response = [False]  # Default: proceed with shutdown
    
    def on_response(response):
        timeout_response[0] = response
        root.quit()
    
    def on_timeout():
        log_message("⏰ Dialog timeout - no user response. Proceeding with shutdown.")
        root.quit()
    
    # Create custom dialog with timeout
    dialog_frame = tk.Toplevel(root)
    dialog_frame.title("Final Shutdown Warning")
    dialog_frame.geometry("400x150")
    dialog_frame.protocol("WM_DELETE_WINDOW", lambda: on_response(False))  # Handle window close
    
    # Keep dialog on top
    dialog_frame.attributes('-topmost', True)
    
    # Message
    tk.Label(dialog_frame, text="Your PC will shut down in 10 minutes.", pady=10, font=("Arial", 12)).pack()
    tk.Label(dialog_frame, text="Click YES to cancel the shutdown or NO to proceed.", pady=5).pack()
    
    # Buttons
    button_frame = tk.Frame(dialog_frame)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Yes (Cancel)", width=15, command=lambda: on_response(True)).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="No (Proceed)", width=15, command=lambda: on_response(False)).pack(side=tk.RIGHT, padx=10)
    
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
    if timeout_response[0]:
        log_message("✅ Shutdown canceled by user at second dialog.")
        
        # Show confirmation that shutdown was canceled
        cancel_root = tk.Tk()
        cancel_root.withdraw()
        messagebox.showinfo("Shutdown Canceled", "The scheduled shutdown has been canceled.")
        cancel_root.destroy()
        
        # Terminate the script
        root.destroy()
        os._exit(0)  # Force exit the script
    else:
        log_message("❌ User confirmed shutdown will proceed (or didn't respond).")
    
    second_dialog_shown = True
    root.destroy()

def execute_shutdown(delay_minutes=1):
    """Actually shuts down the PC with specified delay"""
    log_message(f"🔴 INITIATING SYSTEM SHUTDOWN with {delay_minutes} minute delay...")
    
    try:
        if os.name == 'nt':  # Windows
            # Force shutdown with specified delay
            delay_seconds = delay_minutes * 60
            os.system(f"shutdown /s /t {delay_seconds} /f /c \"Scheduled shutdown at 11:00 PM\"")
        else:  # Linux/macOS
            os.system(f"shutdown -h +{delay_minutes} \"Scheduled shutdown at 11:00 PM\"")
            
        log_message("⚡ Shutdown command executed successfully.")
    except Exception as e:
        log_message(f"⚠️ Error during shutdown: {e}")
    
    # Exit the script after initiating shutdown
    os._exit(0)

def schedule_checker():
    """Main function that checks time and shows dialogs at appropriate times"""
    global immediate_shutdown
    
    log_message("🕒 Shutdown Scheduler is running in hidden mode...")
    
    # Check if PC was restarted to evade shutdown
    if check_restart_evasion():
        immediate_shutdown = show_restart_evasion_dialog()
        
        if immediate_shutdown:
            # If we need immediate shutdown (restart evasion detected)
            execute_shutdown(delay_minutes=2)  # 2-minute warning for restart evasion
            return
    
    while True:
        now = datetime.datetime.now().time()
        
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
        if first_dialog_time <= now < shutdown_time and not first_dialog_shown:
            log_message("🔔 Showing first confirmation dialog...")
            show_first_dialog()
        
        # Check if it's time to show second dialog (10:50 PM)
        if second_dialog_time <= now < shutdown_time and not second_dialog_shown and first_dialog_shown:
            log_message("⚠️ Showing second (final) confirmation dialog...")
            show_second_dialog()
        
        # Check if it's shutdown time
        if now >= shutdown_time and first_dialog_shown:
            log_message("⏰ Shutdown time reached.")
            execute_shutdown()
            break
        
        # Check time every 5 minutes
        time.sleep(300)

def hide_console_window():
    """Hide the console window on Windows"""
    if os.name == 'nt' and windows_available:
        # Get the console window handle
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            return True
    return False

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
    # Check if the script should run in background mode
    if "--background" not in sys.argv:
        # If not run with --background flag, restart in background mode
        run_in_background()
    else:
        # Hide console window
        if os.name == 'nt' and windows_available:
            hide_console_window()
        
        # Run scheduler in hidden mode
        try:
            # Log startup information
            log_startup_info()
            
            # Run the scheduler
            schedule_checker()
        except Exception as e:
            # Log error to file
            try:
                with open("shutdown_error.log", "a") as f:
                    f.write(f"{datetime.datetime.now()}: {str(e)}\n")
            except:
                pass