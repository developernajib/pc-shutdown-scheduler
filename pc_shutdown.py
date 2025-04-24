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
first_dialog_root = None  # Reference to first dialog for closing
shutdown_canceled = False  # Track if shutdown is canceled

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
    except Exception as e:
        # Write to error log if main log fails
        try:
            with open("shutdown_error.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: Failed to write to main log: {str(e)}\n")
        except:
            pass  # Silent fail if all logging isn't possible

def show_first_dialog():
    """Shows the first confirmation dialog (9:30 PM - 10:50 PM)"""
    global first_dialog_shown, first_dialog_root, shutdown_canceled
    
    log_message("🔔 Displaying first shutdown warning dialog")
    
    first_dialog_root = tk.Tk()
    first_dialog_root.withdraw()
    
    # Keep the dialog on top
    first_dialog_root.attributes('-topmost', True)
    
    # Handle dialog close without interaction
    def on_dialog_close():
        global first_dialog_shown
        log_message("ℹ️ First dialog closed without interaction (proceeding with shutdown)")
        first_dialog_shown = True
        first_dialog_root.destroy()
    
    response = messagebox.askyesno(
        "Shutdown Confirmation",
        "Your PC is scheduled to shut down at 11:00 PM.\n\nDo you want to cancel the shutdown?",
        icon="warning"
    )
    
    if response:
        log_message("✅ Shutdown canceled by user at first dialog.")
        shutdown_canceled = True
        messagebox.showinfo("Shutdown Canceled", "The scheduled shutdown has been canceled.")
        # Terminate the script
        first_dialog_root.destroy()
        os._exit(0)  # Force exit the script
    else:
        # Log the fact that user clicked "No" or closed the dialog
        log_message("⏳ User clicked 'No' or closed first dialog (proceeding with shutdown)")
        # Don't destroy the dialog yet, we'll do it before showing the second dialog
        # Just mark that we've shown it
        first_dialog_shown = True

def close_first_dialog():
    """Close the first dialog if it's still open"""
    global first_dialog_root
    
    if first_dialog_root is not None:
        try:
            first_dialog_root.destroy()
            first_dialog_root = None
            log_message("ℹ️ First dialog automatically closed before showing second dialog")
        except:
            pass  # Dialog might have been closed already

