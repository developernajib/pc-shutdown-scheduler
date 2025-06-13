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

def is_friday():
    """Check if today is Friday (weekday 4)"""
    return datetime.datetime.now().weekday() == 4

# Status tracking
first_dialog_shown = False
second_dialog_shown = False
shutdown_canceled = False
shutdown_timer_started = False

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
        log_message("🔑 Requesting administrator privileges for reliable shutdown")
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            return False
        except:
            log_message("⚠ Failed to get administrator privileges")
            return False

def force_shutdown():
    """Force shutdown the PC using multiple methods"""
    global shutdown_canceled
    
    if shutdown_canceled:
        log_message("❌ Shutdown was canceled, not executing")
        return
    
    log_message("🔴 INITIATING FORCED SHUTDOWN at 11:00 PM")
    
    try:
        # Method 1: Use subprocess with shell=False for better reliability
        log_message("💻 Attempting shutdown via subprocess...")
        result = subprocess.run([
            "shutdown", "/s", "/t", "5", "/f", "/c", "Scheduled shutdown at 11:00 PM"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            log_message("✅ Shutdown command executed successfully")
        else:
            log_message(f"⚠️ Shutdown command returned code {result.returncode}: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        log_message("⏱ Shutdown command timed out, trying alternative method")
        try:
            # Method 2: Direct system call
            os.system("shutdown /s /t 5 /f")
            log_message("🔄 Alternative shutdown method executed")
        except Exception as e:
            log_message(f"❌ Alternative shutdown failed: {e}")
            
    except Exception as e:
        log_message(f"❌ Primary shutdown method failed: {e}")
        try:
            # Method 3: Using wmic as last resort
            os.system('wmic os where "Primary=\'True\'" call shutdown')
            log_message("🔧 WMIC shutdown method executed")
        except Exception as e2:
            log_message(f"💥 All shutdown methods failed: {e2}")

def start_shutdown_timer():
    """Start the absolute shutdown timer that will execute regardless of dialogs"""
    global shutdown_timer_started
    
    if shutdown_timer_started:
        return
    
    # Don't start timer on Friday
    if is_friday():
        log_message("🎉 Friday detected - shutdown timer NOT started")
        return
    
    shutdown_timer_started = True
    log_message("⏰ Starting absolute shutdown timer")
    
    def shutdown_timer():
        # Calculate exact time until shutdown
        now = datetime.datetime.now()
        shutdown_dt = datetime.datetime.combine(now.date(), shutdown_time)
        
        # If shutdown time has passed today, schedule for tomorrow
        if shutdown_dt <= now:
            shutdown_dt += datetime.timedelta(days=1)
        
        wait_seconds = (shutdown_dt - now).total_seconds()
        log_message(f"⏳ Shutdown timer set for {wait_seconds:.0f} seconds ({shutdown_dt.strftime('%H:%M:%S')})")
        
        # Wait until shutdown time, checking every minute for cancellation
        while datetime.datetime.now() < shutdown_dt:
            if shutdown_canceled:
                log_message("🛑 Shutdown timer stopped - user canceled shutdown")
                return
            
            # Check if it became Friday during the wait
            if is_friday():
                log_message("🎉 Friday detected during timer - canceling shutdown")
                return
            
            time.sleep(60)  # Check every minute
        
        # Execute shutdown if not canceled and not Friday
        if not shutdown_canceled and not is_friday():
            log_message("💥 SHUTDOWN TIME REACHED - Executing shutdown (no user interaction detected)")
            force_shutdown()
        else:
            if shutdown_canceled:
                log_message("✅ Shutdown timer expired but shutdown was canceled by user")
            if is_friday():
                log_message("🎉 Shutdown timer expired but it's Friday - no shutdown")
    
    # Start the timer in a separate daemon thread
    timer_thread = threading.Thread(target=shutdown_timer, daemon=True)
    timer_thread.start()

def show_first_dialog():
    """Shows the first confirmation dialog (9:30 PM - 10:50 PM)"""
    global first_dialog_shown, shutdown_canceled
    
    if first_dialog_shown or shutdown_canceled:
        return
    
    first_dialog_shown = True
    log_message("💬 Displaying first shutdown warning dialog")
    
    def dialog_thread():
        try:
            root = tk.Tk()
            root.withdraw()
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
                
                # Show confirmation in a new window
                confirm_root = tk.Tk()
                confirm_root.withdraw()
                messagebox.showinfo("Shutdown Canceled", 
                                  "✅ The scheduled shutdown has been canceled!\n\nYour PC will NOT shut down at 11:00 PM today.")
                confirm_root.destroy()
                
                log_message("🚪 Script terminating - shutdown canceled by user")
                os._exit(0)  # Completely exit the program
            else:
                log_message("➡️ User clicked NO - will proceed with scheduled shutdown")
            
            root.destroy()
            
        except Exception as e:
            log_message(f"❌ Error in first dialog: {e}")
    
    # Run dialog in separate thread to avoid blocking
    threading.Thread(target=dialog_thread, daemon=True).start()

def show_second_dialog():
    """Shows the final confirmation dialog (10:50 PM until shutdown)"""
    global second_dialog_shown, shutdown_canceled
    
    if second_dialog_shown or shutdown_canceled:
        return
    
    second_dialog_shown = True
    log_message("🚨 Displaying final shutdown warning dialog (10 minutes remaining)")
    
    def dialog_thread():
        try:
            root = tk.Tk()
            root.withdraw()
            
            # Create the dialog with a timeout
            dialog = tk.Toplevel(root)
            dialog.title("🚨 FINAL SHUTDOWN WARNING")
            dialog.geometry("450x250")
            dialog.attributes('-topmost', True)
            
            # Center the dialog
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            tk.Label(dialog, text="🚨 FINAL WARNING 🚨", font=("Arial", 16, "bold"), fg="red").pack(pady=15)
            tk.Label(dialog, text="Your PC will shut down in 10 minutes!", font=("Arial", 12, "bold")).pack(pady=5)
            tk.Label(dialog, text="(at exactly 11:00 PM)", font=("Arial", 10)).pack(pady=5)
            tk.Label(dialog, text="Click 'YES - Cancel Shutdown' to prevent shutdown.", font=("Arial", 11)).pack(pady=10)
            tk.Label(dialog, text="If you do nothing, PC will shutdown automatically.", font=("Arial", 9), fg="gray").pack(pady=5)
            
            def cancel_shutdown():
                global shutdown_canceled
                shutdown_canceled = True
                log_message("✅ SHUTDOWN CANCELED by user at final dialog (clicked YES)")
                dialog.destroy()
                root.destroy()
                
                # Show confirmation in a new window
                confirm_root = tk.Tk()
                confirm_root.withdraw()
                messagebox.showinfo("Shutdown Canceled", 
                                  "✅ The scheduled shutdown has been canceled!\n\nYour PC will NOT shut down at 11:00 PM today.")
                confirm_root.destroy()
                
                log_message("🚪 Script terminating - shutdown canceled by user")
                os._exit(0)  # Completely exit the program
            
            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=20)
            
            tk.Button(button_frame, text="YES - Cancel Shutdown", command=cancel_shutdown, 
                     bg="green", fg="white", font=("Arial", 12, "bold"), width=20).pack(pady=5)
            tk.Button(button_frame, text="NO - Let PC Shutdown", command=lambda: [dialog.destroy(), root.destroy()], 
                     bg="red", fg="white", font=("Arial", 10), width=20).pack(pady=5)
            
            # Auto-close dialog after 8 minutes (2 minutes before shutdown)
            def auto_close():
                time.sleep(480)  # 8 minutes
                try:
                    if not shutdown_canceled:
                        log_message("⏰ Final dialog auto-closed - proceeding with shutdown")
                        dialog.destroy()
                        root.destroy()
                except:
                    pass
            
            threading.Thread(target=auto_close, daemon=True).start()
            
            # Handle manual close (X button) - treat as "let it shutdown"
            def on_close():
                log_message("➡️ Final dialog closed manually (X button) - proceeding with shutdown")
                dialog.destroy()
                root.destroy()
            
            dialog.protocol("WM_DELETE_WINDOW", on_close)
            
            root.mainloop()
            
        except Exception as e:
            log_message(f"❌ Error in final dialog: {e}")
    
    # Run dialog in separate thread
    threading.Thread(target=dialog_thread, daemon=True).start()

def schedule_checker():
    """Main function that checks time and shows dialogs at appropriate times"""
    global shutdown_canceled  # Move global declaration to the top
    
    # Check if today is Friday - if so, skip shutdown entirely
    if is_friday():
        log_message("🎉 Today is Friday - NO SHUTDOWN scheduled! Enjoy your weekend!")
        log_message("📅 Shutdown scheduler will resume on Monday")
        return  # Exit the function, no shutdown on Friday
    
    log_message("🚀 Shutdown scheduler started and running in background")
    log_message(f"📅 Today is {datetime.datetime.now().strftime('%A')} - shutdown is scheduled")
    log_message(f"⭐ Schedule: First warning at {first_dialog_time.strftime('%I:%M %p')}, "
              f"Final warning at {second_dialog_time.strftime('%I:%M %p')}, "
              f"Shutdown at {shutdown_time.strftime('%I:%M %p')}")
    
    # Start the absolute shutdown timer immediately
    start_shutdown_timer()
    
    while not shutdown_canceled:
        now = datetime.datetime.now().time()
        
        # Double-check it's not Friday (in case day changed during execution)
        if is_friday():
            log_message("🎉 Day changed to Friday - canceling shutdown")
            shutdown_canceled = True
            break
        
        # Check if it's time to show first dialog
        if (first_dialog_time <= now < second_dialog_time and 
            not first_dialog_shown and not shutdown_canceled):
            show_first_dialog()
        
        # Check if it's time to show second dialog
        if (second_dialog_time <= now < shutdown_time and 
            not second_dialog_shown and not shutdown_canceled):
            show_second_dialog()
        
        # If we've passed shutdown time, the timer thread will handle it
        if now >= shutdown_time:
            log_message("⏰ Shutdown time passed - timer thread handling shutdown")
            break
        
        # Check every 30 seconds for responsiveness
        time.sleep(30)

def hide_console_window():
    """Hide the console window on Windows"""
    if os.name == 'nt':
        try:
            import win32gui
            import win32con
            hwnd = win32gui.GetConsoleWindow()
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                log_message("👁️ Console window hidden")
        except:
            # Alternative method if win32gui is not available
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

if __name__ == "__main__":
    try:
        # First check if it's Friday - exit early if so
        if is_friday():
            log_message("🎉 TODAY IS FRIDAY - Shutdown scheduler disabled for the weekend!")
            log_message("📅 The scheduler will resume automatically on Monday")
            print("🎉 It's Friday! No shutdown scheduled today. Enjoy your weekend!")
            sys.exit(0)
        
        # Check for administrator privileges on Windows
        if os.name == 'nt':
            if not is_admin():
                log_message("🔑 Script needs administrator privileges for reliable shutdown")
                if not run_as_admin():
                    log_message("⚠ Failed to get administrator privileges, continuing anyway")
                else:
                    sys.exit(0)  # Exit this instance, the elevated one will run
        
        # Hide console window
        hide_console_window()
        
        # Log startup
        log_message("🚀 Shutdown Scheduler started with enhanced reliability")
        log_message(f"🔐 Running with admin privileges: {is_admin()}")
        log_message(f"📅 Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
        
        # Run the scheduler
        schedule_checker()
        
    except KeyboardInterrupt:
        log_message("🛑 Shutdown scheduler stopped by user")
    except Exception as e:
        log_message(f"💥 Critical error in shutdown scheduler: {e}")
        try:
            with open("shutdown_error.log", "a") as f:
                f.write(f"{datetime.datetime.now()}: Critical error: {str(e)}\n")
        except:
            pass