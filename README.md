# Mouse and Keyboard Automation Tool

A simple Python automation tool that records mouse and keyboard actions and replays them a specified number of times.

## Features

- **Record** mouse movements, clicks, scrolling, and keyboard presses
- **Replay** recorded actions multiple times
- **Save/Load** recorded actions to/from JSON files
- **Timing preservation** - maintains the exact timing between actions during replay

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the automation script:

```bash
python automation.py
```

You'll be presented with three options:

### Option 1: Record Actions
- Records your mouse and keyboard actions
- Press **ESC** to stop recording
- Saves the recorded actions to a JSON file

### Option 2: Replay from File
- Loads previously recorded actions from a JSON file
- Replays them a specified number of times
- Configurable delay before starting

### Option 3: Record and Replay Immediately
- Records actions, then immediately replays them
- Useful for quick testing

## How It Works

1. **Recording**: The tool captures all mouse movements, clicks, scrolls, and keyboard presses with precise timing information.

2. **Replay**: The tool replays the recorded actions in the same sequence, maintaining the original timing between actions.

3. **Repeat**: You can specify how many times to repeat the entire sequence.

## Important Notes

- **Administrator privileges**: On some systems, you may need to run the script with administrator privileges for keyboard recording to work properly.
- **Timing**: The replay maintains relative timing between actions, so the sequence will play back at the same speed as it was recorded.
- **Safety**: Always test with a small number of repeats first. The tool will move your mouse and type on your keyboard automatically.

## Example Workflow

1. Run `python automation.py`
2. Choose option 1 (Record)
3. Perform your actions (move mouse, click, type, etc.)
4. Press ESC to stop recording
5. Save to a file (e.g., `my_actions.json`)
6. Later, choose option 2 (Replay from file)
7. Load `my_actions.json` and specify how many times to replay

## Troubleshooting

- If keyboard recording doesn't work, try running as administrator
- Make sure you have the correct permissions for mouse/keyboard access
- On Linux, you may need to install additional packages: `sudo apt-get install python3-tk python3-dev`

