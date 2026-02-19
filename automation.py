"""
Mouse and Keyboard Automation Tool
Records mouse and keyboard actions and replays them a specified number of times.
"""

import json
import os
import time
from datetime import datetime
from pynput import mouse, keyboard
from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener


class ActionRecorder:
    """Records mouse and keyboard actions."""
    
    def __init__(self, auto_save_callback=None):
        self.actions = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.recording = False
        self.shift_pressed = False
        self.alt_pressed = False
        self.auto_save_callback = auto_save_callback
        self.auto_saved = False
        self.first_alt_tab_skipped = False
        self.skipping_first_alt_tab = False
        
    def start_recording(self):
        """Start recording mouse and keyboard actions."""
        self.actions = []
        self.start_time = time.time()
        self.recording = True
        
        # Start mouse listener
        self.mouse_listener = MouseListener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.start()
        
        # Start keyboard listener
        self.keyboard_listener = KeyboardListener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        
        print("Recording started... Press F9 to stop and auto-save, or ESC to stop without saving.")
        
    def stop_recording(self):
        """Stop recording and return the recorded actions."""
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        print(f"Recording stopped. Total actions recorded: {len(self.actions)}")
        return self.actions
    
    def _on_mouse_move(self, x, y):
        """Record mouse movement."""
        if self.recording:
            elapsed = time.time() - self.start_time
            self.actions.append({
                'type': 'mouse_move',
                'x': x,
                'y': y,
                'time': elapsed
            })
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Record mouse clicks."""
        if self.recording:
            elapsed = time.time() - self.start_time
            self.actions.append({
                'type': 'mouse_click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'time': elapsed
            })
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Record mouse scroll."""
        if self.recording:
            elapsed = time.time() - self.start_time
            self.actions.append({
                'type': 'mouse_scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'time': elapsed
            })
    
    def _on_key_press(self, key):
        """Record key press."""
        if self.recording:
            # Check for F9 key (auto-save) or ESC key (no save) first, before recording
            # Check for F9 key
            try:
                is_f9 = key == Key.f9
            except AttributeError:
                # Fallback to string comparison if Key.f9 doesn't exist
                is_f9 = str(key) == 'Key.f9'
            
            if is_f9:
                # Stop recording and trigger auto-save (don't record F9)
                self.recording = False
                if self.auto_save_callback:
                    self.auto_save_callback(self.actions)
                    self.auto_saved = True
                return False
            elif key == Key.esc:
                # Stop recording without auto-save (don't record ESC)
                return False
            
            # Track modifier keys first
            if key == Key.shift or key == Key.shift_l or key == Key.shift_r:
                self.shift_pressed = True
            elif key == Key.alt or key == Key.alt_l or key == Key.alt_r:
                self.alt_pressed = True
            
            # Skip recording the first Alt+Tab combination
            # When Tab is pressed while Alt is held (and Shift is not), skip the first occurrence
            if key == Key.tab and self.alt_pressed and not self.shift_pressed:
                if not self.first_alt_tab_skipped:
                    self.first_alt_tab_skipped = True
                    self.skipping_first_alt_tab = True
                    # Remove any Alt key press that was just recorded (if it exists)
                    # Find and remove the most recent Alt key press/release
                    for i in range(len(self.actions) - 1, -1, -1):
                        action = self.actions[i]
                        if action['type'] in ['key_press', 'key_release']:
                            key_str = action.get('key', '')
                            if 'alt' in key_str.lower() or key_str in ['Key.alt', 'Key.alt_l', 'Key.alt_r']:
                                self.actions.pop(i)
                                break
                    return
            
            # Skip recording Shift+Alt+Tab combination
            if key == Key.tab and self.shift_pressed and self.alt_pressed:
                return
            
            elapsed = time.time() - self.start_time
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key)
            
            self.actions.append({
                'type': 'key_press',
                'key': key_str,
                'time': elapsed
            })
    
    def _on_key_release(self, key):
        """Record key release."""
        if self.recording:
            # Skip recording the first Alt+Tab combination (check before updating modifier states)
            if key == Key.tab and self.alt_pressed and not self.shift_pressed:
                if self.skipping_first_alt_tab:
                    # This is the first Alt+Tab release, skip it
                    return
            
            # Skip recording Shift+Alt+Tab combination (check before updating modifier states)
            if key == Key.tab and self.shift_pressed and self.alt_pressed:
                return
            
            # Track modifier keys
            if key == Key.shift or key == Key.shift_l or key == Key.shift_r:
                self.shift_pressed = False
            elif key == Key.alt or key == Key.alt_l or key == Key.alt_r:
                # If we're skipping the first Alt+Tab, don't record Alt key releases either
                if self.skipping_first_alt_tab:
                    # Check if Alt is being released (which ends the Alt+Tab sequence)
                    self.alt_pressed = False
                    self.skipping_first_alt_tab = False
                    return
                self.alt_pressed = False
            
            elapsed = time.time() - self.start_time
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key)
            
            self.actions.append({
                'type': 'key_release',
                'key': key_str,
                'time': elapsed
            })


