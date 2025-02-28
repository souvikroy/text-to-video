# Text to Video Generator

An AI-powered application that converts text descriptions into engaging videos using OpenAI for text understanding and the Text-to-Video model from Hugging Face.

## Features

- Text-based video generation
- AI-enhanced prompt generation
- Customizable video duration and quality
- Easy-to-use Streamlit interface
- Download generated videos in MP4 format

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Run the Streamlit application:
```bash
streamlit run app.py
```

## Usage

1. Enter your video description in the text area
2. Adjust advanced options if needed:
   - Video duration
   - Generation quality
3. Click "Generate Video"
4. Wait for the generation process to complete
5. Download the generated video

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- OpenAI API key
- Internet connection

## Technical Details

- Frontend: Streamlit
- Text Understanding: OpenAI GPT-4
- Video Generation: Text-to-Video MS-1.7B model
- Video Processing: MoviePy

## Note

The video generation process can be resource-intensive. Higher quality settings will take longer to generate but produce better results.
