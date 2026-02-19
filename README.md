# Mouse and Keyboard Automation Tool

A simple Python automation tool that records mouse and keyboard actions and replays them a specified number of times.

## Features

- **Record** mouse movements, clicks, scrolling, and keyboard presses
- **Replay** recorded actions multiple times
- **Save/Load** recorded actions to/from JSON files
- **Timing preservation** - maintains the exact timing between actions during replay
- **F9 Hotkey** - Press F9 to stop recording and auto-save, or stop playback during replay
- **Auto-numbered filenames** - Automatically creates numbered filenames to prevent overwriting
- **Smart Alt+Tab handling** - Automatically skips the first Alt+Tab press (useful for switching to your target application)

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### GUI Version (Recommended)

For easier use, run the graphical interface:

```bash
python automation_gui.py
```

The GUI provides:
- One-click recording and replay controls
- Visual status indicators
- File browser for loading/saving recordings
- Real-time log output
- Easy-to-use settings for repeat count and delay

### Command Line Version

Run the automation script:

```bash
python automation.py
```

You'll be presented with three options:

### Option 1: Record Actions
- Records your mouse and keyboard actions
- Press **F9** to stop recording and automatically save to a numbered file
- Press **ESC** to stop recording without auto-saving (you'll be prompted for a filename)
- The first Alt+Tab you press will be automatically skipped (useful for switching to your target app)

### Option 2: Replay from File
- Loads previously recorded actions from a JSON file
- Replays them a specified number of times
- Configurable delay before starting
- Press **F9** at any time during replay to stop playback

### Option 3: Record and Replay Immediately
- Records actions, then immediately replays them
- Useful for quick testing
- Press **F9** to stop recording and auto-save, or stop playback during replay

## How It Works

1. **Recording**: The tool captures all mouse movements, clicks, scrolls, and keyboard presses with precise timing information. The first Alt+Tab combination is automatically skipped to help you switch to your target application without recording it.

2. **Replay**: The tool replays the recorded actions in the same sequence, maintaining the original timing between actions. You can stop playback at any time by pressing F9.

3. **Auto-Save**: When you press F9 during recording, the file is automatically saved with a numbered filename (e.g., `recorded_actions.json`, `recorded_actions_1.json`, etc.) to prevent overwriting existing files.

4. **Repeat**: You can specify how many times to repeat the entire sequence.

## Important Notes

- **Administrator privileges**: On some systems, you may need to run the script with administrator privileges for keyboard recording to work properly.
- **Timing**: The replay maintains relative timing between actions, so the sequence will play back at the same speed as it was recorded.
- **Safety**: Always test with a small number of repeats first. The tool will move your mouse and type on your keyboard automatically.
- **F9 Hotkey**: 
  - During recording: Stops recording and automatically saves the file
  - During replay: Stops playback immediately
- **First Alt+Tab**: The first Alt+Tab you press after starting recording is automatically skipped, making it easy to switch to your target application without recording the window switch.

## Example Workflow

### Using the GUI:

1. Run `python automation_gui.py`
2. Click "Start Recording"
3. Press Alt+Tab to switch to your target application (this won't be recorded)
4. Perform your actions (move mouse, click, type, etc.)
5. Press **F9** to stop recording and auto-save, or click "Stop Recording"
6. Click "Load Recording" to load a saved file
7. Set repeat count and delay, then click "Start Replay"
8. Press **F9** at any time during replay to stop playback

### Using the Command Line:

1. Run `python automation.py`
2. Choose option 1 (Record)
3. Press Alt+Tab to switch to your target application (this won't be recorded)
4. Perform your actions (move mouse, click, type, etc.)
5. Press **F9** to stop recording and auto-save, or **ESC** to stop without auto-saving
6. If you used F9, the file is automatically saved with a numbered filename
7. Later, choose option 2 (Replay from file)
8. Load your saved file and specify how many times to replay
9. Press **F9** at any time during replay to stop playback

## Troubleshooting

- If keyboard recording doesn't work, try running as administrator
- Make sure you have the correct permissions for mouse/keyboard access
- On Linux, you may need to install additional packages: `sudo apt-get install python3-tk python3-dev`

