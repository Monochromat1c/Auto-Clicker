"""
Mouse and Keyboard Automation Tool
Records mouse and keyboard actions and replays them a specified number of times.
"""

import json
import time
from datetime import datetime
from pynput import mouse, keyboard
from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener


class ActionRecorder:
    """Records mouse and keyboard actions."""
    
    def __init__(self):
        self.actions = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.recording = False
        
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
        
        print("Recording started... Press ESC to stop recording.")
        
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
            
            # Stop recording on ESC key
            if key == Key.esc:
                return False
    
    def _on_key_release(self, key):
        """Record key release."""
        if self.recording:
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
        
    def replay(self, actions, repeat_count=1, delay_before_start=3):
        """Replay recorded actions a specified number of times."""
        print(f"\nStarting replay in {delay_before_start} seconds...")
        print(f"Will repeat {repeat_count} time(s).")
        time.sleep(delay_before_start)
        
        for iteration in range(repeat_count):
            print(f"\nReplay iteration {iteration + 1}/{repeat_count}")
            start_time = time.time()
            last_action_time = 0
            
            for action in actions:
                # Wait for the correct timing
                elapsed = time.time() - start_time
                wait_time = action['time'] - last_action_time
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # Execute the action
                self._execute_action(action)
                last_action_time = action['time']
            
            # Small delay between iterations
            if iteration < repeat_count - 1:
                time.sleep(0.5)
        
        print("\nReplay completed!")
    
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
        recorder = ActionRecorder()
        recorder.start_recording()
        
        # Wait for ESC to stop (handled in listener)
        try:
            while recorder.recording:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        actions = recorder.stop_recording()
        if actions:
            filename = input("Enter filename to save (default: recorded_actions.json): ").strip()
            if not filename:
                filename = 'recorded_actions.json'
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
        recorder = ActionRecorder()
        recorder.start_recording()
        
        try:
            while recorder.recording:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        actions = recorder.stop_recording()
        if actions:
            repeat_count = int(input("How many times to replay? (default: 1): ").strip() or "1")
            delay = int(input("Delay before start in seconds (default: 3): ").strip() or "3")
            
            replayer = ActionReplayer()
            replayer.replay(actions, repeat_count, delay)
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()

