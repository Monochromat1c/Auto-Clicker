"""
Mouse and Keyboard Automation Tool - GUI Version
Records mouse and keyboard actions and replays them a specified number of times.
"""

import json
import os
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pynput.keyboard import Key, Listener as KeyboardListener
from automation import ActionRecorder, ActionReplayer, get_numbered_filename, save_actions, load_actions


class AutomationGUI:
    """GUI for the automation tool."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse and Keyboard Automation Tool")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # State variables
        self.recorder = None
        self.replayer = None
        self.recording_thread = None
        self.replaying_thread = None
        self.is_recording = False
        self.is_replaying = False
        self._hotkey_shift_pressed = False
        self._hotkey_alt_pressed = False
        self.hotkey_listener = None
        
        # Create GUI elements
        self.create_widgets()
        
        # Start global hotkey listener for Shift+F8 and Shift+F10
        self.start_hotkey_listener()
        
        # Update status periodically
        self.update_status()
        
        # Clean up hotkey listener when window closes
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Mouse and Keyboard Automation Tool", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Record button
        self.record_btn = ttk.Button(control_frame, text="Start Recording", 
                                     command=self.start_recording, width=20)
        self.record_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Stop recording button
        self.stop_record_btn = ttk.Button(control_frame, text="Stop Recording (Alt+Shift+Q)", 
                                          command=self.stop_recording, width=25, state=tk.DISABLED)
        self.stop_record_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Load file button
        self.load_btn = ttk.Button(control_frame, text="Load Recording", 
                                   command=self.load_file, width=20)
        self.load_btn.grid(row=1, column=0, padx=5, pady=5)
        
        # Replay button
        self.replay_btn = ttk.Button(control_frame, text="Start Replay", 
                                     command=self.start_replay, width=20, state=tk.DISABLED)
        self.replay_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Stop replay button
        self.stop_replay_btn = ttk.Button(control_frame, text="Stop Replay (Alt+Shift+W)", 
                                         command=self.stop_replay, width=25, state=tk.DISABLED)
        self.stop_replay_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Replay Settings", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Repeat count
        ttk.Label(settings_frame, text="Repeat Count:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.repeat_var = tk.StringVar(value="1")
        repeat_spin = ttk.Spinbox(settings_frame, from_=1, to=1000, textvariable=self.repeat_var, width=10)
        repeat_spin.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Delay before start
        ttk.Label(settings_frame, text="Delay (seconds):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.delay_var = tk.StringVar(value="3")
        delay_spin = ttk.Spinbox(settings_frame, from_=0, to=60, textvariable=self.delay_var, width=10)
        delay_spin.grid(row=0, column=3, padx=5, sticky=tk.W)
        
        # Current file label
        self.current_file_label = ttk.Label(settings_frame, text="No file loaded", foreground="gray")
        self.current_file_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0), padx=5)
        
        # Log/Output area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Instructions
        instructions = (
            "Hotkeys: Alt+Shift+Q (Start/Stop Record) | Alt+Shift+W (Start/Stop Play)\n"
            "• Click 'Start Recording' or press Alt+Shift+Q to begin recording\n"
            "• Press Alt+Shift+Q again to stop recording and auto-save, or click 'Stop Recording'\n"
            "• Load a recording file, then press Alt+Shift+W or click 'Start Replay'\n"
            "• Press Alt+Shift+W during replay to stop playback"
        )
        instructions_label = ttk.Label(main_frame, text=instructions, 
                                      font=("Arial", 9), foreground="gray", justify=tk.LEFT)
        instructions_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Store loaded actions
        self.loaded_actions = None
    
    def start_hotkey_listener(self):
        """Start global hotkey listener for Alt+Shift+Q and Alt+Shift+W."""
        def on_press(key):
            try:
                if key in [Key.shift, Key.shift_l, Key.shift_r]:
                    self._hotkey_shift_pressed = True
                    return
                if key in [Key.alt, Key.alt_l, Key.alt_r]:
                    self._hotkey_alt_pressed = True
                    return
                if self._hotkey_shift_pressed and self._hotkey_alt_pressed:
                    try:
                        if key.char == 'q' or key.char == 'Q':
                            # Alt+Shift+Q: Start recording if not recording, or stop if recording
                            if not self.is_recording and not self.is_replaying:
                                self.root.after(0, self.start_recording)
                            elif self.is_recording:
                                self.root.after(0, self.stop_recording)
                            return
                        if key.char == 'w' or key.char == 'W':
                            # Alt+Shift+W: Start replay if not replaying, or stop if replaying
                            if not self.is_recording and not self.is_replaying and self.loaded_actions:
                                self.root.after(0, self.start_replay)
                            elif self.is_replaying:
                                self.root.after(0, self.stop_replay)
                            return
                    except (AttributeError, TypeError):
                        pass
            except AttributeError:
                pass
        
        def on_release(key):
            try:
                if key in [Key.shift, Key.shift_l, Key.shift_r]:
                    self._hotkey_shift_pressed = False
                if key in [Key.alt, Key.alt_l, Key.alt_r]:
                    self._hotkey_alt_pressed = False
            except AttributeError:
                pass
        
        self.hotkey_listener = KeyboardListener(
            on_press=on_press,
            on_release=on_release
        )
        self.hotkey_listener.start()
    
    def on_closing(self):
        """Clean up when closing the window."""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        self.root.destroy()
    
    def log(self, message):
        """Add a message to the log area."""
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self):
        """Update the status label and check for state changes."""
        # Check if recording has stopped (e.g., via Shift+F9)
        if self.is_recording and self.recorder and not self.recorder.recording:
            # Recording was stopped (likely by Alt+Shift+Q), update GUI state
            self.is_recording = False
            self.record_btn.config(state=tk.NORMAL)
            self.stop_record_btn.config(state=tk.DISABLED)
            self.load_btn.config(state=tk.NORMAL)
            if self.loaded_actions:
                self.replay_btn.config(state=tk.NORMAL)
        
        # Check if replay has stopped
        if self.is_replaying and self.replayer and not self.replayer.replaying:
            # Replay was stopped, update GUI state
            self.is_replaying = False
            self.record_btn.config(state=tk.NORMAL)
            self.load_btn.config(state=tk.NORMAL)
            self.replay_btn.config(state=tk.NORMAL if self.loaded_actions else tk.DISABLED)
            self.stop_replay_btn.config(state=tk.DISABLED)
        
        # Update status label
        if self.is_recording:
            self.status_label.config(text="Recording... Press Alt+Shift+Q to stop and save", 
                                    foreground="red")
        elif self.is_replaying:
            self.status_label.config(text="Replaying... Press Alt+Shift+W to stop", 
                                    foreground="blue")
        else:
            self.status_label.config(text="Ready", foreground="black")
        
        # Schedule next update
        self.root.after(100, self.update_status)
    
    def on_recording_stopped(self, filename=None):
        """Called when recording stops (via Alt+Shift+Q or manual stop)."""
        self.is_recording = False
        self.record_btn.config(state=tk.NORMAL)
        self.stop_record_btn.config(state=tk.DISABLED)
        self.load_btn.config(state=tk.NORMAL)
        if self.loaded_actions:
            self.replay_btn.config(state=tk.NORMAL)
        if filename:
            messagebox.showinfo("Saved", f"Recording saved to {filename}")
    
    def start_recording(self):
        """Start recording mouse and keyboard actions."""
        if self.is_recording or self.is_replaying:
            messagebox.showwarning("Warning", "Please stop current operation first.")
            return
        
        def auto_save(actions):
            """Auto-save callback with numbered filename."""
            if actions:
                filename = get_numbered_filename('recorded_actions.json')
                save_actions(actions, filename)
                self.log(f"Recording auto-saved to {filename}")
                # Update GUI state after auto-save
                self.root.after(0, lambda: self.on_recording_stopped(filename))
            else:
                self.log("No actions to save.")
                self.root.after(0, lambda: self.on_recording_stopped(None))
        
        self.recorder = ActionRecorder(auto_save_callback=auto_save)
        self.is_recording = True
        
        # Update UI
        self.record_btn.config(state=tk.DISABLED)
        self.stop_record_btn.config(state=tk.NORMAL)
        self.load_btn.config(state=tk.DISABLED)
        self.replay_btn.config(state=tk.DISABLED)
        
        self.log("Recording started... Press Alt+Shift+Q to stop and auto-save, or ESC to stop without saving.")
        
        # Start recording in a separate thread
        def record_thread():
            self.recorder.start_recording()
            try:
                while self.recorder.recording:
                    time.sleep(0.1)
                # Recording stopped (e.g., by Alt+Shift+Q), ensure GUI is updated if not already
                # The auto_save callback should have already updated the GUI, but this is a fallback
                if self.is_recording and not self.recorder.auto_saved:
                    self.root.after(0, lambda: self.on_recording_stopped(None))
            except:
                pass
        
        self.recording_thread = threading.Thread(target=record_thread, daemon=True)
        self.recording_thread.start()
    
    def stop_recording(self):
        """Stop recording."""
        if not self.is_recording or not self.recorder:
            return
        
        # Stop the recorder (Alt+Shift+Q would have already done this, but handle manual stop)
        actions = self.recorder.stop_recording()
        self.is_recording = False
        
        # Update UI
        self.record_btn.config(state=tk.NORMAL)
        self.stop_record_btn.config(state=tk.DISABLED)
        self.load_btn.config(state=tk.NORMAL)
        
        if actions and not self.recorder.auto_saved:
            # Ask user if they want to save
            if messagebox.askyesno("Save Recording", "Do you want to save the recording?"):
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialfile="recorded_actions.json"
                )
                if filename:
                    filename = get_numbered_filename(filename)
                    save_actions(actions, filename)
                    self.log(f"Recording saved to {filename}")
                    messagebox.showinfo("Saved", f"Recording saved to {filename}")
        
        self.log(f"Recording stopped. Total actions: {len(actions) if actions else 0}")
    
    def load_file(self):
        """Load a recording file."""
        if self.is_recording or self.is_replaying:
            messagebox.showwarning("Warning", "Please stop current operation first.")
            return
        
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="."
        )
        
        if filename:
            try:
                self.loaded_actions = load_actions(filename)
                self.current_file_label.config(text=f"Loaded: {os.path.basename(filename)}", 
                                              foreground="green")
                self.replay_btn.config(state=tk.NORMAL)
                self.log(f"Loaded {len(self.loaded_actions)} actions from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                self.log(f"Error loading file: {str(e)}")
    
    def start_replay(self):
        """Start replaying loaded actions."""
        if self.is_recording or self.is_replaying:
            messagebox.showwarning("Warning", "Please stop current operation first.")
            return
        
        if not self.loaded_actions:
            messagebox.showwarning("Warning", "Please load a recording file first.")
            return
        
        try:
            repeat_count = int(self.repeat_var.get())
            delay = int(self.delay_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for repeat count and delay.")
            return
        
        self.is_replaying = True
        self.replayer = ActionReplayer()
        
        # Update UI
        self.record_btn.config(state=tk.DISABLED)
        self.load_btn.config(state=tk.DISABLED)
        self.replay_btn.config(state=tk.DISABLED)
        self.stop_replay_btn.config(state=tk.NORMAL)
        
        self.log(f"Starting replay: {repeat_count} time(s) with {delay} second delay")
        
        # Start replay in a separate thread
        def replay_thread():
            try:
                self.replayer.replay(self.loaded_actions, repeat_count, delay)
            except Exception as e:
                self.log(f"Replay error: {str(e)}")
            finally:
                self.root.after(0, self.replay_finished)
        
        self.replaying_thread = threading.Thread(target=replay_thread, daemon=True)
        self.replaying_thread.start()
    
    def stop_replay(self):
        """Stop replay."""
        if not self.is_replaying or not self.replayer:
            return
        
        self.replayer.stop_replay = True
        self.log("Stopping replay...")
    
    def replay_finished(self):
        """Called when replay finishes."""
        self.is_replaying = False
        
        # Update UI
        self.record_btn.config(state=tk.NORMAL)
        self.load_btn.config(state=tk.NORMAL)
        self.replay_btn.config(state=tk.NORMAL)
        self.stop_replay_btn.config(state=tk.DISABLED)
        
        self.log("Replay finished.")


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

