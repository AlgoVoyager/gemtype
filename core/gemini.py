"""
Gemini API wrapper for GemType.
Handles all interactions with the Google Gemini API.
"""
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types

# Configure logging
logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with the Gemini API."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-preview-05-20"):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Google API key for authentication
            model: The model to use for generation
        """
        self.api_key = api_key
        self.model_name = model
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Gemini client with the API key."""
        try:
            self._client = genai.Client(api_key=self.api_key)
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Gemini client: %s", e)
            raise
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the Gemini model.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            str: The generated response text
        """
        if not self._client:
            self._initialize_client()
            
        if not self._client:
            return "❌ Error: Failed to initialize Gemini client"
            
        try:
            # Prepare the content
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                )
            ]
            
            # Set default config
            config = types.GenerateContentConfig(
                response_mime_type="text/plain",
                **kwargs
            )
            
            # Generate response
            response = self._client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # Stream and concatenate the response
            full_response = []
            for chunk in response:
                if chunk.text:
                    full_response.append(chunk.text)
            
            return "".join(full_response).strip()
            
        except Exception as e:
            logger.error("Error generating response: %s", e, exc_info=True)
            return f"❌ Error: {str(e)}"
    
    def test_connection(self) -> bool:
        """
        Test the connection to the Gemini API.
        
        Returns:
            bool: True if the connection is successful, False otherwise
        """
        try:
            # Try a simple request to test the connection
            response = self.generate_response("Say 'Hello'")
            return not response.startswith("❌")
        except Exception as e:
            logger.error("Connection test failed: %s", e)
            return False
