# Screen Capture to PDF

A desktop application that allows users to:
1. Select and monitor a rectangular region on their screen
2. Automatically capture screenshots when content changes
3. Save screenshots as individual images
4. Generate a PDF compilation with configurable layout (1, 2, or 4 images per page)

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

1. Click "Select Region" to define the screen area to monitor
2. Configure settings including:
   - Output directory for images
   - PDF generation options (enabled/disabled)
   - PDF layout (1, 2, or 4 images per page)
   - PDF output location
3. Click "Start" to begin monitoring
4. Click "Stop" to end monitoring and generate PDF (if enabled)

## Features

- Real-time screen region monitoring
- Automatic screenshot capture on content change
- Individual image saving
- Configurable PDF generation
- Multiple PDF layout options
- User-friendly GUI
