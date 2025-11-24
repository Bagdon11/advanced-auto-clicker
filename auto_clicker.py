import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import win32gui
import win32con
import win32api
import threading
import time
from pynput import keyboard, mouse
import ctypes
import json
import os
import pyautogui

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Window-Specific Auto Clicker")
        self.root.geometry("650x650")
        self.root.resizable(True, True)
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        self.clicking = False
        self.click_thread = None
        self.target_hwnd = None
        self.listener = None
        self.click_sequence = []  # List of (action_type, data, delay) tuples
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure root grid to expand
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Configure main_frame grid - only row 11 (sequence builder) should expand
        for i in range(16):  # Set all rows to not expand
            main_frame.grid_rowconfigure(i, weight=0)
        main_frame.grid_rowconfigure(11, weight=1)  # Only row 11 expands (seq_frame)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Window selection
        ttk.Label(main_frame, text="Select Target Window:", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.window_combo = ttk.Combobox(main_frame, width=50, state='readonly')
        self.window_combo.grid(row=1, column=0, columnspan=2, pady=(0, 5))
        
        ttk.Button(main_frame, text="Refresh Windows", command=self.refresh_windows).grid(row=2, column=0, columnspan=2, pady=(0, 15))
        
        # Click settings
        ttk.Label(main_frame, text="Click Settings:", font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 5))
        
        # Click interval
        ttk.Label(main_frame, text="Interval (seconds):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.StringVar(value="1.0")
        interval_entry = ttk.Entry(main_frame, textvariable=self.interval_var, width=15)
        interval_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Click button type
        ttk.Label(main_frame, text="Mouse Button:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.button_var = tk.StringVar(value="Left")
        button_combo = ttk.Combobox(main_frame, textvariable=self.button_var, width=12, state='readonly')
        button_combo['values'] = ('Left', 'Right', 'Middle')
        button_combo.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Click type
        ttk.Label(main_frame, text="Click Type:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.click_type_var = tk.StringVar(value="Single")
        click_type_combo = ttk.Combobox(main_frame, textvariable=self.click_type_var, width=12, state='readonly')
        click_type_combo['values'] = ('Single', 'Double')
        click_type_combo.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Click method
        ttk.Label(main_frame, text="Click Method:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.click_method_var = tk.StringVar(value="Physical")
        method_combo = ttk.Combobox(main_frame, textvariable=self.click_method_var, width=15, state='readonly')
        method_combo['values'] = ('Physical', 'Window Message')
        method_combo.grid(row=7, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="(Use Physical for Roblox)", font=('Arial', 8), foreground='blue').grid(row=7, column=0, columnspan=2, sticky=tk.E, padx=(0, 5), pady=5)
        
        # Keep target window active option
        self.keep_window_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Keep game window in foreground (for Roblox)", 
                       variable=self.keep_window_active_var).grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Click position mode
        ttk.Label(main_frame, text="Click Mode:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.position_mode_var = tk.StringVar(value="Single Position")
        position_combo = ttk.Combobox(main_frame, textvariable=self.position_mode_var, width=15, state='readonly')
        position_combo['values'] = ('Current Cursor', 'Single Position', 'Click Sequence')
        position_combo.grid(row=9, column=1, sticky=tk.W, pady=5)
        
        # Single position frame
        self.pos_frame = ttk.Frame(main_frame)
        self.pos_frame.grid(row=10, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(self.pos_frame, text="X:").grid(row=0, column=0, padx=5)
        self.x_var = tk.StringVar(value="0")
        ttk.Entry(self.pos_frame, textvariable=self.x_var, width=8).grid(row=0, column=1, padx=5)
        
        ttk.Label(self.pos_frame, text="Y:").grid(row=0, column=2, padx=5)
        self.y_var = tk.StringVar(value="0")
        ttk.Entry(self.pos_frame, textvariable=self.y_var, width=8).grid(row=0, column=3, padx=5)
        
        ttk.Button(self.pos_frame, text="Set Current Pos", command=self.set_current_position).grid(row=0, column=4, padx=5)
        
        # Click sequence frame
        self.seq_frame = ttk.LabelFrame(main_frame, text="Click Sequence Builder", padding="5")
        self.seq_frame.grid(row=11, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure seq_frame to expand
        self.seq_frame.grid_rowconfigure(0, weight=1)
        self.seq_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable canvas for sequence steps
        self.seq_canvas = tk.Canvas(self.seq_frame, height=150, bg='white')
        seq_scrollbar = ttk.Scrollbar(self.seq_frame, orient="vertical", command=self.seq_canvas.yview)
        self.seq_steps_frame = ttk.Frame(self.seq_canvas)
        
        self.seq_steps_frame.bind(
            "<Configure>",
            lambda e: self.seq_canvas.configure(scrollregion=self.seq_canvas.bbox("all"))
        )
        
        self.seq_canvas.create_window((0, 0), window=self.seq_steps_frame, anchor="nw")
        self.seq_canvas.configure(yscrollcommand=seq_scrollbar.set)
        
        self.seq_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        seq_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=5)
        
        # Action buttons at bottom
        seq_button_frame = ttk.Frame(self.seq_frame)
        seq_button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(seq_button_frame, text="+ Add Click", command=lambda: self.add_step_ui('click')).grid(row=0, column=0, padx=5)
        ttk.Button(seq_button_frame, text="+ Add Key Press", command=lambda: self.add_step_ui('key')).grid(row=0, column=1, padx=5)
        ttk.Button(seq_button_frame, text="Clear All", command=self.clear_sequence).grid(row=0, column=2, padx=5)
        ttk.Button(seq_button_frame, text="Save Sequence", command=self.save_sequence).grid(row=0, column=3, padx=5)
        ttk.Button(seq_button_frame, text="Load Sequence", command=self.load_sequence).grid(row=0, column=4, padx=5)
        
        self.step_widgets = []  # Track step UI elements
        
        position_combo.bind('<<ComboboxSelected>>', self.toggle_position_frame)
        # Show appropriate frame by default
        self.toggle_position_frame()
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=0, columnspan=2, pady=(20, 5))
        
        self.start_button = ttk.Button(button_frame, text="Start (F6)", command=self.start_clicking, width=15)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop (F6)", command=self.stop_clicking, width=15, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Status: Idle")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        status_label.grid(row=13, column=0, columnspan=2, pady=(10, 0))
        
        # Instructions
        instructions = ttk.Label(main_frame, text="Press F6 to start/stop clicking\nClicks in background - you can use other windows!", font=('Arial', 9, 'italic'))
        instructions.grid(row=14, column=0, columnspan=2, pady=(5, 0))
        
        # Initialize
        self.refresh_windows()
        self.setup_hotkey()
        
    def refresh_windows(self):
        """Get list of visible windows"""
        windows = []
        
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append((title, hwnd))
            return True
        
        win32gui.EnumWindows(callback, None)
        
        self.window_list = windows
        self.window_combo['values'] = [title for title, _ in windows]
        if windows:
            self.window_combo.current(0)
    
    def toggle_position_frame(self, event=None):
        """Show/hide position inputs based on mode"""
        mode = self.position_mode_var.get()
        if mode == "Single Position":
            self.pos_frame.grid()
            self.seq_frame.grid_remove()
        elif mode == "Click Sequence":
            self.pos_frame.grid_remove()
            self.seq_frame.grid()
        else:  # Current Cursor
            self.pos_frame.grid_remove()
            self.seq_frame.grid_remove()
    
    def toggle_sequence_inputs(self, event=None):
        """Show/hide inputs based on action type"""
        if self.seq_action_var.get() == "Click":
            self.seq_click_frame.grid()
            self.seq_key_frame.grid_remove()
        else:  # Key Press
            self.seq_click_frame.grid_remove()
            self.seq_key_frame.grid()
    
    def add_step_ui(self, action_type):
        """Add a new step UI element"""
        step_num = len(self.step_widgets) + 1
        
        # Create frame for this step
        step_frame = ttk.LabelFrame(self.seq_steps_frame, text=f"Step {step_num}", padding="5")
        step_frame.grid(row=step_num-1, column=0, pady=5, padx=5, sticky=(tk.W, tk.E))
        
        step_data = {'frame': step_frame, 'type': action_type}
        
        if action_type == 'click':
            # Click step UI
            ttk.Label(step_frame, text="Action: Click", font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=2)
            
            ttk.Label(step_frame, text="X:").grid(row=1, column=0, padx=2, sticky=tk.E)
            x_var = tk.StringVar(value="0")
            ttk.Entry(step_frame, textvariable=x_var, width=8).grid(row=1, column=1, padx=2)
            
            ttk.Label(step_frame, text="Y:").grid(row=1, column=2, padx=2, sticky=tk.E)
            y_var = tk.StringVar(value="0")
            ttk.Entry(step_frame, textvariable=y_var, width=8).grid(row=1, column=3, padx=2)
            
            ttk.Button(step_frame, text="Get Current Position", 
                      command=lambda: self.get_position_for_step(x_var, y_var)).grid(row=1, column=4, padx=5)
            ttk.Button(step_frame, text="Click to Capture", 
                      command=lambda: self.click_to_capture_position(x_var, y_var)).grid(row=1, column=5, padx=5)
            
            ttk.Label(step_frame, text="Delay after (seconds):").grid(row=2, column=0, columnspan=2, sticky=tk.E, padx=2)
            delay_var = tk.StringVar(value="1.0")
            ttk.Entry(step_frame, textvariable=delay_var, width=8).grid(row=2, column=2, padx=2, sticky=tk.W)
            
            ttk.Label(step_frame, text="Repeat:").grid(row=2, column=3, sticky=tk.E, padx=2)
            repeat_var = tk.StringVar(value="1")
            ttk.Entry(step_frame, textvariable=repeat_var, width=5).grid(row=2, column=4, padx=2, sticky=tk.W)
            ttk.Label(step_frame, text="times", font=('Arial', 8)).grid(row=2, column=5, sticky=tk.W)
            
            step_data.update({'x_var': x_var, 'y_var': y_var, 'delay_var': delay_var, 'repeat_var': repeat_var})
            
        else:  # key press
            # Key step UI
            ttk.Label(step_frame, text="Action: Key Press", font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=2)
            
            ttk.Label(step_frame, text="Key:").grid(row=1, column=0, padx=2, sticky=tk.E)
            key_var = tk.StringVar(value="e")
            ttk.Entry(step_frame, textvariable=key_var, width=12).grid(row=1, column=1, padx=2, sticky=tk.W)
            ttk.Label(step_frame, text="(e.g., e, space, enter)", font=('Arial', 8)).grid(row=1, column=2, columnspan=2, sticky=tk.W)
            
            ttk.Label(step_frame, text="Delay after (seconds):").grid(row=2, column=0, columnspan=2, sticky=tk.E, padx=2)
            delay_var = tk.StringVar(value="1.0")
            ttk.Entry(step_frame, textvariable=delay_var, width=8).grid(row=2, column=2, padx=2, sticky=tk.W)
            
            ttk.Label(step_frame, text="Repeat:").grid(row=2, column=3, sticky=tk.E, padx=2)
            repeat_var = tk.StringVar(value="1")
            ttk.Entry(step_frame, textvariable=repeat_var, width=5).grid(row=2, column=4, padx=2, sticky=tk.W)
            ttk.Label(step_frame, text="times", font=('Arial', 8)).grid(row=2, column=5, sticky=tk.W)
            
            step_data.update({'key_var': key_var, 'delay_var': delay_var, 'repeat_var': repeat_var})
        
        # Remove button
        ttk.Button(step_frame, text="✕ Remove", 
                  command=lambda: self.remove_step_ui(step_data)).grid(row=0, column=4, padx=5, sticky=tk.E)
        
        self.step_widgets.append(step_data)
        self.update_step_numbers()
        self.rebuild_sequence()
    
    def get_position_for_step(self, x_var, y_var):
        """Get cursor position for a specific step"""
        hwnd = self.get_selected_window_hwnd()
        if not hwnd:
            messagebox.showerror("Error", "Please select a window first!")
            return
        
        # Check if window is minimized
        if win32gui.IsIconic(hwnd):
            messagebox.showwarning("Window Minimized", "The target window is minimized! Please restore it first.\nMinimized windows have invalid coordinates.")
            return
        
        # Bring target window to front
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass
        
        # Give user time to position cursor
        def capture_after_delay():
            time.sleep(3.0)
            cursor_pos = win32gui.GetCursorPos()
            rect = win32gui.GetWindowRect(hwnd)
            rel_x = cursor_pos[0] - rect[0]
            rel_y = cursor_pos[1] - rect[1]
            
            x_var.set(str(rel_x))
            y_var.set(str(rel_y))
            self.root.after(0, lambda: messagebox.showinfo("Position Captured", f"Position set to ({rel_x}, {rel_y})"))
            # Bring auto-clicker back to front
            self.root.after(0, lambda: self.root.attributes('-topmost', True))
        
        # Temporarily disable topmost to allow target window to come forward
        self.root.attributes('-topmost', False)
        messagebox.showinfo("Get Position", "Target window will come to front.\nMove your cursor to the desired position.\nPosition will be captured in 3 seconds...")
        
        threading.Thread(target=capture_after_delay, daemon=True).start()
    
    def click_to_capture_position(self, x_var, y_var):
        """Capture position when user clicks - more precise than timer"""
        hwnd = self.get_selected_window_hwnd()
        if not hwnd:
            messagebox.showerror("Error", "Please select a window first!")
            return
        
        # Check if window is minimized
        if win32gui.IsIconic(hwnd):
            messagebox.showwarning("Window Minimized", "The target window is minimized! Please restore it first.\nMinimized windows have invalid coordinates.")
            return
        
        # Bring target window to front
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass
        
        self.root.attributes('-topmost', False)
        
        # Use pynput to capture the next click
        def on_click(x, y, button, pressed):
            if pressed:  # Only capture on press, not release
                rect = win32gui.GetWindowRect(hwnd)
                rel_x = x - rect[0]
                rel_y = y - rect[1]
                
                x_var.set(str(rel_x))
                y_var.set(str(rel_y))
                
                # Show confirmation and restore auto-clicker
                self.root.after(0, lambda: messagebox.showinfo("Position Captured", f"Clicked position captured!\n\nWindow-relative: ({rel_x}, {rel_y})\nScreen position: ({x}, {y})"))
                self.root.after(0, lambda: self.root.attributes('-topmost', True))
                
                # Stop listener
                return False  # Stops the listener
        
        # Start click listener
        from pynput import mouse
        messagebox.showinfo("Click to Capture", "Target window will come to front.\n\nClick ANYWHERE on the target window to capture that position.\n\nTip: Take your time - click exactly where you want the auto-clicker to click!")
        
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def remove_step_ui(self, step_data):
        """Remove a step from the UI"""
        step_data['frame'].destroy()
        self.step_widgets.remove(step_data)
        self.update_step_numbers()
        self.rebuild_sequence()
    
    def update_step_numbers(self):
        """Update step numbers in the UI"""
        for i, step_data in enumerate(self.step_widgets, 1):
            step_data['frame'].config(text=f"Step {i}")
    
    def rebuild_sequence(self):
        """Rebuild the click_sequence list from UI widgets"""
        self.click_sequence.clear()
        
        for step_data in self.step_widgets:
            try:
                delay = float(step_data['delay_var'].get())
                if delay < 0.1:
                    delay = 0.1
                
                repeat = int(step_data.get('repeat_var', tk.StringVar(value="1")).get())
                if repeat < 1:
                    repeat = 1
                
                if step_data['type'] == 'click':
                    x = int(step_data['x_var'].get())
                    y = int(step_data['y_var'].get())
                    self.click_sequence.append(('click', (x, y), delay, repeat))
                else:  # key
                    key = step_data['key_var'].get().strip().lower()
                    if key:
                        self.click_sequence.append(('key', key, delay, repeat))
            except ValueError:
                pass  # Skip invalid entries
    
    def get_seq_position(self):
        """Get current cursor position for sequence (legacy - not used with new UI)"""
        pass
    
    def add_to_sequence(self):
        """Add action to sequence (legacy - not used with new UI)"""
        pass
    
    def remove_from_sequence(self):
        """Remove selected item from sequence (legacy - not used with new UI)"""
        pass
    
    def clear_sequence(self):
        """Clear all sequence items"""
        self.click_sequence.clear()
        for step_data in self.step_widgets:
            step_data['frame'].destroy()
        self.step_widgets.clear()
    
    def refresh_sequence_display(self):
        """Refresh the sequence display (legacy - not used with new UI)"""
        pass
    
    def save_sequence(self):
        """Save current sequence to a JSON file"""
        if not self.step_widgets:
            messagebox.showwarning("Nothing to Save", "No sequence to save!")
            return
        
        # Rebuild sequence to get latest values
        self.rebuild_sequence()
        
        if not self.click_sequence:
            messagebox.showwarning("Nothing to Save", "Sequence is empty!")
            return
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Sequence"
        )
        
        if not file_path:
            return
        
        try:
            # Convert sequence to serializable format
            sequence_data = []
            for action_type, data, delay in self.click_sequence:
                if action_type == 'click':
                    sequence_data.append({
                        'type': 'click',
                        'x': data[0],
                        'y': data[1],
                        'delay': delay
                    })
                else:  # key
                    sequence_data.append({
                        'type': 'key',
                        'key': data,
                        'delay': delay
                    })
            
            with open(file_path, 'w') as f:
                json.dump(sequence_data, f, indent=2)
            
            messagebox.showinfo("Saved", f"Sequence saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sequence:\n{str(e)}")
    
    def load_sequence(self):
        """Load sequence from a JSON file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Sequence"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                sequence_data = json.load(f)
            
            # Clear existing sequence
            self.clear_sequence()
            
            # Load each step
            for step in sequence_data:
                if step['type'] == 'click':
                    self.add_step_ui('click')
                    widget = self.step_widgets[-1]
                    widget['x_var'].set(str(step['x']))
                    widget['y_var'].set(str(step['y']))
                    widget['delay_var'].set(str(step['delay']))
                elif step['type'] == 'key':
                    self.add_step_ui('key')
                    widget = self.step_widgets[-1]
                    widget['key_var'].set(step['key'])
                    widget['delay_var'].set(str(step['delay']))
            
            # Rebuild the sequence
            self.rebuild_sequence()
            
            messagebox.showinfo("Loaded", f"Sequence loaded from:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sequence:\n{str(e)}")
    
    def set_current_position(self):
        """Set current cursor position as fixed position relative to window"""
        hwnd = self.get_selected_window_hwnd()
        if not hwnd:
            messagebox.showerror("Error", "Please select a window first!")
            return
        
        # Bring target window to front
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass
        
        # Give user time to position cursor
        def capture_after_delay():
            time.sleep(0.5)
            cursor_pos = win32gui.GetCursorPos()
            rect = win32gui.GetWindowRect(hwnd)
            rel_x = cursor_pos[0] - rect[0]
            rel_y = cursor_pos[1] - rect[1]
            
            self.x_var.set(str(rel_x))
            self.y_var.set(str(rel_y))
            self.root.after(0, lambda: messagebox.showinfo("Position Set", f"Window-relative position set to: ({rel_x}, {rel_y})\nScreen position was: ({cursor_pos[0]}, {cursor_pos[1]})"))
            # Bring auto-clicker back to front
            self.root.after(0, lambda: self.root.attributes('-topmost', True))
        
        # Temporarily disable topmost to allow target window to come forward
        self.root.attributes('-topmost', False)
        messagebox.showinfo("Get Position", "Target window will come to front.\nMove your cursor to the desired position.\nPosition will be captured in 3 seconds...")
        
        threading.Thread(target=capture_after_delay, daemon=True).start()
    
    def setup_hotkey(self):
        """Setup F6 hotkey listener"""
        print("Setting up hotkey listener...")  # Debug
        
        # Track last toggle time to prevent double-triggering
        self.last_toggle_time = 0
        
        # Use suppress=False to ensure keyboard events are not suppressed
        def on_press(key):
            try:
                if key == keyboard.Key.f6:
                    current_time = time.time()
                    # Prevent double-triggering within 0.3 seconds
                    if current_time - self.last_toggle_time < 0.3:
                        print(f"F6 ignored (too soon: {current_time - self.last_toggle_time:.2f}s)")
                        return True
                    
                    self.last_toggle_time = current_time
                    print("F6 detected! Toggling...")  # Debug output
                    # Schedule toggle on main thread
                    self.root.after(0, self.toggle_clicking)
                    return True  # Don't suppress the key
            except Exception as e:
                print(f"Hotkey error: {e}")
        
        # Start listener without suppressing keys
        self.listener = keyboard.Listener(on_press=on_press, suppress=False)
        self.listener.start()
        print(f"Keyboard listener started: {self.listener.running}")  # Debug output
    
    def toggle_clicking(self):
        """Toggle clicking on/off - called by hotkey"""
        print(f"Toggle called. Currently clicking: {self.clicking}")  # Debug output
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()
    
    def get_selected_window_hwnd(self):
        """Get HWND of selected window"""
        selection = self.window_combo.current()
        if selection >= 0:
            return self.window_list[selection][1]
        return None
    
    def is_window_valid(self, hwnd):
        """Check if window still exists and is visible"""
        try:
            return win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)
        except:
            return False
    
    def send_physical_click(self, x, y, button='left', double=False):
        """Physically move mouse and click (works with Roblox)"""
        try:
            # Disable pyautogui failsafe temporarily
            original_failsafe = pyautogui.FAILSAFE
            pyautogui.FAILSAFE = False
            
            # Get current position and move with slight wiggle to trigger hover
            current_x, current_y = pyautogui.position()
            print(f"Moving from ({current_x}, {current_y}) to ({x}, {y})")
            
            # Move to slightly offset position first
            pyautogui.moveTo(x - 3, y - 3, duration=0.15)
            time.sleep(0.1)
            
            # Move to exact position
            pyautogui.moveTo(x, y, duration=0.15)
            time.sleep(0.5)  # Hover for 500ms
            
            # Verify position
            final_x, final_y = pyautogui.position()
            print(f"Mouse at ({final_x}, {final_y}) before click")
            
            # Click
            if double:
                pyautogui.doubleClick(button=button)
            else:
                pyautogui.click(button=button)
            
            # Restore failsafe
            pyautogui.FAILSAFE = original_failsafe
            return True
        except Exception as e:
            print(f"Error sending physical click: {e}")
            pyautogui.FAILSAFE = original_failsafe
            return False
    
    def send_click_to_window(self, hwnd, x, y, button='left', double=False):
        """Send click directly to window without bringing it to front"""
        try:
            # Convert screen coordinates to client coordinates
            rect = win32gui.GetWindowRect(hwnd)
            client_x = x - rect[0]
            client_y = y - rect[1]
            
            # Create lparam with x and y coordinates
            lparam = win32api.MAKELONG(client_x, client_y)
            
            # Determine message types based on button
            if button == 'left':
                down_msg = win32con.WM_LBUTTONDOWN
                up_msg = win32con.WM_LBUTTONUP
                wparam = win32con.MK_LBUTTON
            elif button == 'right':
                down_msg = win32con.WM_RBUTTONDOWN
                up_msg = win32con.WM_RBUTTONUP
                wparam = win32con.MK_RBUTTON
            elif button == 'middle':
                down_msg = win32con.WM_MBUTTONDOWN
                up_msg = win32con.WM_MBUTTONUP
                wparam = win32con.MK_MBUTTON
            else:
                return False
            
            # Try SendMessage first (more forceful than PostMessage)
            try:
                win32api.SendMessage(hwnd, down_msg, wparam, lparam)
                time.sleep(0.05)
                win32api.SendMessage(hwnd, up_msg, 0, lparam)
                
                if double:
                    time.sleep(0.05)
                    win32api.SendMessage(hwnd, down_msg, wparam, lparam)
                    time.sleep(0.05)
                    win32api.SendMessage(hwnd, up_msg, 0, lparam)
            except:
                # Fallback to PostMessage if SendMessage fails
                win32api.PostMessage(hwnd, down_msg, wparam, lparam)
                time.sleep(0.05)
                win32api.PostMessage(hwnd, up_msg, 0, lparam)
                
                if double:
                    time.sleep(0.05)
                    win32api.PostMessage(hwnd, down_msg, wparam, lparam)
                    time.sleep(0.05)
                    win32api.PostMessage(hwnd, up_msg, 0, lparam)
                
            return True
        except Exception as e:
            print(f"Error sending click: {e}")
            return False
    
    def send_physical_key(self, key):
        """Physically press key (works with Roblox)"""
        try:
            # Map common key names
            key_map = {
                'space': 'space',
                'enter': 'enter',
                'return': 'enter',
                'tab': 'tab',
                'esc': 'esc',
                'escape': 'esc',
                'shift': 'shift',
                'ctrl': 'ctrl',
                'alt': 'alt',
                'backspace': 'backspace',
                'delete': 'delete',
                'up': 'up',
                'down': 'down',
                'left': 'left',
                'right': 'right',
            }
            
            key_to_press = key_map.get(key.lower(), key.lower())
            print(f"Pressing key: '{key_to_press}'")  # Debug
            
            # Use pyautogui with a small hold duration for better detection
            pyautogui.press(key_to_press, interval=0.1)
            time.sleep(0.1)  # Small delay after key press
            
            return True
        except Exception as e:
            print(f"Error sending physical key: {e}")
            return False
    
    def send_key_to_window(self, hwnd, key):
        """Send keyboard key press to window"""
        try:
            # Map common key names to virtual key codes
            key_map = {
                'space': win32con.VK_SPACE,
                'enter': win32con.VK_RETURN,
                'return': win32con.VK_RETURN,
                'tab': win32con.VK_TAB,
                'esc': win32con.VK_ESCAPE,
                'escape': win32con.VK_ESCAPE,
                'shift': win32con.VK_SHIFT,
                'ctrl': win32con.VK_CONTROL,
                'alt': win32con.VK_MENU,
                'backspace': win32con.VK_BACK,
                'delete': win32con.VK_DELETE,
                'up': win32con.VK_UP,
                'down': win32con.VK_DOWN,
                'left': win32con.VK_LEFT,
                'right': win32con.VK_RIGHT,
            }
            
            # Get virtual key code
            if key.lower() in key_map:
                vk_code = key_map[key.lower()]
            elif len(key) == 1:
                # Single character - convert to uppercase for VK code
                vk_code = ord(key.upper())
            else:
                print(f"Unknown key: {key}")
                return False
            
            # Try SendMessage first (more forceful)
            try:
                win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                time.sleep(0.05)
                win32api.SendMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
            except:
                # Fallback to PostMessage
                win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
                time.sleep(0.05)
                win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)
            
            return True
        except Exception as e:
            print(f"Error sending key: {e}")
            return False
    
    def click_in_window(self):
        """Perform clicking in the target window"""
        mode = self.position_mode_var.get()
        print(f"click_in_window started. Mode: {mode}")  # Debug
        print(f"Sequence length: {len(self.click_sequence)}")  # Debug
        
        # Handle different clicking modes
        if mode == "Click Sequence":
            if not self.click_sequence:
                print("Sequence is empty!")  # Debug
                self.root.after(0, lambda: messagebox.showerror("Error", "Sequence is empty! Add clicks first."))
                self.root.after(0, self.stop_clicking)
                return
            print(f"Starting sequence loop with {len(self.click_sequence)} steps")  # Debug
            self.click_sequence_loop()
        else:
            print("Starting single position clicking")  # Debug
            self.click_single_position()
    
    def click_sequence_loop(self):
        """Execute click sequence repeatedly"""
        print("click_sequence_loop started")  # Debug
        print(f"self.clicking = {self.clicking}")  # Debug
        print(f"self.target_hwnd = {self.target_hwnd}")  # Debug
        
        # If keeping window active, bring it to foreground once at start
        if self.keep_window_active_var.get():
            try:
                win32gui.ShowWindow(self.target_hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.target_hwnd)
                time.sleep(0.5)  # Give it time to come to front
                print("Target window brought to foreground")
            except Exception as e:
                print(f"Could not bring window to foreground: {e}")
        
        button_map = {
            'Left': 'left',
            'Right': 'right',
            'Middle': 'middle'
        }
        button = button_map.get(self.button_var.get(), 'left')
        is_double = self.click_type_var.get() == 'Double'
        
        cycle_count = 0
        print(f"Entering while loop. self.clicking = {self.clicking}")  # Debug
        while self.clicking:
            print(f"Inside while loop, iteration {cycle_count + 1}")  # Debug
            
            # Check if window is valid
            is_valid = self.is_window_valid(self.target_hwnd)
            print(f"Window valid: {is_valid}")  # Debug
            
            if not is_valid:
                print("Target window invalid!")  # Debug
                self.root.after(0, lambda: self.status_var.set("Status: Window closed!"))
                self.root.after(0, self.stop_clicking)
                break
            
            # Keep window in foreground if option is enabled
            if self.keep_window_active_var.get() and cycle_count > 0:
                try:
                    # Check if window lost focus and restore it
                    foreground = win32gui.GetForegroundWindow()
                    if foreground != self.target_hwnd:
                        win32gui.SetForegroundWindow(self.target_hwnd)
                        time.sleep(0.1)
                except:
                    pass
            
            cycle_count += 1
            print(f"Starting cycle {cycle_count}")  # Debug
            for step_num, step_tuple in enumerate(self.click_sequence, 1):
                if not self.clicking:
                    print("Clicking stopped mid-sequence")  # Debug
                    break
                
                # Unpack with default repeat of 1 for backward compatibility
                if len(step_tuple) == 4:
                    action_type, data, delay, repeat = step_tuple
                else:
                    action_type, data, delay = step_tuple
                    repeat = 1
                
                try:
                    use_physical = self.click_method_var.get() == "Physical"
                    
                    # Repeat the action the specified number of times
                    for rep in range(repeat):
                        if not self.clicking:
                            break
                        
                        if action_type == 'click':
                            x, y = data
                            rep_msg = f" (repeat {rep+1}/{repeat})" if repeat > 1 else ""
                            print(f"Cycle {cycle_count}, Step {step_num}: Clicking at ({x}, {y}){rep_msg}")  # Debug
                            # Get window position
                            rect = win32gui.GetWindowRect(self.target_hwnd)
                            
                            # Calculate absolute screen position
                            click_x = rect[0] + x
                            click_y = rect[1] + y
                            
                            # Send click using selected method
                            if use_physical:
                                success = self.send_physical_click(click_x, click_y, button, is_double)
                            else:
                                success = self.send_click_to_window(self.target_hwnd, click_x, click_y, button, is_double)
                            
                            if success:
                                print(f"Click sent successfully")  # Debug
                                self.root.after(0, lambda c=cycle_count, s=step_num: 
                                              self.status_var.set(f"Status: Cycle {c} - Step {s}/{len(self.click_sequence)}"))
                            else:
                                print("Click failed")  # Debug
                            
                            # Small delay between repeats
                            if rep < repeat - 1:
                                time.sleep(0.2)
                        
                        elif action_type == 'key':
                            rep_msg = f" (repeat {rep+1}/{repeat})" if repeat > 1 else ""
                            print(f"Cycle {cycle_count}, Step {step_num}: Pressing key '{data}'{rep_msg}")  # Debug
                            # Send key press using selected method
                            if use_physical:
                                # For physical mode, try multiple methods for better Roblox compatibility
                                try:
                                    # Method 1: Direct keyDown/keyUp with hold
                                    pyautogui.keyDown(data)
                                    time.sleep(0.15)  # Hold the key
                                    pyautogui.keyUp(data)
                                    success = True
                                    print(f"Key sent via keyDown/keyUp")  # Debug
                                except:
                                    # Fallback to press
                                    success = self.send_physical_key(data)
                            else:
                                success = self.send_key_to_window(self.target_hwnd, data)
                            
                            if success:
                                print(f"Key sent successfully")  # Debug
                                self.root.after(0, lambda c=cycle_count, s=step_num, k=data: 
                                              self.status_var.set(f"Status: Cycle {c} - Step {s}/{len(self.click_sequence)} (Key '{k}')"))
                            else:
                                print("Key press failed")  # Debug
                            
                            # Small delay between repeats
                            if rep < repeat - 1:
                                time.sleep(0.2)
                    
                    # Wait for specified delay
                    print(f"Waiting {delay} seconds")  # Debug
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"Sequence error: {e}")  # Debug
        
        print(f"Exited while loop. self.clicking = {self.clicking}")  # Debug
        print("click_sequence_loop ended")  # Debug
    
    def click_single_position(self):
        """Perform clicking at a single position (original behavior)"""
        try:
            interval = float(self.interval_var.get())
        except ValueError:
            interval = 1.0
        
        button_map = {
            'Left': 'left',
            'Right': 'right',
            'Middle': 'middle'
        }
        button = button_map.get(self.button_var.get(), 'left')
        is_double = self.click_type_var.get() == 'Double'
        use_fixed_pos = self.position_mode_var.get() == 'Single Position'
        
        if use_fixed_pos:
            try:
                fixed_x = int(self.x_var.get())
                fixed_y = int(self.y_var.get())
            except ValueError:
                fixed_x, fixed_y = 100, 100
        
        # Store initial position if using current cursor mode
        if not use_fixed_pos:
            # Get cursor position when clicking starts
            cursor_pos = win32gui.GetCursorPos()
            rect = win32gui.GetWindowRect(self.target_hwnd)
            # Convert to window-relative coordinates
            fixed_x = cursor_pos[0] - rect[0]
            fixed_y = cursor_pos[1] - rect[1]
        
        click_count = 0
        while self.clicking:
            if not self.is_window_valid(self.target_hwnd):
                self.root.after(0, lambda: self.status_var.set("Status: Window closed!"))
                self.root.after(0, self.stop_clicking)
                break
            
            try:
                # Get window position (in case window moved)
                rect = win32gui.GetWindowRect(self.target_hwnd)
                
                # Calculate absolute screen position
                click_x = rect[0] + fixed_x
                click_y = rect[1] + fixed_y
                
                # Send click directly to window (works even in background)
                if self.send_click_to_window(self.target_hwnd, click_x, click_y, button, is_double):
                    click_count += 1
                    self.root.after(0, lambda c=click_count: self.status_var.set(f"Status: Clicking... ({c} clicks)"))
                
            except Exception as e:
                print(f"Click error: {e}")
            
            time.sleep(interval)
    
    def start_clicking(self):
        """Start auto-clicking"""
        print(f"start_clicking called. clicking={self.clicking}")  # Debug
        if self.clicking:
            print("Already clicking, returning")  # Debug
            return
        
        hwnd = self.get_selected_window_hwnd()
        if not hwnd:
            print("No window selected")  # Debug
            messagebox.showerror("Error", "Please select a window first!")
            return
        
        if not self.is_window_valid(hwnd):
            print("Window not valid")  # Debug
            messagebox.showerror("Error", "Selected window is not valid!")
            return
        
        # Rebuild sequence from UI before starting
        if self.position_mode_var.get() == "Click Sequence":
            print("Rebuilding sequence")  # Debug
            self.rebuild_sequence()
            if not self.click_sequence:
                print("Sequence is empty!")  # Debug
                messagebox.showerror("Error", "Sequence is empty! Add steps first.")
                return
        
        print("Starting clicking thread")  # Debug
        self.target_hwnd = hwnd
        self.clicking = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_var.set("Status: Clicking...")
        
        self.click_thread = threading.Thread(target=self.click_in_window, daemon=True)
        self.click_thread.start()
        print("Click thread started")  # Debug
    
    def stop_clicking(self):
        """Stop auto-clicking"""
        print(f"stop_clicking called. clicking={self.clicking}")  # Debug
        if not self.clicking:
            print("Not clicking, returning")  # Debug
            return
        
        print("Stopping clicks")  # Debug
        self.clicking = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("Status: Stopped")
        print("Stopped")  # Debug
    
    def on_closing(self):
        """Clean up when closing"""
        self.stop_clicking()
        if self.listener:
            self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
