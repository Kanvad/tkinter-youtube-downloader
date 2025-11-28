#!/usr/bin/env python3
"""
YouTube Downloader Application
A robust GUI application for downloading YouTube videos using yt-dlp.

Features:
- Download videos in MP4 or MP3 format
- Real-time progress tracking
- Thumbnail preview
- Threading to keep GUI responsive
- Comprehensive error handling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont
import threading
import os
import sys
import shutil
import re
from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import URLError
from datetime import datetime
import json

try:
    import yt_dlp
except ImportError:
    print("ERROR: yt-dlp is not installed.")
    print("Please install it using: pip install yt-dlp")
    sys.exit(1)

try:
    from PIL import Image, ImageTk
except ImportError:
    print("ERROR: Pillow is not installed.")
    print("Please install it using: pip install Pillow")
    sys.exit(1)


class YouTubeDownloader:
    """Main application class for YouTube Downloader."""

    def __init__(self, root):
        """Initialize the YouTube Downloader application.

        Args:
            root: The main Tkinter window
        """
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("950x420")  # CÓ THỂ THAY ĐỔI - You can change window size (width x height) | Có thể điều chỉnh kích thước cửa sổ (chiều rộng x chiều cao)
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(850, 420)  # CÓ THỂ THAY ĐỔI - Minimum window size | Kích thước tối thiểu của cửa sổ


        # Variables
        self.url_var = tk.StringVar()
        self.directory_var = tk.StringVar(
            value=str(Path.home() / "Downloads")
        )
        self.format_var = tk.StringVar(value="mp4")
        self.progress_var = tk.DoubleVar()
        self.progress_label_var = tk.StringVar(value="0%")

        # Thumbnail
        self.thumbnail_label = None
        self.thumbnail_path = None
        self.video_title = None  # Store video title for thumbnail filename

        # Download state
        self.is_downloading = False
        
        # Setup colors and styles
        self.setup_styles()

        # Create GUI
        self.create_widgets()
    
    def setup_styles(self):
        """Setup color scheme and custom styles for the application."""
        # Color Palette - Modern and Eye-catching
        self.colors = {
            'primary': '#2196F3',      # Blue
            'primary_dark': '#1976D2',  # Dark Blue
            'primary_light': '#BBDEFB', # Light Blue
            'success': '#4CAF50',       # Green
            'success_dark': '#388E3C',  # Dark Green
            'warning': '#FF9800',       # Orange
            'danger': '#F44336',        # Red
            'bg_main': '#F5F7FA',       # Light Gray Background
            'bg_card': '#FFFFFF',       # White
            'text_primary': '#212121',  # Almost Black
            'text_secondary': '#757575', # Gray
            'border': '#E0E0E0',        # Light Border
            'accent': '#FF5722',        # Deep Orange Accent
        }
        
        # Configure main window
        self.root.configure(bg=self.colors['bg_main'])
        
        # Setup ttk Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure TFrame
        self.style.configure('TFrame', background=self.colors['bg_main'])
        self.style.configure('Card.TFrame', background=self.colors['bg_card'], 
                            relief='flat', borderwidth=0)
        
        # Configure TLabelframe
        self.style.configure('TLabelframe', 
                            background=self.colors['bg_main'],
                            bordercolor=self.colors['border'],
                            borderwidth=2,
                            relief='solid')
        self.style.configure('TLabelframe.Label', 
                            background=self.colors['bg_main'],
                            foreground=self.colors['primary'],
                            font=('Helvetica', 12, 'bold'))
        
        # Configure TLabel
        self.style.configure('TLabel', 
                            background=self.colors['bg_main'],
                            foreground=self.colors['text_primary'])
        self.style.configure('Title.TLabel',
                            background=self.colors['bg_main'],
                            foreground=self.colors['primary'],
                            font=('Helvetica', 24, 'bold'))
        
        # Configure TEntry
        self.style.configure('TEntry',
                            fieldbackground='white',
                            foreground=self.colors['text_primary'],
                            bordercolor=self.colors['border'],
                            lightcolor=self.colors['primary_light'],
                            darkcolor=self.colors['primary'])
        
        # Configure TButton - Default
        self.style.configure('TButton',
                            background=self.colors['bg_card'],
                            foreground=self.colors['text_primary'],
                            bordercolor=self.colors['border'],
                            borderwidth=1,
                            relief='flat',
                            font=('Helvetica', 11))
        self.style.map('TButton',
                      background=[('active', self.colors['primary_light']),
                                ('pressed', self.colors['primary'])],
                      foreground=[('active', self.colors['primary_dark'])])
        
        # Primary Button Style (Download button)
        self.style.configure('Primary.TButton',
                            background=self.colors['primary'],
                            foreground='white',
                            borderwidth=0,
                            relief='flat',
                            font=('Helvetica', 12, 'bold'),
                            padding=(20, 10))
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['primary_dark']),
                                ('pressed', self.colors['primary_dark']),
                                ('disabled', self.colors['text_secondary'])],
                      foreground=[('disabled', 'white')])
        
        # Success Button Style (Save thumbnail)
        self.style.configure('Success.TButton',
                            background=self.colors['success'],
                            foreground='white',
                            borderwidth=0,
                            relief='flat',
                            font=('Helvetica', 11, 'bold'),
                            padding=(10, 5))
        self.style.map('Success.TButton',
                      background=[('active', self.colors['success_dark']),
                                ('pressed', self.colors['success_dark']),
                                ('disabled', self.colors['text_secondary'])],
                      foreground=[('disabled', 'white')])
        
        # Configure Progressbar
        self.style.configure('Custom.Horizontal.TProgressbar',
                            troughcolor=self.colors['bg_card'],
                            bordercolor=self.colors['border'],
                            background=self.colors['primary'],
                            lightcolor=self.colors['primary'],
                            darkcolor=self.colors['primary_dark'],
                            thickness=25)
        
        # Configure Radiobutton
        self.style.configure('TRadiobutton',
                            background=self.colors['bg_main'],
                            foreground=self.colors['text_primary'],
                            font=('Helvetica', 11))
        self.style.map('TRadiobutton',
                      background=[('active', self.colors['bg_main'])],
                      foreground=[('active', self.colors['primary'])])
        
        # Configure Separator
        self.style.configure('TSeparator',
                            background=self.colors['border'])

    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Configure grid weights for main_frame - 2 columns layout
        main_frame.columnconfigure(0, weight=1, uniform="columns")  # Left column (controls) - 50% width | Cột trái chiếm 50%
        main_frame.columnconfigure(1, weight=1, uniform="columns")  # Right column (preview) - 50% width | Cột phải chiếm 50% - CÓ THỂ THAY ĐỔI weight để điều chỉnh tỷ lệ
        main_frame.rowconfigure(2, weight=1)     # Logs area can expand

        row = 0

        # ==================== HEADER ====================
        # Gradient Title using Canvas
        canvas_width = 920
        title_canvas = tk.Canvas(
            main_frame, 
            width=canvas_width, 
            height=40, 
            bg=self.colors['bg_main'], 
            highlightthickness=0
        )
        title_canvas.grid(row=row, column=0, columnspan=2, pady=(0, 10))
        
        text = "YouTube Downloader"
        font_family = "Helvetica"
        font_size = 22
        font_weight = "bold"
        tk_font = tkfont.Font(family=font_family, size=font_size, weight=font_weight)
        
        # Calculate total width for centering
        total_width = sum(tk_font.measure(char) for char in text)
        start_x = (canvas_width - total_width) // 2
        
        # Gradient Colors (RGB)
        c1 = (33, 150, 243)  # Blue #2196F3
        c2 = (244, 67, 54)   # Red #F44336
        
        current_x = start_x
        for i, char in enumerate(text):
            # Interpolate color
            t = i / (len(text) - 1)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            title_canvas.create_text(
                current_x, 22, 
                text=char, 
                font=(font_family, font_size, font_weight), 
                fill=color, 
                anchor="w"
            )
            current_x += tk_font.measure(char)
            
        row += 1

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15)
        )
        row += 1

        # ==================== LEFT COLUMN: INPUT SECTION ====================
        input_section = ttk.LabelFrame(
            main_frame, text="📥 Video Information", padding="15"
        )
        input_section.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10), padx=(0, 10))
        input_section.columnconfigure(1, weight=1)

        # URL Input
        ttk.Label(input_section, text="YouTube URL:", font=("Helvetica", 11, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10), padx=(0, 10)
        )
        url_entry = ttk.Entry(
            input_section, textvariable=self.url_var, font=("Helvetica", 11)
        )
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Paste Button
        paste_btn = ttk.Button(
            input_section, text="📋", width=3,
            command=lambda: self.url_var.set(self.root.clipboard_get())
        )
        paste_btn.grid(row=0, column=2, padx=(5, 0), pady=(0, 10))

        # Fetch Thumbnail Button
        fetch_thumb_btn = ttk.Button(
            input_section,
            text="🔍 Fetch Info",
            command=self.fetch_thumbnail_threaded,
            width=15
        )
        fetch_thumb_btn.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        # Directory Selection
        ttk.Label(input_section, text="Save To:", font=("Helvetica", 11, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 10), padx=(0, 10)
        )
        dir_entry = ttk.Entry(
            input_section, textvariable=self.directory_var, font=("Helvetica", 11)
        )
        dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        browse_btn = ttk.Button(
            input_section, text="📁 Browse", command=self.browse_directory, width=9
        )
        browse_btn.grid(row=2, column=2, padx=(5, 0), pady=(0, 10))

        # Format Selection
        ttk.Label(input_section, text="Format:", font=("Helvetica", 11, "bold")).grid(
            row=3, column=0, sticky=tk.W, padx=(0, 10)
        )
        format_container = ttk.Frame(input_section)
        format_container.grid(row=3, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Radiobutton(
            format_container,
            text="🎬 MP4",
            variable=self.format_var,
            value="mp4"
        ).pack(side=tk.LEFT, padx=(0, 20))

        ttk.Radiobutton(
            format_container,
            text="🎵 MP3",
            variable=self.format_var,
            value="mp3"
        ).pack(side=tk.LEFT)

        # Download Button (centered)
        button_frame = ttk.Frame(input_section)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(15, 0))
        
        self.download_btn = ttk.Button(
            button_frame,
            text="Start Download",
            command=self.start_download,
            width=30,
            style='Primary.TButton'
        )
        self.download_btn.pack()


        # ==================== RIGHT COLUMN: THUMBNAIL SECTION ====================
        thumbnail_frame = ttk.LabelFrame(
            main_frame, text="📺 Video Preview", padding="15"
        )
        thumbnail_frame.grid(
            row=row, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)  # CÓ THỂ THAY ĐỔI - Added tk.S to match height with input section | Thêm tk.S để chiều cao bằng nhau
        )

        # Create a fixed-size container for thumbnail
        thumbnail_container = ttk.Frame(thumbnail_frame)
        thumbnail_container.pack(fill=tk.X, pady=(0, 10))
        thumbnail_container.pack_propagate(False)  # Prevent auto-resize
        thumbnail_container.configure(height=200)  # CÓ THỂ THAY ĐỔI - Thumbnail container height | Chiều cao khung chứa thumbnail
        
        self.thumbnail_label = ttk.Label(
            thumbnail_container, 
            text="📷 Thumbnail will appear\nhere after fetching\nvideo info", 
            anchor=tk.CENTER,
            font=("Helvetica", 11),
            foreground="gray",
            justify=tk.CENTER
        )
        self.thumbnail_label.pack(fill=tk.BOTH, expand=True)
        
        # Save Thumbnail Button
        self.save_thumb_btn = ttk.Button(
            thumbnail_frame,
            text="💾 Save Thumbnail",
            command=self.save_thumbnail,
            state=tk.DISABLED,  # Disabled until thumbnail is fetched
            style='Success.TButton'
        )
        self.save_thumb_btn.pack(pady=(0, 5))


        row += 1



    def browse_directory(self):
        """Open directory selection dialog."""
        directory = filedialog.askdirectory(
            initialdir=self.directory_var.get(),
            title="Select Download Directory"
        )
        if directory:
            self.directory_var.set(directory)
            self.log_message(f"Download directory set to: {directory}")

    def log_message(self, message):
        """Add a message to the log text area.

        Args:
            message: The message to log
        """
        # Log text area is disabled/hidden
        pass


    def update_progress(self, percentage):
        """Update the progress bar and label.

        Args:
            percentage: Progress percentage (0-100)
        """
        self.progress_var.set(percentage)
        self.progress_label_var.set(f"{percentage:.1f}%")

    def validate_url(self, url):
        """Validate if the URL is a valid YouTube URL.

        Args:
            url: The URL to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not url or not url.strip():
            return False

        valid_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
        return any(domain in url.lower() for domain in valid_domains)

    def fetch_thumbnail_threaded(self):
        """Start thumbnail fetch in a separate thread."""
        if not self.validate_url(self.url_var.get()):
            messagebox.showerror(
                "Invalid URL",
                "Please enter a valid YouTube URL first."
            )
            return

        thread = threading.Thread(target=self.fetch_thumbnail, daemon=True)
        thread.start()

    def fetch_thumbnail(self):
        """Fetch and display video thumbnail."""
        url = self.url_var.get().strip()

        try:
            self.log_message("Fetching video information...")

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                thumbnail_url = info.get('thumbnail')

                if thumbnail_url:
                    self.log_message(f"Downloading thumbnail from: {thumbnail_url}")

                    # Download thumbnail to temp location
                    temp_dir = Path.home() / '.youtube_downloader_temp'
                    temp_dir.mkdir(exist_ok=True)
                    self.thumbnail_path = temp_dir / 'thumbnail.jpg'

                    urlretrieve(thumbnail_url, self.thumbnail_path)

                    # Load and display thumbnail with fixed size
                    image = Image.open(self.thumbnail_path)
                    
                    # Create a fixed-size canvas
                    canvas_width = 360  # CÓ THỂ THAY ĐỔI - Thumbnail display width | Chiều rộng hiển thị thumbnail
                    canvas_height = 200  # CÓ THỂ THAY ĐỔI - Thumbnail display height | Chiều cao hiển thị thumbnail
                    canvas = Image.new('RGB', (canvas_width, canvas_height), '#F5F7FA')
                    
                    # Resize image to fit while maintaining aspect ratio
                    image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                    
                    # Center the image on canvas
                    offset_x = (canvas_width - image.width) // 2
                    offset_y = (canvas_height - image.height) // 2
                    canvas.paste(image, (offset_x, offset_y))
                    
                    photo = ImageTk.PhotoImage(canvas)

                    # Update label with image (without changing size)
                    self.thumbnail_label.configure(image=photo, text="")
                    self.thumbnail_label.image = photo  # Keep a reference
                    
                    # Enable Save Thumbnail button
                    self.save_thumb_btn.configure(state=tk.NORMAL)
                    
                    # Store video title for thumbnail filename
                    self.video_title = info.get('title', 'Unknown')

                    self.log_message("Thumbnail loaded successfully!")
                    self.log_message(f"Video Title: {self.video_title}")
                    self.log_message(
                        f"Duration: {info.get('duration', 0) // 60} minutes"
                    )
                else:
                    self.log_message("No thumbnail available for this video.")
                    self.save_thumb_btn.configure(state=tk.DISABLED)

        except URLError as e:
            self.log_message(f"Network error while fetching thumbnail: {e}")
            self.save_thumb_btn.configure(state=tk.DISABLED)
            messagebox.showerror(
                "Network Error",
                "Could not fetch thumbnail. Check your internet connection."
            )
        except Exception as e:
            self.log_message(f"Error fetching thumbnail: {e}")
            self.save_thumb_btn.configure(state=tk.DISABLED)
            messagebox.showerror("Error", f"Failed to fetch thumbnail: {e}")

    def save_thumbnail(self):
        """Save the current thumbnail to a file automatically."""
        if not self.thumbnail_path or not os.path.exists(self.thumbnail_path):
            messagebox.showerror(
                "No Thumbnail",
                "Please fetch a thumbnail first before saving."
            )
            return

        try:
            # Get download directory
            download_dir = self.directory_var.get()
            
            # Validate directory
            if not download_dir or not os.path.exists(download_dir):
                messagebox.showerror(
                    "Invalid Directory",
                    "Download directory is not set or doesn't exist."
                )
                return
            
            # Create filename from video title (sanitize for filesystem)
            if self.video_title:
                # Remove invalid characters for filename
                safe_title = re.sub(r'[<>:"/\\|?*]', '', self.video_title)
                filename = f"{safe_title}_thumbnail.jpg"
            else:
                # Use timestamp if no title available
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"thumbnail_{timestamp}.jpg"
            
            # Full save path
            save_path = os.path.join(download_dir, filename)
            
            # Handle duplicate filenames
            counter = 1
            base_path = save_path
            while os.path.exists(save_path):
                name, ext = os.path.splitext(base_path)
                save_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # Copy thumbnail to download directory
            shutil.copy2(self.thumbnail_path, save_path)
            
            self.log_message(f"💾 Thumbnail saved to: {save_path}")
            messagebox.showinfo(
                "Success",
                f"Thumbnail saved successfully!\n\nFile: {os.path.basename(save_path)}\nLocation: {download_dir}"
            )

        except Exception as e:
            self.log_message(f"✗ Error saving thumbnail: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to save thumbnail:\n{e}"
            )

    def start_download(self):
        """Validate inputs and start download in a separate thread."""
        url = self.url_var.get().strip()
        directory = self.directory_var.get().strip()

        # Validation
        if not self.validate_url(url):
            messagebox.showerror(
                "Invalid URL",
                "Please enter a valid YouTube URL."
            )
            return

        if not directory or not os.path.exists(directory):
            messagebox.showerror(
                "Invalid Directory",
                "Please select a valid download directory."
            )
            return

        if self.is_downloading:
            messagebox.showwarning(
                "Download in Progress",
                "A download is already in progress. Please wait."
            )
            return

        # Start download in separate thread
        self.is_downloading = True
        self.download_btn.configure(state=tk.DISABLED)
        self.update_progress(0)

        download_thread = threading.Thread(
            target=self.download_video,
            args=(url, directory),
            daemon=True
        )
        download_thread.start()

    def progress_hook(self, d):
        """Hook for yt-dlp to report download progress.

        Args:
            d: Dictionary containing download status information
        """
        if d['status'] == 'downloading':
            try:
                # Calculate percentage more accurately
                downloaded_bytes = d.get('downloaded_bytes', 0)
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                if total_bytes > 0:
                    percentage = (downloaded_bytes / total_bytes) * 100
                    self.root.after(0, self.update_progress, percentage)
                else:
                    # Fallback to string parsing if bytes not available
                    percent_str = d.get('_percent_str', '0%').strip().replace('%', '')
                    percentage = float(percent_str)
                    self.root.after(0, self.update_progress, percentage)


                    
            except (ValueError, KeyError, ZeroDivisionError) as e:
                pass

        elif d['status'] == 'finished':
            self.root.after(0, self.update_progress, 100)
            self.root.after(0, self.log_message, "✓ Download finished. Processing...")

    def download_video(self, url, directory):
        """Download video using yt-dlp.

        Args:
            url: YouTube URL to download
            directory: Directory to save the downloaded file
        """
        try:
            self.log_message(f"Starting download from: {url}")
            self.log_message(f"Saving to: {directory}")

            format_choice = self.format_var.get()

            if format_choice == "mp4":
                # Best quality video with audio
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': os.path.join(directory, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'merge_output_format': 'mp4',
                }
                self.log_message("Format: MP4 (Best Quality Video)")

            else:  # mp3
                # Audio only, extract as MP3
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(directory, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                self.log_message("Format: MP3 (Audio Only)")

            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                # For MP3, the extension changes after processing
                if format_choice == "mp3":
                    filename = os.path.splitext(filename)[0] + '.mp3'

                self.log_message("=" * 50)
                self.log_message("✓ Download completed successfully!")
                self.log_message(f"File saved as: {os.path.basename(filename)}")
                self.log_message("=" * 50)

                # Show success message
                self.root.after(
                    0,
                    messagebox.showinfo,
                    "Success",
                    f"Download completed!\n\nFile: {os.path.basename(filename)}"
                )

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            self.log_message(f"✗ Download Error: {error_msg}")

            if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
                self.root.after(
                    0,
                    messagebox.showerror,
                    "FFmpeg Missing",
                    "FFmpeg is required for this operation.\n\n"
                    "Install it using:\n"
                    "- Ubuntu/Debian: sudo apt install ffmpeg\n"
                    "- macOS: brew install ffmpeg\n"
                    "- Windows: Download from ffmpeg.org"
                )
            else:
                self.root.after(
                    0,
                    messagebox.showerror,
                    "Download Error",
                    f"Failed to download video:\n{error_msg}"
                )

        except URLError as e:
            self.log_message(f"✗ Network Error: {e}")
            self.root.after(
                0,
                messagebox.showerror,
                "Network Error",
                "Could not connect to the internet.\n"
                "Please check your connection and try again."
            )

        except PermissionError as e:
            self.log_message(f"✗ Permission Error: {e}")
            self.root.after(
                0,
                messagebox.showerror,
                "Permission Error",
                f"Cannot write to directory:\n{directory}\n\n"
                "Please choose a different location."
            )

        except OSError as e:
            self.log_message(f"✗ File System Error: {e}")
            self.root.after(
                0,
                messagebox.showerror,
                "File System Error",
                f"Error accessing file system:\n{e}"
            )

        except Exception as e:
            self.log_message(f"✗ Unexpected Error: {e}")
            self.root.after(
                0,
                messagebox.showerror,
                "Error",
                f"An unexpected error occurred:\n{e}"
            )

        finally:
            # Re-enable download button
            self.is_downloading = False
            self.root.after(0, self.download_btn.configure, {'state': tk.NORMAL})


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    
    # Create app (styling will be done in __init__)
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
