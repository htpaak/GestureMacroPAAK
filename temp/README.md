# Mouse Gesture Recognition Application

A simple mouse gesture recognition application built with PyQt5. This application allows you to perform various actions by making specific mouse gestures, optionally combined with keyboard modifier keys.

## Features

- Recognizes various mouse gestures (circular movements, swipes, arrows, etc.)
- Maps gestures to system actions (navigate back/forward, scroll, tab management, etc.)
- **Keyboard+Mouse gesture combinations** using Ctrl, Shift, and Alt modifiers
- **Global gesture mode** - gestures work anywhere on your screen, not just in the app
- Visual feedback of recognized gestures and active modifiers
- Real-time display of gesture path
- **Customizable gesture actions** - map any gesture to your preferred action
- System tray icon for background operation

## Requirements

- Python 3.6+
- PyQt5
- pyautogui
- pynput (for global gesture mode)

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```
2. Hold right mouse button and make gestures
3. For keyboard+mouse gestures, hold modifier keys (Ctrl, Shift, Alt) before pressing the right mouse button
4. Release the button to execute the associated action
5. Click the "Gesture Settings" button to customize gesture actions
6. Toggle "Enable global mode" to use gestures anywhere on your screen
7. The app can be minimized to system tray and continue to work in the background

## Supported Basic Gestures

- **Circle clockwise**: Default - Refresh page (F5)
- **Circle counterclockwise**: Default - Undo (Ctrl+Z)
- **Swipe right**: Default - Navigate forward (Alt+Right)
- **Swipe left**: Default - Navigate back (Alt+Left)
- **Swipe up**: Default - Scroll up
- **Swipe down**: Default - Scroll down
- **Arrow right**: Default - Next tab (Ctrl+Tab)
- **Arrow left**: Default - Previous tab (Ctrl+Shift+Tab)
- **Diagonal up-right**: Default - New tab (Ctrl+T)
- **Diagonal up-left**: Default - Close tab (Ctrl+W)

## Supported Keyboard+Mouse Gestures

- **Ctrl + Swipe right**: Default - Maximize window
- **Ctrl + Swipe left**: Default - Minimize window
- **Ctrl + Swipe up**: Default - Copy
- **Ctrl + Swipe down**: Default - Paste
- **Shift + Swipe right**: Default - Save
- **Shift + Swipe left**: Default - Print
- **Alt + Swipe right**: Default - Select all
- **Alt + Swipe left**: Default - Cut

## Available Actions

The following actions can be assigned to any gesture:

- Refresh page (F5)
- Undo (Ctrl+Z)
- Navigate forward/back
- Scroll up/down
- Tab management (next, previous, new, close)
- Window control (maximize, minimize)
- Clipboard operations (copy, cut, paste)
- Select all (Ctrl+A)
- Save (Ctrl+S)
- Print (Ctrl+P)
- No action

## Customizing Gestures

1. Click the "Gesture Settings" button in the main window
2. Switch between the "Standard Gestures" and "Keyboard+Mouse Gestures" tabs
3. For each gesture, select the desired action from the dropdown menu
4. Click "Save" to apply changes or "Reset to Defaults" to restore default settings
5. Settings are stored in `gesture_settings.json` in the application directory

## Global Mode

When global mode is enabled:

1. Gestures will be recognized anywhere on your screen, not just in the app window
2. The app can be minimized to system tray and will still detect gestures
3. Right-click and drag to perform gestures in any application or on the desktop

## System Tray

The app has a system tray icon with the following options:

- Show Window: Restore the minimized application
- Gesture Settings: Open settings dialog directly
- Toggle Global Mode: Enable/disable global gesture recognition
- Quit: Exit the application completely

## Adding Custom Gestures

You can add custom gestures by modifying the `gesture_templates` dictionary in the `GestureRecognizer` class and adding corresponding actions in the `GestureHandler` class.
