# Advanced Auto Clicker for Windows

A powerful Windows auto-clicker with advanced features for game automation, specifically optimized for Roblox and other games that require precise mouse and keyboard control.

## 🎮 Features

### Window-Specific Clicking
- **Target Specific Windows**: Select any window from a dropdown list - clicks only affect that window
- **Background Operation**: Works even when the window is minimized or in the background
- **Automatic Window Detection**: Refreshes and lists all open windows
- **Foreground Control**: Optional setting to keep the game window in foreground during automation

### Click Sequence Builder
The sequence builder allows you to create complex multi-step automation:

- **Click Actions**: Click at specific X/Y coordinates with pixel-perfect precision
- **Keyboard Actions**: Press any key (letters, space, enter, arrow keys, etc.)
- **Custom Delays**: Set individual delay times after each action (in seconds)
- **Repeat Counts**: Configure how many times each action repeats before moving to the next step
- **Save & Load**: Export sequences to JSON files and reload them anytime
- **Visual Step Cards**: Each step displayed as a card showing all its settings
- **Easy Reordering**: Steps execute in the order they're added

### Three Click Modes

1. **Current Cursor Mode**
   - Clicks wherever your mouse cursor is currently positioned
   - Useful for simple repetitive clicking at your mouse location

2. **Single Position Mode**
   - Repeatedly clicks at one specific X/Y coordinate
   - Set position manually or capture your current mouse position
   - Ideal for farming/grinding at a single button location

3. **Click Sequence Mode**
   - Execute a series of clicks and key presses in order
   - Each step can have different coordinates, delays, and repeat counts
   - Perfect for complex game automation (combat sequences, crafting, quests)

### Click Methods

**Physical Mode** ⭐ (Recommended for Roblox)
- Actually moves the physical mouse cursor to the target position
- Performs real mouse clicks that games can detect
- Includes intelligent hover behavior:
  - Moves to position with slight offset (3 pixels)
  - Moves to exact target position
  - Hovers for 500ms to trigger hover-sensitive UI elements
- Works with games that require physical input (like Roblox)

**Window Message Mode**
- Sends click messages directly to the window without moving mouse
- Faster execution (no mouse movement delay)
- Doesn't work with all games (many modern games ignore window messages)

### Position Capture Tools

**Set Current Pos Button**
- Captures your current mouse position instantly
- Automatically converts to window-relative coordinates
- One-click convenience for quick positioning

**Click to Capture**
- Opens a capture mode where you click anywhere on the target window
- Shows a popup with both window-relative and absolute screen coordinates
- Target window is brought to front automatically for easy selection
- Perfect for precise positioning of buttons, UI elements, etc.

## 📖 How to Use

### Getting Started

1. **Launch the Application**
   - Double-click `run.bat`, OR
   - Open terminal and run: `python auto_clicker.py`

2. **Select Your Target Window**
   - Click "Refresh Windows" to see all open windows
   - Choose your game/application from the dropdown (e.g., "Roblox")

3. **Configure Basic Settings**
   - **Interval**: Time between actions (e.g., 1.0 = one per second)
   - **Mouse Button**: Left, Right, or Middle click
   - **Click Type**: Single or Double click
   - **Click Method**: Choose Physical for Roblox, Window Message for other apps
   - **Keep in Foreground**: Check this for Roblox to prevent window minimizing

### Creating Your First Click Sequence

**Step 1: Switch to Sequence Mode**
- Set "Click Mode" dropdown to "Click Sequence"
- The Click Sequence Builder panel will appear

**Step 2: Add Click Actions**
- Click the **"+ Add Click"** button
- A new step card appears with these fields:
  - **X**: Horizontal position (pixels from left edge)
  - **Y**: Vertical position (pixels from top edge)
  - **Delay**: Wait time after this click (seconds)
  - **Repeat**: How many times to click here
- Use **"Click to Capture"** to get exact coordinates by clicking on the game
- Click the **X** button on any step to remove it

**Step 3: Add Keyboard Actions**
- Click the **"+ Add Key Press"** button
- Enter the key name in the Key field:
  - Letters: `e`, `r`, `t`, etc.
  - Special keys: `space`, `enter`, `tab`, `esc`
  - Arrow keys: `up`, `down`, `left`, `right`
  - Function keys: `f1`, `f2`, etc.
- Set delay and repeat count

**Step 4: Arrange Your Sequence**
- Steps execute from top to bottom
- Remove unwanted steps with the X button
- The entire sequence loops continuously when running

**Step 5: Save Your Sequence (Optional)**
- Click **"Save Sequence"** to export to a JSON file
- Click **"Load Sequence"** to import previously saved sequences
- Sequences remember all clicks, keys, delays, and repeat counts

### Example: Roblox Combat Automation

Let's create a combat sequence that enters battle, attacks, and waits for cooldowns:

1. **Setup**
   - Select your Roblox window
   - Set Click Method to **Physical**
   - Check **"Keep game window in foreground"**
   - Set Click Mode to **Click Sequence**