class ActionReplayer:
    """Replays recorded mouse and keyboard actions."""
    
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.replaying = False
        self.stop_replay = False
        self.keyboard_listener = None
        
    def _on_key_press_replay(self, key):
        """Handle key press during replay - stop on F9."""
        # Check for F9 key
        try:
            is_f9 = key == Key.f9
        except AttributeError:
            # Fallback to string comparison if Key.f9 doesn't exist
            is_f9 = str(key) == 'Key.f9'
        
        if is_f9:
            self.stop_replay = True
            return False  # Stop the listener
    
    def replay(self, actions, repeat_count=1, delay_before_start=3):
        """Replay recorded actions a specified number of times."""
        self.replaying = True
        self.stop_replay = False
        
        # Start keyboard listener to detect F9
        self.keyboard_listener = KeyboardListener(
            on_press=self._on_key_press_replay
        )
        self.keyboard_listener.start()
        
        print(f"\nStarting replay in {delay_before_start} seconds...")
        print(f"Will repeat {repeat_count} time(s).")
        print("Press F9 to stop playback at any time.")
        time.sleep(delay_before_start)
        
        try:
            for iteration in range(repeat_count):
                if self.stop_replay:
                    print(f"\nPlayback stopped by user at iteration {iteration + 1}")
                    break
                
                print(f"\nReplay iteration {iteration + 1}/{repeat_count}")
                start_time = time.time()
                last_action_time = 0
                
                for action in actions:
                    if self.stop_replay:
                        print(f"\nPlayback stopped by user during iteration {iteration + 1}")
                        break
                    
                    # Wait for the correct timing (check for stop during wait)
                    elapsed = time.time() - start_time
                    wait_time = action['time'] - last_action_time
                    if wait_time > 0:
                        # Break wait into smaller chunks to check for stop
                        chunk_size = 0.1
                        waited = 0
                        while waited < wait_time and not self.stop_replay:
                            sleep_time = min(chunk_size, wait_time - waited)
                            time.sleep(sleep_time)
                            waited += sleep_time
                    
                    if self.stop_replay:
                        break
                    
                    # Execute the action
                    self._execute_action(action)
                    last_action_time = action['time']
                
                if self.stop_replay:
                    break
                
                # Small delay between iterations
                if iteration < repeat_count - 1:
                    time.sleep(0.5)
            
            if not self.stop_replay:
                print("\nReplay completed!")
            else:
                print("\nPlayback stopped.")
        finally:
            # Clean up
            self.replaying = False
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
    
    def _execute_action(self, action):
        """Execute a single recorded action."""
        action_type = action['type']
        
        if action_type == 'mouse_move':
            self.mouse_controller.position = (action['x'], action['y'])
        
        elif action_type == 'mouse_click':
            self.mouse_controller.position = (action['x'], action['y'])
            button = Button.left if 'left' in action['button'] else Button.right
            if action['pressed']:
                self.mouse_controller.press(button)
            else:
                self.mouse_controller.release(button)
        
        elif action_type == 'mouse_scroll':
            self.mouse_controller.position = (action['x'], action['y'])
            self.mouse_controller.scroll(action['dx'], action['dy'])
        
        elif action_type == 'key_press':
            key = self._parse_key(action['key'])
            if key:
                self.keyboard_controller.press(key)
        
        elif action_type == 'key_release':
            key = self._parse_key(action['key'])
            if key:
                self.keyboard_controller.release(key)
    
    def _parse_key(self, key_str):
        """Parse key string to Key object."""
        # Handle special keys
        special_keys = {
            'Key.space': Key.space,
            'Key.enter': Key.enter,
            'Key.shift': Key.shift,
            'Key.ctrl': Key.ctrl,
            'Key.alt': Key.alt,
            'Key.tab': Key.tab,
            'Key.backspace': Key.backspace,
            'Key.delete': Key.delete,
            'Key.esc': Key.esc,
            'Key.up': Key.up,
            'Key.down': Key.down,
            'Key.left': Key.left,
            'Key.right': Key.right,
        }
        
        if key_str in special_keys:
            return special_keys[key_str]
        elif key_str.startswith('Key.'):
            # Try to get the key by name
            try:
                return getattr(Key, key_str.split('.')[1])
            except:
                return None
        else:
            # Regular character
            return key_str


