import os
import re
from collections import defaultdict
from transformers import pipeline, DistilBertTokenizer, DistilBertForMaskedLM
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS
import logging
from functools import lru_cache
import nltk

nltk.download("punkt")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model
MODEL_NAME = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
model = DistilBertForMaskedLM.from_pretrained(MODEL_NAME)
fill_mask = pipeline(task="fill-mask", model=model, tokenizer=tokenizer)

def is_url(text):
    return bool(re.search(r"(http[s]?://|www\.)\S+", text))

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

@lru_cache(maxsize=500)
def get_mask_predictions(masked_sentence, top_k=5):
    try:
        predictions = fill_mask(masked_sentence, top_k=top_k)
        return [pred['token_str'].replace("##", "").strip() for pred in predictions]
    except:
        return []

def extract_keywords(text, top_k=100):
    vectorizer = CountVectorizer(
        ngram_range=(1, 2),
        stop_words=list(ENGLISH_STOP_WORDS),
        max_features=top_k * 2
    )
    matrix = vectorizer.fit_transform([text])
    keywords = zip(vectorizer.get_feature_names_out(), matrix.sum(axis=0).tolist()[0])
    return [w for w, _ in sorted(keywords, key=lambda x: x[1], reverse=True) if len(w) > 1]

def preserve_case(original, replacement):
    if original.isupper():
        return replacement.upper()
    elif original.istitle():
        return replacement.capitalize()
    else:
        return replacement.lower()

def segment_resume_sections(resume_text):
    sections = defaultdict(str)
    current_section = "general"
    for line in resume_text.splitlines():
        if "overview" in line.lower() or "summary" in line.lower():
            current_section = "overview"
        elif "skills" in line.lower():
            current_section = "skills"
        elif "experience" in line.lower():
            current_section = "experience"
        elif line.strip() == "":
            continue
        sections[current_section] += line.strip() + " "
    return sections

def optimize_resume(resume_text, job_description, replacement_threshold=0.5):
    resume_text = clean_text(resume_text)
    jd_text = clean_text(job_description)

    jd_keywords = extract_keywords(jd_text, top_k=100)
    resume_keywords = extract_keywords(resume_text, top_k=100)

    missing_keywords = [kw for kw in jd_keywords if kw not in resume_keywords]

    logger.info(f"Missing JD Keywords: {missing_keywords}")

    sections = segment_resume_sections(resume_text)
    updated_resume = []
    change_log = []

    # 1. Optimize Overview
    if sections["overview"]:
        summary_sentences = sent_tokenize(sections["overview"])
        enriched = set()
        for kw in missing_keywords:
            for i, sent in enumerate(summary_sentences):
                if kw in sent or is_url(sent):
                    continue
                if "[MASK]" not in sent and len(sent.split()) > 4:
                    tokens = sent.split()
                    middle = len(tokens) // 2
                    masked = " ".join(tokens[:middle]) + " [MASK] " + " ".join(tokens[middle:])
                    predictions = get_mask_predictions(masked)
                    if predictions:
                        enriched.add(kw)
                        summary_sentences[i] = sent + f" Skilled in {kw}."
                        change_log.append(f"Added '{kw}' to summary.")
                        break
        sections["overview"] = " ".join(summary_sentences)

    # 2. Optimize Skills section
    if sections["skills"]:
        existing_skills = set(re.split(r",|\n|;", sections["skills"]))
        new_skills = [kw for kw in missing_keywords if kw not in existing_skills]
        if new_skills:
            sections["skills"] = sections["skills"].strip().rstrip(".") + ", " + ", ".join(new_skills) + "."
            change_log.append(f"Added new skills: {new_skills}")

    # 3. Optimize Experience
    if sections["experience"]:
        experience_sentences = sent_tokenize(sections["experience"])
        for i, sent in enumerate(experience_sentences):
            if is_url(sent):
                continue
            for kw in missing_keywords:
                if kw in sent:
                    continue
                if "[MASK]" not in sent:
                    mid = len(sent.split()) // 2
                    tokens = sent.split()
                    masked = " ".join(tokens[:mid]) + " [MASK] " + " ".join(tokens[mid:])
                    preds = get_mask_predictions(masked)
                    if preds and kw not in sent:
                        experience_sentences[i] += f" Worked on {kw}."
                        change_log.append(f"Added '{kw}' to experience.")
                        break
        sections["experience"] = " ".join(experience_sentences)

    # 4. Rebuild updated resume
    for sec in ["overview", "skills", "experience", "general"]:
        if sections[sec]:
            updated_resume.append(f"\n--- {sec.upper()} ---\n{sections[sec]}")

    logger.info("Resume optimization complete.")
    return "\n".join(updated_resume).strip(), change_log

# === Example Usage ===
if __name__ == "__main__":
    sample_resume = """
    OVERVIEW
    Experienced software developer with 5 years of experience in Python and Java.

    SKILLS
    Python, Java, Git

    EXPERIENCE
    Developed machine learning models for predictive analytics.
    Strong background in data structures and algorithms.
    """

    sample_jd = """
    Looking for an experienced Python developer familiar with TensorFlow, data pipelines,
    model deployment, neural networks, cloud platforms like AWS or Azure, and containerization tools.
    Must have experience in CI/CD, Docker, and Kubernetes.
    """

    optimized_resume, changes = optimize_resume(sample_resume, sample_jd)
    print("\n=== Optimized Resume ===\n")
    print(optimized_resume)
    print("\n=== Modifications Done ===\n")
    for c in changes:
        print(f"- {c}")
