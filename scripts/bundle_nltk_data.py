"""Download the NLTK data the app needs into a folder for PyInstaller to bundle.

Usage: python scripts/bundle_nltk_data.py <target_dir>

Exits non-zero if any package fails to download or the app's NLTK calls fail
when NLTK is restricted to <target_dir>, so CI cannot ship a bundle that is
missing data (the packaged app never downloads NLTK data at runtime).
"""

import os
import sys

import nltk

PACKAGES = [
    "punkt",  # grammar.py checks tokenizers/punkt and falls back to naive splitting without it
    "punkt_tab",
    "averaged_perceptron_tagger_eng",
    "wordnet",
    "omw-1.4",
    "wordnet_ic",
]


def download(target_dir):
    for package in PACKAGES:
        print(f"Downloading {package}")
        nltk.download(package, download_dir=target_dir, quiet=True, raise_on_error=True)


def verify(target_dir):
    nltk.data.path[:] = [target_dir]

    from nltk import pos_tag, sent_tokenize, word_tokenize
    from nltk.stem import WordNetLemmatizer

    nltk.data.find("tokenizers/punkt")
    assert sent_tokenize("The dog runs. The cat sleeps.") == ["The dog runs.", "The cat sleeps."]
    assert pos_tag(word_tokenize("The dog runs"))[1] == ("dog", "NN")
    assert WordNetLemmatizer().lemmatize("dogs") == "dog"


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/bundle_nltk_data.py <target_dir>")
    target_dir = os.path.abspath(sys.argv[1])
    # NLTK refuses to download into group- or world-writable directories.
    os.makedirs(target_dir, mode=0o755, exist_ok=True)
    os.chmod(target_dir, 0o755)

    download(target_dir)
    verify(target_dir)
    print(f"NLTK data verified in {target_dir}")


if __name__ == "__main__":
    main()