def show_second_dialog():
    """Shows the final confirmation dialog (10:50 PM until shutdown)"""
    global second_dialog_shown, shutdown_canceled
    
    # First make sure the first dialog is closed
    close_first_dialog()
    
    log_message("🔔 Displaying final shutdown warning dialog (10 minutes remaining)")
    
    root = tk.Tk()
    root.withdraw()
    
    # Set response tracking
    dialog_result = [False]  # Default: proceed with shutdown
    
    def on_response(response):
        dialog_result[0] = response
        # Don't close the dialog, just set the result
        if response:
            # Only quit if YES was clicked (user wants to cancel)
            root.quit()
    
    # Create custom dialog
    dialog_frame = tk.Toplevel(root)
    dialog_frame.title("Final Shutdown Warning")
    dialog_frame.geometry("400x150")
    
    # Handle dialog close without interaction - in this case proceed with shutdown
    def on_dialog_close():
        log_message("ℹ️ Final dialog closed without interaction (proceeding with shutdown)")
        # We don't need to do anything special here since the default is to proceed
        dialog_frame.destroy()
    
    # Override the close button to log the event
    dialog_frame.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    # Keep dialog on top
    dialog_frame.attributes('-topmost', True)
    
    # Message
    tk.Label(dialog_frame, text="Your PC will shut down in 10 minutes.", pady=10, font=("Arial", 12)).pack()
    tk.Label(dialog_frame, text="Click YES to cancel the shutdown.", pady=5).pack()
    
    # Buttons - only YES button now
    button_frame = tk.Frame(dialog_frame)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Yes (Cancel Shutdown)", width=20, command=lambda: on_response(True)).pack()
    
    # Center dialog
    dialog_frame.update_idletasks()
    width = dialog_frame.winfo_width()
    height = dialog_frame.winfo_height()
    x = (dialog_frame.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog_frame.winfo_screenheight() // 2) - (height // 2)
    dialog_frame.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Mark dialog as shown
    second_dialog_shown = True
    
    # Start a thread to wait for shutdown time
    shutdown_thread = threading.Thread(target=wait_for_shutdown, args=(root, dialog_result))
    shutdown_thread.daemon = True
    shutdown_thread.start()
    
    # Run dialog
    root.mainloop()
    
    # Process result - this only happens if user clicked "Yes"
    if dialog_result[0]:
        log_message("✅ Shutdown canceled by user at second dialog.")
        shutdown_canceled = True
        
        # Show confirmation that shutdown was canceled
        cancel_root = tk.Tk()
        cancel_root.withdraw()
        messagebox.showinfo("Shutdown Canceled", "The scheduled shutdown has been canceled.")
        cancel_root.destroy()
        
        # Terminate the script
        os._exit(0)  # Force exit the script

def wait_for_shutdown(root, dialog_result):
    """Wait until shutdown time then execute shutdown"""
    log_message("⏰ Countdown to shutdown started")
    
    # Calculate time until shutdown for logging
    now = datetime.datetime.now()
    shutdown_dt = datetime.datetime.combine(now.date(), shutdown_time)
    if shutdown_dt < now:
        shutdown_dt = shutdown_dt + datetime.timedelta(days=1)
    
    minutes_to_shutdown = (shutdown_dt - now).total_seconds() / 60
    log_message(f"⏱️ Approximately {int(minutes_to_shutdown)} minutes until shutdown")
    
    while datetime.datetime.now().time() < shutdown_time:
        time.sleep(1)
        
        # If the dialog result was set to True (canceled), exit
        if dialog_result[0]:
            return
    
    # Shutdown time reached - log it
    log_message("🕒 Shutdown time reached, initiating shutdown")
    
    # Close the dialog
    try:
        root.destroy()
    except:
        pass
    
    # Execute shutdown
    execute_shutdown()

def execute_shutdown():
    """Actually shuts down the PC"""
    global shutdown_canceled
    
    # Double-check shutdown wasn't canceled
    if shutdown_canceled:
        log_message("⚠️ Shutdown already canceled, not executing shutdown command")
        return
    
    try:
        # Log right before shutdown
        log_message("🔴 PC SHUTDOWN INITIATED at scheduled time (11:00 PM)")
        log_message("💻 No user interaction detected to cancel the shutdown")
        
        # Execute shutdown command
        if os.name == 'nt':  # Windows
            os.system("shutdown /s /t 0 /f")
        else:  # Linux/macOS
            os.system("shutdown -h now")
            
    except Exception as e:
        log_message(f"⚠️ Error during shutdown: {e}")
    
    # Exit the script after initiating shutdown
    os._exit(0)

def schedule_checker():
    """Main function that checks time and shows dialogs at appropriate times"""
    log_message("✅ Shutdown scheduler started and running in background")
    log_message(f"📅 Schedule: First warning at {first_dialog_time.strftime('%I:%M %p')}, " 
              f"Final warning at {second_dialog_time.strftime('%I:%M %p')}, "
              f"Shutdown at {shutdown_time.strftime('%I:%M %p')}")
    
    while True:
        now = datetime.datetime.now().time()
        
        # Check if it's time to show first dialog (9:30 PM - 10:50 PM)
        if first_dialog_time <= now < second_dialog_time and not first_dialog_shown:
            show_first_dialog()
        
        # Check if it's time to show second dialog (10:50 PM until shutdown)
        if second_dialog_time <= now < shutdown_time and not second_dialog_shown:
            show_second_dialog()
            # Once second dialog is shown, the wait_for_shutdown thread will handle the rest
            break
        
        # Check if we somehow missed showing the second dialog and it's shutdown time
        if now >= shutdown_time and not second_dialog_shown:
            log_message("🕒 Shutdown time reached without showing second dialog")
            execute_shutdown()
            break
        
        # Check time every minute (more responsive than 5 minutes)
        time.sleep(60)

def hide_console_window():
    """Hide the console window on Windows"""
    if os.name == 'nt' and windows_available:
        # Get the console window handle
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            log_message("🔍 Console window hidden")
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