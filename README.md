# Markdown Viewer

A modern, Windows-ready PySide6 desktop application for viewing and editing Markdown files with live preview, syntax highlighting, and zoom controls.

## Features

- **Live Preview**: Real-time Markdown to HTML conversion with debounced updates
- **Syntax Highlighting**: Code syntax highlighting using Pygments
- **Dual Pane Layout**: Optional editor panel with splitter layout
- **Zoom Controls**: Zoom in/out/reset for preview (Ctrl +/-/0)
- **File Management**: Open, save, recent files with native Windows dialogs
- **HTML Sanitization**: Optional HTML sanitization using bleach
- **Settings Persistence**: Remembers window geometry, splitter sizes, and preferences
- **High DPI Support**: Proper scaling on high-resolution displays

## Requirements

- Python 3.10+
- Windows 10/11
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
python main.py
```

Or double-click `run.bat` on Windows.

### Opening Files

- Use **File → Open** or **Ctrl+O**
- Drag and drop files onto the application
- Use **File → Open Recent** for recently opened files
- Pass file path as command line argument: `python main.py document.md`

### Editor Controls

- **F2** or **Edit button**: Toggle editor panel visibility
- **Ctrl+S**: Save current file
- **Ctrl+Shift+S**: Save as new file
- **Ctrl+N**: New file

### Preview Controls

- **Ctrl +/-/0**: Zoom in/out/reset
- **Ctrl+R**: Refresh preview
- **Mouse wheel + Ctrl**: Zoom with mouse

### View Menu

- **Toggle Editor**: Show/hide the editor panel
- **Zoom In/Out/Reset**: Preview zoom controls
- **Refresh Preview**: Force refresh the preview

### Tools Menu

- **Sanitize HTML**: Toggle HTML sanitization for security

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New File | Ctrl+N |
| Open File | Ctrl+O |
| Save File | Ctrl+S |
| Save As | Ctrl+Shift+S |
| Toggle Editor | F2 |
| Zoom In | Ctrl++ |
| Zoom Out | Ctrl+- |
| Reset Zoom | Ctrl+0 |
| Refresh Preview | Ctrl+R |
| Exit | Ctrl+Q |

## Supported Markdown Features

- Headers (H1-H6)
- **Bold** and *italic* text
- `Inline code` and code blocks with syntax highlighting
- Links and images
- Lists (ordered and unordered)
- Tables
- Blockquotes
- Horizontal rules
- Table of contents (TOC)
- Fenced code blocks

## Configuration

The application automatically saves and restores:

- Window size and position
- Splitter panel sizes
- Editor visibility state
- Recent files list (last 5 files)
- HTML sanitization preference
- Preview zoom level

Settings are stored using Qt's QSettings in the Windows registry.

## File Support

**Supported Extensions:**
- `.md` (Markdown)
- `.markdown`
- `.mdown`
- `.txt` (Plain text)

**File Encoding:**
- UTF-8 (without BOM)
- Automatic encoding detection for existing files

## Architecture

```
src/
├── main_window.py          # Main application window
├── widgets/
│   ├── markdown_editor.py  # Editor with syntax highlighting
│   └── markdown_preview.py # Preview with zoom controls
├── utils/
│   ├── logging_config.py   # Logging configuration
│   ├── settings.py         # Settings management
│   └── markdown_renderer.py # Markdown to HTML conversion
└── resources/
    ├── style.css           # Main CSS styles
    └── pygments.css        # Syntax highlighting styles
```

## Dependencies

- **PySide6**: Qt6 GUI framework
- **Markdown**: Python Markdown processor
- **Pygments**: Syntax highlighting
- **bleach**: HTML sanitization

## License

This project is provided as-is for educational and personal use.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
2. **Font Issues**: The application uses system fonts; ensure proper font rendering support
3. **High DPI Issues**: The application includes High DPI support for modern displays
4. **File Encoding**: Files are saved as UTF-8 without BOM for maximum compatibility

### Logging

The application logs to both console and rotating log files in the `logs/` directory. Check `logs/markdown_viewer.log` for detailed error information.

### Performance

- Large files (>1MB) may experience slower preview updates
- Use **Ctrl+R** for manual refresh if needed
- Debounced updates prevent excessive rendering during typing
