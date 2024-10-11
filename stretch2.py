import tkinter as tk
from datetime import datetime
import threading
import time
import os

DEFAULT_COUNTDOWN_TIME = 0.1 * 60  # 20 minutes
LOG_FILE = os.path.join(os.path.dirname(__file__), "stretch_log.txt")


class StretchReminder:
    def __init__(self):
        self.log = self.load_log()
        self.countdown = DEFAULT_COUNTDOWN_TIME
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.timer_thread = None
        self.stop_event = threading.Event()
        self.current_dialog = None

    def load_log(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as file:
                return file.read().splitlines()
        return []

    def save_log(self):
        with open(LOG_FILE, "w") as file:
            for entry in self.log:
                file.write(f"{entry}\n")

    def show_popup(self):
        if self.current_dialog:
            self.current_dialog.destroy()

        self.root.bell()  # Ring the bell
        self.current_dialog = tk.Toplevel(self.root)
        self.current_dialog.title("Time to Stretch!")
        self.current_dialog.geometry("250x350")

        message = tk.Label(self.current_dialog, text="It's time to stand and stretch!", font=("Helvetica", 14))
        message.pack(pady=10)

        history_label = tk.Label(self.current_dialog, text="Stretch History:")
        history_label.pack()

        history_frame = tk.Frame(self.current_dialog)
        history_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        history_scrollbar = tk.Scrollbar(history_frame)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        history_listbox = tk.Listbox(history_frame, width=50, height=10, yscrollcommand=history_scrollbar.set)
        history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        history_scrollbar.config(command=history_listbox.yview)

        for entry in self.log:
            history_listbox.insert(tk.END, entry)

        time_options = [5, 10, 15, 20, 30, 60]  # Minutes
        self.time_var = tk.IntVar(value=int(self.countdown / 60))
        time_dropdown = tk.OptionMenu(self.current_dialog, self.time_var, *time_options)
        time_dropdown.pack(pady=10)

        ok_button = tk.Button(self.current_dialog, text="OK", command=self.dismiss_popup)
        ok_button.pack(pady=10)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.append(now)
        self.save_log()

        self.current_dialog.protocol("WM_DELETE_WINDOW", self.dismiss_popup)
        self.current_dialog.lift()  # Bring window to front
        self.current_dialog.attributes("-topmost", True)  # Keep on top
        self.current_dialog.after_idle(self.current_dialog.attributes, "-topmost", False)

    def dismiss_popup(self):
        if self.current_dialog:
            self.current_dialog.destroy()
            self.current_dialog = None
        self.countdown = self.time_var.get() * 60  # Reset the countdown with the selected time

    def timer_loop(self):
        while not self.stop_event.is_set():
            time.sleep(1)  # Check every second
            self.countdown -= 1
            if self.countdown <= 0 and not self.stop_event.is_set():
                if not self.current_dialog:
                    self.root.after(0, self.show_popup)
                    while not self.stop_event.is_set() and self.current_dialog:
                        time.sleep(0.1)  # Wait for popup to be dismissed

    def run(self):
        self.timer_thread = threading.Thread(target=self.timer_loop)
        self.timer_thread.start()
        self.root.mainloop()

    def stop(self):
        self.stop_event.set()
        if self.current_dialog:
            self.root.after(0, self.current_dialog.destroy)
        if self.timer_thread:
            self.timer_thread.join()
        self.root.quit()


if __name__ == "__main__":
    reminder = StretchReminder()
    try:
        reminder.run()
    except KeyboardInterrupt:
        print("Stopping the reminder...")
        reminder.stop()
