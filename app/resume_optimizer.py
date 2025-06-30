import os
import re
from transformers import DistilBertTokenizer, DistilBertForMaskedLM, BertTokenizer, BertForMaskedLM
from transformers import pipeline
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import docx
import nltk
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Safe download of 'punkt_tab' if not present
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    logger.info("Downloading NLTK punkt_tab resource...")
    nltk.download("punkt_tab")

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased")  # Allow model name to be set via environment variable

# Initialize tokenizer and model
try:
    if "distilbert" in MODEL_NAME.lower():
        tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
        model = DistilBertForMaskedLM.from_pretrained(MODEL_NAME)
    elif "bert" in MODEL_NAME.lower():
        tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
        model = BertForMaskedLM.from_pretrained(MODEL_NAME)
    else:
        raise ValueError(f"Model {MODEL_NAME} not supported. Choose 'distilbert-base-uncased' or 'bert-base-uncased'.")
except Exception as e:
    logger.error(f"Failed to load model or tokenizer: {e}")
    raise

fill_mask = pipeline(task="fill-mask", model=model, tokenizer=tokenizer)

def extract_text_from_docx(path):
    """Extract text from a .docx file."""
    if not os.path.exists(path):
        logger.error(f"Document not found: {path}")
        raise FileNotFoundError(f"Document not found: {path}")
    try:
        doc = docx.Document(path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        if not text:
            logger.warning(f"No text extracted from document: {path}")
        return text
    except Exception as e:
        logger.error(f"Error reading .docx file {path}: {e}")
        raise

def extract_keywords(text, top_k=10):
    """Extract top-k keywords from text, excluding stop words."""
    if not text or not isinstance(text, str):
        logger.error("Invalid input for keyword extraction: text must be a non-empty string")
        return []
    try:
        words = [w.lower() for w in word_tokenize(text) if w.isalnum() and w.lower() not in ENGLISH_STOP_WORDS]
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:top_k]]
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []

def preserve_case(original_word, replacement_word):
    """Preserve the case of the original word in the replacement."""
    if original_word.isupper():
        return replacement_word.upper()
    elif original_word.istitle():
        return replacement_word.capitalize()
    elif original_word.islower():
        return replacement_word.lower()
    return replacement_word

def optimize_resume(resume_text, job_description):
    """Optimize resume text by replacing keywords with model predictions."""
    if not resume_text or not job_description:
        logger.error("Resume text or job description is empty")
        return resume_text

    try:
        # Tokenize resume into sentences
        resume_sentences = sent_tokenize(resume_text)
        if not resume_sentences:
            logger.warning("No sentences found in resume text")
            return resume_text

        # Extract keywords once, outside the loop
        keywords = extract_keywords(job_description)
        if not keywords:
            logger.warning("No keywords extracted from job description")
            return resume_text

        enhanced_resume = []
        for sentence in resume_sentences:
            optimized = sentence
            for word in keywords:
                # Check if the word exists in the sentence (case-insensitive)
                pattern = rf"\b{re.escape(word)}\b"
                if re.search(pattern, sentence, flags=re.IGNORECASE):
                    # Find all matches to preserve their original case
                    matches = re.finditer(pattern, sentence, flags=re.IGNORECASE)
                    for match in matches:
                        original_word = match.group(0)
                        masked = re.sub(pattern, "[MASK]", sentence, flags=re.IGNORECASE, count=1)
                        try:
                            prediction = fill_mask(masked)
                            if prediction and isinstance(prediction, list) and len(prediction) > 0:
                                best_word = prediction[0]['token_str']
                                # Preserve the case of the original word
                                best_word = preserve_case(original_word, best_word)
                                optimized = re.sub(pattern, best_word, optimized, flags=re.IGNORECASE, count=1)
                            else:
                                logger.warning(f"No valid prediction for masked word: {word}")
                        except Exception as e:
                            logger.error(f"Masking failed for word '{word}' in sentence '{sentence}': {e}")
            enhanced_resume.append(optimized)

        return "\n".join(enhanced_resume)
    except Exception as e:
        logger.error(f"Error optimizing resume: {e}")
        return resume_text  # Return original text as fallback