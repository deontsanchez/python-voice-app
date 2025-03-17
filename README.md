# Text-to-Voice App using Eleven Labs

This application converts text to speech using the Eleven Labs API, providing natural-sounding voice outputs from written text.

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your Eleven Labs API key:
   ```
   ELEVEN_LABS_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## Getting an Eleven Labs API Key

1. Create an account at [Eleven Labs](https://elevenlabs.io/)
2. Navigate to your profile settings
3. Copy your API key
4. Paste it into your `.env` file

## Features

- Convert text to speech using Eleven Labs' high-quality voices
- Adjust voice settings like stability and clarity
- Save the generated audio to a file
- Simple, user-friendly interface

## Requirements

- Python 3.8+
- Internet connection (to access the Eleven Labs API)
