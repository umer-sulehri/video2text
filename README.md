# Media Converter

A web application that allows you to convert between different media formats using OpenAI's API:
- Video to Audio
- Audio to Text
- Video to Text

## Features
- Modern and responsive web interface
- Drag and drop file upload
- Support for multiple video formats (MP4, AVI, MOV)
- Support for multiple audio formats (WAV, MP3)
- Real-time conversion status
- Download converted files
- Error handling and user feedback

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

5. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Select the conversion type from the dropdown menu
2. Upload your file by either:
   - Dragging and dropping it into the upload area
   - Clicking the "Choose File" button
3. Click the "Convert" button
4. Wait for the conversion to complete
5. Download the converted file using the download button

## Requirements
- Python 3.7 or higher
- Internet connection (for API calls)
- Sufficient disk space for temporary files
- OpenAI API key

## Note
The application uses OpenAI's API for processing. Make sure you have a valid API key configured in the `.env` file. 