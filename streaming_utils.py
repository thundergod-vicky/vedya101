"""
VEDYA Platform streaming utilities for text-like streaming responses.

This module provides utilities for streaming text responses character by character
or in small chunks to create a more natural, typing-like experience similar to ChatGPT.
"""

import asyncio
import re
from typing import List, Generator, AsyncGenerator

# Punctuation delay settings (in seconds)
DELAYS = {
    "default": 0.01,      # Base delay between characters
    ".": 0.3,             # End of sentence
    "!": 0.3,             # End of exclamation
    "?": 0.3,             # End of question
    ",": 0.15,            # Comma pause
    ";": 0.2,             # Semicolon pause
    ":": 0.2,             # Colon pause
    "\n": 0.4,            # New line
    "-": 0.1,             # Dash pause
    "(": 0.1,             # Opening parenthesis
    ")": 0.1,             # Closing parenthesis
}

def chunk_text(text: str, avg_chunk_size: int = 1) -> List[str]:
    """
    Split text into small chunks for realistic streaming.
    
    Args:
        text: The text to chunk
        avg_chunk_size: Average number of characters per chunk (randomized slightly)
        
    Returns:
        List of text chunks
    """
    # For character-by-character, just return list of characters
    if avg_chunk_size == 1:
        return list(text)
    
    # Otherwise, chunk by patterns
    chunks = []
    current_chunk = ""
    
    for char in text:
        current_chunk += char
        
        # Create natural breaking points at punctuation or spaces
        if (len(current_chunk) >= avg_chunk_size and 
            (char in " .,;:!?\n" or current_chunk.endswith((" ", ".", ",", ";", ":", "!", "?", "\n")))):
            chunks.append(current_chunk)
            current_chunk = ""
    
    # Add any remaining text
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def get_delay_for_char(char: str) -> float:
    """Get the appropriate delay for a specific character based on its type."""
    return DELAYS.get(char, DELAYS["default"])

async def stream_text_chunks(text: str, character_by_character: bool = True) -> AsyncGenerator[str, None]:
    """
    Stream text in a natural, typing-like manner either character by character or in small chunks.
    
    Args:
        text: The text to stream
        character_by_character: Whether to stream character by character (True) or word by word (False)
    
    Yields:
        Text chunks with appropriate timing
    """
    if not text:
        return
        
    if character_by_character:
        # Character-by-character streaming (most ChatGPT-like)
        prev_char = None
        for char in text:
            # Calculate delay based on the previous character (for punctuation)
            delay = get_delay_for_char(prev_char) if prev_char else DELAYS["default"]
            await asyncio.sleep(delay)
            yield char
            prev_char = char
    else:
        # Word-by-word streaming (faster but less ChatGPT-like)
        words = text.split(' ')
        for i, word in enumerate(words):
            if i > 0:  # Add a space before all words except the first
                yield ' '
            yield word
            await asyncio.sleep(0.05)  # Fixed delay between words
