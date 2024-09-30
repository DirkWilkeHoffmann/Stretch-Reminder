import tkinter as tk
from datetime import datetime
import threading
import time

COUNTDOWN_TIME = 20 * 60  # 20 minutes


class StretchReminder:
    def __init__(self):
        self.log = []
        self.countdown = COUNTDOWN_TIME
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        self.timer_thread = None
        self.stop_event = threading.Event()
        self.current_dialog = None

    def show_popup(self):
        if self.current_dialog:
            self.current_dialog.destroy()

        self.root.bell()  # Ring the bell
        self.current_dialog = tk.Toplevel(self.root)
        self.current_dialog.title("Time to Stretch!")
        self.current_dialog.geometry("250x300")

        message = tk.Label(self.current_dialog, text="It's time to stand and stretch!", font=("Helvetica", 14))
        message.pack(pady=10)

        history_label = tk.Label(self.current_dialog, text="Stretch History:")
        history_label.pack()

        history_listbox = tk.Listbox(self.current_dialog, width=50, height=10)
        history_listbox.pack(pady=5)

        for entry in self.log:
            history_listbox.insert(tk.END, entry)

        ok_button = tk.Button(self.current_dialog, text="OK", command=self.dismiss_popup)
        ok_button.pack(pady=10)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.append(now)

        self.current_dialog.protocol("WM_DELETE_WINDOW", self.dismiss_popup)
        self.current_dialog.lift()  # Bring window to front
        self.current_dialog.attributes("-topmost", True)  # Keep on top
        self.current_dialog.after_idle(self.current_dialog.attributes, "-topmost", False)

    def dismiss_popup(self):
        if self.current_dialog:
            self.current_dialog.destroy()
            self.current_dialog = None
        self.countdown = COUNTDOWN_TIME  # Reset the countdown

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
