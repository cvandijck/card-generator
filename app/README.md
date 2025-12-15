# Card Generator Streamlit App

This is a Streamlit web application for generating personalized holiday cards using AI.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have your Google Gemini API key configured. Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_api_key_here
```

## Running the App

To run the Streamlit app:

```bash
streamlit run app/app.py
```

Or from the app directory:

```bash
cd app
streamlit run app.py
```

The app will open in your default web browser at http://localhost:8501

## Features

- **Upload Family Photos**: Upload multiple family member photos
- **Customize Names & Descriptions**: Add names and descriptions for each person
- **Scene Instructions**: Describe the scene you want in your card
- **Style Customization**: Choose the artistic style (cartoon, realistic, etc.)
- **Text Overlays**: Add holiday messages and text to your card
- **AI-Enhanced Descriptions**: Optionally let AI expand profile descriptions
- **Download Generated Cards**: Save your generated cards as PNG files

## Usage

1. Choose the number of family members
2. Upload a photo for each family member
3. Add names and descriptions
4. Customize the scene, style, and overlay text
5. Click "Generate Card" and wait for AI to create your personalized card
6. Download the generated card

## Requirements

- Python 3.12+
- Google Gemini API key
- Internet connection for AI generation
