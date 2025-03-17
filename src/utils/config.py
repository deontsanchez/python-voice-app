import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

# Check if API key is available
if not ELEVEN_LABS_API_KEY:
    print("Warning: ELEVEN_LABS_API_KEY not found in environment variables.")
    print("Please create a .env file with your API key or set it in your environment.")

# Default voice settings
DEFAULT_STABILITY = 0.5  # Range: 0-1
DEFAULT_SIMILARITY = 0.75  # Range: 0-1

# Default output directory for saved audio files
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR) 