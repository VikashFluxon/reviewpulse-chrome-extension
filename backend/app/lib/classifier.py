import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import string

table = str.maketrans({key: None for key in string.punctuation})


def get_feature_vector(rating, verified_purchase, tokens):
    fv = {}
    fv["R"] = rating
    fv["VP"] = verified_purchase
    for token in tokens:
        if token not in fv:
            fv[token] = 1
        else:
            fv[token] = +1
    return fv


def pre_process(text):
    lemmatizer = WordNetLemmatizer()
    filtered_tokens = []
    lemmatized_tokens = []
    stop_words = set(stopwords.words("english"))
    text = text.translate(table)
    for w in text.split(" "):
        if w not in stop_words:
            lemmatized_tokens.append(lemmatizer.lemmatize(w.lower()))
        filtered_tokens = [
            " ".join(l) for l in nltk.bigrams(lemmatized_tokens)
        ] + lemmatized_tokens
    return filtered_tokens


def classify(fv, classifier):
    return classifier.classify(fv)

def classify_many(fvs, classifier):
    return classifier.classify_many(fvs)
