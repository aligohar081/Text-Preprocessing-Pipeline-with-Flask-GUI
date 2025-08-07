# text_preprocessing.py
import nltk
import string
import re
from typing import List, Dict, Any, Optional
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
import pandas as pd
import io

class TextPreprocessor:
    """
    A comprehensive text preprocessing pipeline for NLP tasks.
    
    Features:
    - Lowercasing
    - Punctuation removal
    - Tokenization
    - Stopword removal
    - Lemmatization
    - Stemming
    - Special character filtering
    """
    
    def __init__(self):
        """Initialize the preprocessor and download required NLTK data."""
        self._download_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
    
    def _download_nltk_data(self) -> None:
        """Download required NLTK datasets if not already present."""
        required_data = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}' if data == 'punkt' else f'corpora/{data}')
            except LookupError:
                nltk.download(data, quiet=True)
    
    def to_lowercase(self, text: str) -> str:
        """Convert text to lowercase."""
        return text.lower()
    
    def remove_punctuation(self, text: str) -> str:
        """Remove punctuation from text."""
        return text.translate(str.maketrans('', '', string.punctuation))
    
    def remove_special_characters(self, text: str) -> str:
        """Remove special characters and numbers, keeping only alphabetic characters and spaces."""
        return re.sub(r'[^a-zA-Z\s]', '', text)
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into individual words."""
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list."""
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Apply lemmatization to tokens."""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def stem(self, tokens: List[str]) -> List[str]:
        """Apply stemming to tokens."""
        return [self.stemmer.stem(token) for token in tokens]
    
    def preprocess(self, 
                   text: str, 
                   lowercase: bool = True,
                   remove_punct: bool = True,
                   remove_special: bool = False,
                   tokenize_text: bool = True,
                   remove_stops: bool = True,
                   lemmatize_text: bool = True,
                   stem_text: bool = False) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline with configurable steps.
        
        Args:
            text: Input text to preprocess
            lowercase: Whether to convert to lowercase
            remove_punct: Whether to remove punctuation
            remove_special: Whether to remove special characters and numbers
            tokenize_text: Whether to tokenize the text
            remove_stops: Whether to remove stopwords
            lemmatize_text: Whether to apply lemmatization
            stem_text: Whether to apply stemming
            
        Returns:
            Dictionary containing original text, processed text, and tokens
        """
        original_text = text
        processed_text = text
        
        # Apply preprocessing steps
        if lowercase:
            processed_text = self.to_lowercase(processed_text)
        
        if remove_punct:
            processed_text = self.remove_punctuation(processed_text)
        
        if remove_special:
            processed_text = self.remove_special_characters(processed_text)
        
        # Clean up extra whitespaces
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        tokens = []
        if tokenize_text:
            tokens = self.tokenize(processed_text)
            
            if remove_stops:
                tokens = self.remove_stopwords(tokens)
            
            if lemmatize_text:
                tokens = self.lemmatize(tokens)
            
            if stem_text:
                tokens = self.stem(tokens)
        
        return {
            'original_text': original_text,
            'processed_text': processed_text,
            'tokens': tokens,
            'token_count': len(tokens)
        }
    
    def process_batch(self, texts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Process multiple texts with the same configuration."""
        return [self.preprocess(text, **kwargs) for text in texts]
    
    def process_csv_content(self, csv_content: str, text_column: str = 'text', **kwargs) -> pd.DataFrame:
        """Process text from CSV content."""
        df = pd.read_csv(io.StringIO(csv_content))
        
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in CSV")
        
        results = []
        for _, row in df.iterrows():
            text = str(row[text_column])
            result = self.preprocess(text, **kwargs)
            results.append({
                'original_text': result['original_text'],
                'processed_text': result['processed_text'],
                'tokens': ' '.join(result['tokens']),
                'token_count': result['token_count']
            })
        
        return pd.DataFrame(results)