2. **Build the Sequence**

   **Step 1: Enter Combat Mode**
   - Click **"+ Add Key Press"**
   - Key: `e`
   - Delay: `1.0` (wait 1 second after pressing E)
   - Repeat: `1`

   **Step 2: Click Battle Button**
   - Click **"+ Add Click"**
   - Use "Click to Capture" and click the battle button in your game
   - Delay: `0.5` (wait half second for battle to start)
   - Repeat: `1`

   **Step 3: First Strike**
   - Click **"+ Add Click"**
   - Use "Click to Capture" on your attack/strike button
   - Delay: `9.0` (wait for cooldown - adjust to your game)
   - Repeat: `1`

   **Step 4: Second Strike**
   - Click **"+ Add Click"**
   - Use same coordinates as Step 3, or capture again
   - Delay: `1.0`
   - Repeat: `1`

3. **Start Automation**
   - Press **F6** (or click Start button)
   - The sequence loops: E key → battle button → strike → wait 9s → strike → repeat
   - Press **F6** again to stop

4. **Save for Later**
   - Click **"Save Sequence"**
   - Give it a name like "roblox_combat.json"
   - Load it anytime to reuse this exact sequence

### Example: Crafting/Grinding Loop

For repetitive crafting or resource gathering:

1. Set up sequence with clicks on:
   - Resource node (X: 500, Y: 300, Delay: 2.0, Repeat: 5)
   - Craft button (X: 600, Y: 450, Delay: 1.0, Repeat: 1)
   - Collect button (X: 650, Y: 500, Delay: 1.0, Repeat: 1)
2. Press F6 to start the loop
3. Monitors your game while it runs automatically

## ⌨️ Hotkeys

- **F6**: Toggle Start/Stop (works even when the app is in the background)

## 🛠️ Installation

### Requirements
- **Operating System**: Windows 10/11
- **Python**: 3.13 or higher

### Setup Instructions

1. **Clone or Download** this repository

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs:
   - `pywin32>=307` - Windows API for window control
   - `pynput>=1.7.6` - Keyboard/mouse event handling
   - `pyautogui>=0.9.54` - Physical mouse/keyboard control

3. **Run the Application**:
   - Easy way: Double-click `run.bat`
   - Manual way: `python auto_clicker.py`

## 💡 Tips & Best Practices

- **Always use Physical mode for Roblox** - Window Message mode doesn't work with most modern games
- **The hover effect matters** - The 500ms hover helps trigger buttons that need mouse-over state
- **Use Click to Capture** - Much more accurate than manually entering coordinates
- **Test before long runs** - Run your sequence once manually to verify it works correctly
- **Save your sequences** - Don't rebuild complex sequences every time
- **Reasonable delays** - Keep delays sensible to avoid looking like a bot or overwhelming the game
- **Don't move/resize windows** - Captured coordinates are relative to the window's current size and position
- **Check repeat counts** - Use repeat counts instead of duplicate steps for efficiency

## 🐛 Troubleshooting

### Clicks Not Working in Roblox
- ✅ Make sure **Physical** click method is selected (not Window Message)
- ✅ Verify "Keep game window in foreground" is checked
- ✅ Try increasing the interval between clicks

### Window Keeps Minimizing
- ✅ Check the **"Keep game window in foreground"** checkbox
- ✅ Verify you selected the correct window in the dropdown

### Buttons Not Activating / Clicks Missing
- ✅ The 500ms hover should help, but some UI needs longer - try adding more delay
- ✅ Make sure coordinates are accurate - use "Click to Capture"
- ✅ Verify the game window hasn't moved or been resized since capturing coordinates

### Wrong Coordinates / Clicking in Wrong Place
- ✅ Don't move or resize the target window after capturing positions
- ✅ Use window-relative coordinates (which the tool provides automatically)
- ✅ Recapture positions if the window was moved

### Sequence Not Saving/Loading
- ✅ Check that you have write permissions in the directory
- ✅ Ensure the file path doesn't contain special characters
- ✅ Try saving to a different location

### F6 Hotkey Not Working
- ✅ Make sure the application is running (check system tray or taskbar)
- ✅ Try clicking Start/Stop button directly
- ✅ Restart the application

## ⚠️ Important Notes

- **Use Responsibly**: Only use on applications where you have permission to automate
- **Game Rules**: Some games prohibit automation - check terms of service
- **Anti-Cheat**: Games with anti-cheat may detect and ban automation
- **Window Position**: Keep target window at same size/position when using saved sequences
- **Coordinate System**: All coordinates are relative to the window's client area
- **Background Usage**: While clicking runs in background, Physical mode will move your actual mouse

## 📄 License

Use this software responsibly and at your own risk. The developers are not responsible for any bans, suspensions, or other consequences resulting from use of this tool.

---

**Version**: 2.0  
**Last Updated**: November 2025  
**Compatibility**: Windows 10/11, Python 3.13+