def get_numbered_filename(base_filename='recorded_actions.json'):
    """Generate a numbered filename if the base filename already exists."""
    if not os.path.exists(base_filename):
        return base_filename
    
    # Split filename and extension
    base_name, ext = os.path.splitext(base_filename)
    counter = 1
    
    # Find the next available number
    while True:
        numbered_filename = f"{base_name}_{counter}{ext}"
        if not os.path.exists(numbered_filename):
            return numbered_filename
        counter += 1


def save_actions(actions, filename='recorded_actions.json'):
    """Save recorded actions to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(actions, f, indent=2)
    print(f"Actions saved to {filename}")


def load_actions(filename='recorded_actions.json'):
    """Load recorded actions from a JSON file."""
    with open(filename, 'r') as f:
        actions = json.load(f)
    print(f"Actions loaded from {filename}")
    return actions


def main():
    """Main function to run the automation tool."""
    print("=" * 50)
    print("Mouse and Keyboard Automation Tool")
    print("=" * 50)
    print("\n1. Record actions")
    print("2. Replay from file")
    print("3. Record and replay immediately")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == '1':
        # Record only
        def auto_save(actions):
            """Auto-save callback with numbered filename."""
            if actions:
                filename = get_numbered_filename('recorded_actions.json')
                save_actions(actions, filename)
            else:
                print("No actions to save.")
        
        recorder = ActionRecorder(auto_save_callback=auto_save)
        recorder.start_recording()
        
        # Wait for F9 or ESC to stop (handled in listener)
        try:
            while recorder.recording:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        actions = recorder.stop_recording()
        # Only prompt for filename if recording was stopped with ESC (not F9)
        if actions and not recorder.auto_saved:
            filename = input("Enter filename to save (default: recorded_actions.json): ").strip()
            if not filename:
                filename = 'recorded_actions.json'
            filename = get_numbered_filename(filename)
            save_actions(actions, filename)
    
    elif choice == '2':
        # Replay from file
        filename = input("Enter filename to load (default: recorded_actions.json): ").strip()
        if not filename:
            filename = 'recorded_actions.json'
        
        try:
            actions = load_actions(filename)
            repeat_count = int(input("How many times to replay? (default: 1): ").strip() or "1")
            delay = int(input("Delay before start in seconds (default: 3): ").strip() or "3")
            
            replayer = ActionReplayer()
            replayer.replay(actions, repeat_count, delay)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except ValueError:
            print("Error: Invalid number entered.")
    
    elif choice == '3':
        # Record and replay immediately
        saved_actions = []
        auto_saved = False
        
        def auto_save(actions):
            """Auto-save callback with numbered filename."""
            nonlocal saved_actions, auto_saved
            if actions:
                filename = get_numbered_filename('recorded_actions.json')
                save_actions(actions, filename)
                saved_actions = actions
                auto_saved = True
        
        recorder = ActionRecorder(auto_save_callback=auto_save)
        recorder.start_recording()
        
        try:
            while recorder.recording:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        actions = recorder.stop_recording()
        # Use saved actions if auto-saved, otherwise use current actions
        if auto_saved and saved_actions:
            actions = saved_actions
        
        if actions:
            repeat_count = int(input("How many times to replay? (default: 1): ").strip() or "1")
            delay = int(input("Delay before start in seconds (default: 3): ").strip() or "3")
            
            replayer = ActionReplayer()
            replayer.replay(actions, repeat_count, delay)
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

