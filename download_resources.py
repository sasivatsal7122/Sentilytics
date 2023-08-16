import nltk
from transformers import AutoTokenizer,AutoModelForSequenceClassification

def download_nltk_resources():
    nltk_resources = [
        "vader_lexicon",
        "stopwords",
        "punkt",
        "wordnet",
        "omw-1.4"
    ]
    
    for resource in nltk_resources:
        nltk.download(resource)

def download_model():
    model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(model, from_tf=False)

if __name__ == "__main__":
    download_nltk_resources()
    download_model()
