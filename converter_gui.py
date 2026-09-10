#!/usr/bin/env python3
"""
GUI for audio converter
Provides user-friendly interface for format conversion
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
from converter import AudioConverter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConverterGUI:
    """GUI Application for Audio Conversion"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        self.converter = AudioConverter()
        self.processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎵 Audio Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Input file selection
        ttk.Label(main_frame, text="Input Audio File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_file_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_file_var, 
                 width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_input).grid(row=1, column=2, padx=5)
        
        # File info
        ttk.Label(main_frame, text="File Info:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.info_text = tk.Text(main_frame, height=4, width=70, state='disabled')
        self.info_text.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Output format selection
        ttk.Label(main_frame, text="Output Format:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value='mp3')
        format_combo = ttk.Combobox(main_frame, textvariable=self.format_var,
                                   values=['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'],
                                   state='readonly', width=30)
        format_combo.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Bitrate selection (for MP3)
        ttk.Label(main_frame, text="Bitrate (for MP3):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.bitrate_var = tk.StringVar(value='320k')
        bitrate_combo = ttk.Combobox(main_frame, textvariable=self.bitrate_var,
                                    values=['128k', '192k', '256k', '320k'],
                                    state='readonly', width=30)
        bitrate_combo.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_dir_var, 
                 width=50).grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", 
                  command=self.browse_output).grid(row=5, column=2, padx=5)
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', 
                                       length=400)
        self.progress.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, 
                 foreground='blue').grid(row=7, column=0, columnspan=3, pady=5)
        
        # Log
        ttk.Label(main_frame, text="Processing Log:").grid(row=8, column=0, sticky=tk.W, pady=5)
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=8, width=70, 
                               yscrollcommand=scrollbar.set, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Convert", 
                  command=self.convert).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Get File Info", 
                  command=self.get_file_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(9, weight=1)
    
    def browse_input(self):
        """Browse for input file"""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
                      ("All Files", "*.*")]
        )
        if file_path:
            self.input_file_var.set(file_path)
            self.log(f"Selected: {Path(file_path).name}")
            self.get_file_info()
    
    def browse_output(self):
        """Browse for output directory"""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir_var.set(dir_path)
            self.log(f"Output directory: {dir_path}")
    
    def get_file_info(self):
        """Get and display file information"""
        input_file = self.input_file_var.get()
        
        if not input_file:
            return
        
        try:
            info = self.converter.get_audio_info(input_file)
            
            self.info_text.config(state='normal')
            self.info_text.delete(1.0, tk.END)
            
            info_str = f"Duration: {info['duration']} | Channels: {info['channels']} | "
            info_str += f"Sample Rate: {info['sample_rate']} Hz | Size: {info['size_mb']} MB"
            
            self.info_text.insert(1.0, info_str)
            self.info_text.config(state='disabled')
        
        except Exception as e:
            self.log(f"Error getting file info: {str(e)}")
    
    def convert(self):
        """Convert audio file"""
        input_file = self.input_file_var.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return
        
        if not Path(input_file).exists():
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        output_format = self.format_var.get()
        output_dir = self.output_dir_var.get() or None
        bitrate = self.bitrate_var.get()
        
        # Start conversion in separate thread
        thread = threading.Thread(
            target=self._convert_thread,
            args=(input_file, output_format, output_dir, bitrate)
        )
        thread.daemon = True
        thread.start()
    
    def _convert_thread(self, input_file, output_format, output_dir, bitrate):
        """Conversion thread"""
        try:
            self.processing = True
            self.progress.start()
            self.status_var.set("Converting...")
            
            self.log(f"Converting: {Path(input_file).name}")
            self.log(f"Format: {Path(input_file).suffix} → .{output_format}")
            self.log(f"Bitrate: {bitrate}")
            
            result = self.converter.convert(input_file, output_format, output_dir, bitrate)
            
            self.log(f"✓ Conversion completed!")
            self.log(f"Output: {Path(result).name}")
            
            self.status_var.set("✓ Completed successfully")
            messagebox.showinfo("Success", 
                              f"Conversion completed!\n\nOutput: {result}")
        
        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            self.status_var.set("✗ Error occurred")
            messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.processing = False
    
    def log(self, message):
        """Add message to log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')


def main():
    """Run the converter GUI"""
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
