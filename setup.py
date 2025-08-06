import nltk
import spacy

def download_nltk_data():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')

def download_spacy_model():
    try:
        spacy.load("en_core_web_sm")
        print("spaCy model already downloaded.")
    except OSError:
        print("Downloading spaCy model...")
        spacy.cli.download("en_core_web_sm")

if __name__ == "__main__":
    print("Setting up NLP requirements...")
    download_nltk_data()
    download_spacy_model()
    print("✅ All NLP dependencies are set up.")
