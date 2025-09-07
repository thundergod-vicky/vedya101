import React, { useEffect, useState } from 'react';

interface TypewriterProps {
  text: string;
  typingSpeed?: number; // Time in ms between characters
  className?: string;
  onComplete?: () => void;
}

const Typewriter: React.FC<TypewriterProps> = ({
  text,
  typingSpeed = 30,
  className = '',
  onComplete
}) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(true);
  
  // Reset state when text prop changes completely
  useEffect(() => {
    if (!text.startsWith(displayText)) {
      setDisplayText('');
      setCurrentIndex(0);
      setIsTyping(true);
    }
  }, [text, displayText]);

  // Handle the typing animation
  useEffect(() => {
    if (!isTyping) return;
    
    // If we've already typed everything, stop
    if (displayText === text) {
      setIsTyping(false);
      onComplete?.();
      return;
    }

    // Type the next character
    const timeout = setTimeout(() => {
      if (currentIndex < text.length) {
        setDisplayText(text.substring(0, currentIndex + 1));
        setCurrentIndex(prev => prev + 1);
      }
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [text, displayText, currentIndex, isTyping, typingSpeed, onComplete]);

  // Handle dynamic text updates during streaming
  useEffect(() => {
    // If the text is longer than what we've typed so far, update our typing position
    if (text.length > currentIndex && text.startsWith(displayText)) {
      // Continue typing from where we left off
    } else if (text !== displayText) {
      // Text changed completely, restart typing
      setDisplayText('');
      setCurrentIndex(0);
      setIsTyping(true);
    }
  }, [text, displayText, currentIndex]);

  return (
    <span className={className}>
      {displayText}
      {isTyping && <span className="cursor">|</span>}
    </span>
  );
};

export default Typewriter;
