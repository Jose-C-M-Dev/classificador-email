import re
from typing import List, Set

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import RSLPStemmer
except ImportError:
    raise ImportError(
        "NLTK não está instalado. Execute: pip install nltk"
    )

try:
    from unidecode import unidecode
except ImportError:
    raise ImportError(
        "Unidecode não está instalado. Execute: pip install unidecode"
    )

for resource in ['punkt', 'punkt_tab', 'stopwords', 'rslp']:
    try:
        nltk.download(resource, quiet=True)
    except (LookupError, OSError, Exception) as e:
        continue

STOPWORDS_PT: Set[str] = set(stopwords.words('portuguese'))

STEMMER = RSLPStemmer()

CUSTOM_STOPWORDS = {
    'email', 'assunto', 'att', 'atenciosamente', 'cordialmente',
    'prezado', 'prezada', 'senhor', 'senhora', 'sr', 'sra'
}

STOPWORDS_PT.update(CUSTOM_STOPWORDS)

def clean_text(text: str) -> str:
    text = re.sub(r'https?://(?:[a-zA-Z]|[0-9]|[$\-_@.&+]|[!*(),]|%[0-9a-fA-F][0-9a-fA-F])+', '', text)

    text = re.sub(r'\S+@\S+', '', text)

    text = re.sub(r'\(?\d{2,3}\)?\s?\d{4,5}-?\d{4}', '', text)

    text = re.sub(r'[^\w\s.,!?;:\-áéíóúâêîôûãõàèìòùäëïöüçÁÉÍÓÚÂÊÎÔÛÃÕÀÈÌÒÙÄËÏÖÜÇ]', ' ', text)

    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def remove_stopwords(tokens: List[str]) -> List[str]:
    return [token for token in tokens if token.lower() not in STOPWORDS_PT]


def apply_stemming(tokens: List[str]) -> List[str]:
    return [STEMMER.stem(token) for token in tokens]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = unidecode(text)
    return text


def preprocess_email(text: str, apply_stem: bool = True) -> dict:
    cleaned = clean_text(text)

    tokens = word_tokenize(cleaned, language='portuguese')

    tokens = [normalize_text(token) for token in tokens if len(token) > 2]

    tokens_no_stop = remove_stopwords(tokens)

    if apply_stem:
        tokens_stemmed = apply_stemming(tokens_no_stop)
        final_tokens = tokens_stemmed
    else:
        final_tokens = tokens_no_stop

    processed_text = ' '.join(final_tokens)

    stats = {
        'original_length': len(text),
        'cleaned_length': len(cleaned),
        'total_tokens': len(tokens),
        'tokens_after_stopwords': len(tokens_no_stop),
        'final_tokens': len(final_tokens),
        'reduction_percentage': round((1 - len(final_tokens) / max(len(tokens), 1)) * 100, 2)
    }

    return {
        'original': text,
        'cleaned': cleaned,
        'tokens': tokens_no_stop,
        'stemmed': final_tokens if apply_stem else None,
        'processed': processed_text,
        'stats': stats
    }


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    processed = preprocess_email(text, apply_stem=True)
    tokens = processed['stemmed'] or processed['tokens']

    from collections import Counter
    freq = Counter(tokens)

    return [word for word, _ in freq.most_common(top_n)]

def quick_preprocess(text: str) -> str:
    return preprocess_email(text, apply_stem=True)['processed']