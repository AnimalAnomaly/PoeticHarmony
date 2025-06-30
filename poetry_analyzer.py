import re
import nltk
import spacy
from textblob import TextBlob
from collections import Counter
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

class PoetryAnalyzer:
    def __init__(self):
        self.cmudict = None
        try:
            from nltk.corpus import cmudict
            self.cmudict = cmudict.dict()
        except:
            logging.warning("CMU Pronouncing Dictionary not available. Syllable counting will be approximate.")
    
    def analyze_poem(self, poem_text):
        """
        Comprehensive analysis of poem text
        Returns dictionary with analysis results
        """
        if not poem_text.strip():
            return {"error": "Empty poem text provided"}
        
        analysis = {
            "lines": self._get_lines(poem_text),
            "syllable_counts": [],
            "total_syllables": 0,
            "line_count": 0,
            "sentiment": self._analyze_sentiment(poem_text),
            "meter": self._detect_meter(poem_text),
            "rhyme_scheme": self._detect_rhyme_scheme(poem_text),
            "literary_devices": self._detect_literary_devices(poem_text),
            "tempo_suggestion": 120,
            "key_suggestion": "C",
            "time_signature": "4/4"
        }
        
        lines = analysis["lines"]
        analysis["line_count"] = len(lines)
        
        # Analyze each line
        for line in lines:
            syllables = self._count_syllables(line)
            analysis["syllable_counts"].append(syllables)
            analysis["total_syllables"] += syllables
        
        # Generate musical suggestions based on analysis
        analysis.update(self._generate_musical_suggestions(analysis))
        
        return analysis
    
    def _get_lines(self, text):
        """Split text into lines and clean them"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines
    
    def _count_syllables(self, word):
        """Count syllables in a word using CMU dict or fallback method"""
        if not word:
            return 0
        
        # Clean the word
        word = re.sub(r'[^a-zA-Z]', '', word.lower())
        if not word:
            return 0
        
        if self.cmudict and word in self.cmudict:
            # Use CMU dictionary for accurate syllable count
            pronunciations = self.cmudict[word]
            if pronunciations:
                return len([phone for phone in pronunciations[0] if phone[-1].isdigit()])
        
        # Fallback syllable counting method
        return self._fallback_syllable_count(word)
    
    def _fallback_syllable_count(self, word):
        """Fallback method for syllable counting"""
        word = word.lower()
        vowels = "aeiouy"
        syllables = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllables += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e' at the end
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        return max(1, syllables)
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            mood = "positive"
        elif polarity < -0.1:
            mood = "negative"
        else:
            mood = "neutral"
        
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "mood": mood
        }
    
    def _detect_meter(self, text):
        """Basic meter detection based on syllable patterns"""
        lines = self._get_lines(text)
        if not lines:
            return "free_verse"
        
        syllable_counts = [self._count_syllables_in_line(line) for line in lines]
        
        # Check for common patterns
        if len(set(syllable_counts)) == 1:
            return "regular"
        elif self._is_iambic_pattern(lines):
            return "iambic"
        elif self._is_trochaic_pattern(lines):
            return "trochaic"
        else:
            return "free_verse"
    
    def _count_syllables_in_line(self, line):
        """Count total syllables in a line"""
        words = re.findall(r'\b\w+\b', line.lower())
        return sum(self._count_syllables(word) for word in words)
    
    def _is_iambic_pattern(self, lines):
        """Simple iambic pattern detection"""
        # This is a simplified check - real iambic detection would need stress analysis
        syllable_counts = [self._count_syllables_in_line(line) for line in lines]
        # Iambic pentameter has 10 syllables, iambic tetrameter has 8
        common_counts = [8, 10, 12]
        return any(count in common_counts for count in syllable_counts)
    
    def _is_trochaic_pattern(self, lines):
        """Simple trochaic pattern detection"""
        # Similar to iambic but typically shorter lines
        syllable_counts = [self._count_syllables_in_line(line) for line in lines]
        common_counts = [7, 8, 9]
        return any(count in common_counts for count in syllable_counts)
    
    def _detect_rhyme_scheme(self, text):
        """Basic rhyme scheme detection"""
        lines = self._get_lines(text)
        if len(lines) < 2:
            return "none"
        
        # Get last word of each line
        end_words = []
        for line in lines:
            words = re.findall(r'\b\w+\b', line.lower())
            if words:
                end_words.append(words[-1])
        
        # Simple rhyme detection based on ending sounds
        if len(end_words) >= 4:
            if self._words_rhyme(end_words[0], end_words[2]) and self._words_rhyme(end_words[1], end_words[3]):
                return "ABAB"
            elif self._words_rhyme(end_words[0], end_words[1]) and self._words_rhyme(end_words[2], end_words[3]):
                return "AABB"
        
        return "free"
    
    def _words_rhyme(self, word1, word2):
        """Simple rhyme detection based on ending sounds"""
        if len(word1) < 2 or len(word2) < 2:
            return False
        return word1[-2:] == word2[-2:] or word1[-3:] == word2[-3:]
    
    def _detect_literary_devices(self, text):
        """Detect basic literary devices"""
        devices = {
            "alliteration": self._detect_alliteration(text),
            "repetition": self._detect_repetition(text),
            "metaphor_simile": self._detect_metaphor_simile(text)
        }
        return devices
    
    def _detect_alliteration(self, text):
        """Detect alliteration"""
        words = re.findall(r'\b\w+\b', text.lower())
        first_letters = [word[0] for word in words if word]
        letter_counts = Counter(first_letters)
        # If any letter appears 3+ times, consider it alliteration
        return any(count >= 3 for count in letter_counts.values())
    
    def _detect_repetition(self, text):
        """Detect word repetition"""
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = Counter(words)
        # Exclude common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'shall', 'must'}
        significant_repeats = {word: count for word, count in word_counts.items() 
                             if count > 1 and word not in common_words and len(word) > 2}
        return len(significant_repeats) > 0
    
    def _detect_metaphor_simile(self, text):
        """Detect metaphors and similes"""
        text_lower = text.lower()
        simile_indicators = ['like', 'as', 'similar to', 'resembles']
        metaphor_indicators = ['is', 'are', 'was', 'were', 'becomes', 'transforms']
        
        has_simile = any(indicator in text_lower for indicator in simile_indicators)
        has_metaphor = any(indicator in text_lower for indicator in metaphor_indicators)
        
        return has_simile or has_metaphor
    
    def _generate_musical_suggestions(self, analysis):
        """Generate musical parameters based on analysis"""
        suggestions = {}
        
        # Tempo based on sentiment and meter
        sentiment = analysis["sentiment"]
        if sentiment["mood"] == "positive":
            suggestions["tempo_suggestion"] = 130 + int(sentiment["polarity"] * 20)
        elif sentiment["mood"] == "negative":
            suggestions["tempo_suggestion"] = 90 + int(abs(sentiment["polarity"]) * 10)
        else:
            suggestions["tempo_suggestion"] = 120
        
        # Clamp tempo to reasonable range
        suggestions["tempo_suggestion"] = max(60, min(180, suggestions["tempo_suggestion"]))
        
        # Key based on sentiment
        if sentiment["mood"] == "positive":
            suggestions["key_suggestion"] = "C"  # Major
        elif sentiment["mood"] == "negative":
            suggestions["key_suggestion"] = "Am"  # Minor
        else:
            suggestions["key_suggestion"] = "C"
        
        # Time signature based on meter
        meter = analysis["meter"]
        if meter in ["iambic", "trochaic"]:
            suggestions["time_signature"] = "4/4"
        elif meter == "free_verse":
            suggestions["time_signature"] = "4/4"  # Default
        else:
            suggestions["time_signature"] = "4/4"
        
        return suggestions
