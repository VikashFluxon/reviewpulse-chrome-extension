
from urllib.parse import urlparse
import re
import nltk
import openai
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_product_id(url):
    product_id = re.findall(r"/dp/(\w+)(?:/|\?|$)", url)
    if product_id:
        return product_id[0]

def get_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc.replace('www.amazon.', '')

def pos_tagging(text):
    tokenized = sent_tokenize(text)
    for i in tokenized:
        words = nltk.word_tokenize(i)
        words = [word for word in words if word.isalpha()]  # remove punctuation
        tagged = nltk.pos_tag(words)
        return tagged

def remove_words(text):
    pos_to_remove = ['PRON', 'ADP', 'CONJ']
    tagged_words = pos_tagging(text)
    filtered_words = [word for word, pos in tagged_words if pos not in pos_to_remove]
    return ' '.join(filtered_words)

def summarize_reviews(reviews):
    shorten_reviews = []
    for r in reviews:
        if r:
            shorten_reviews.append(remove_words(r))
    
    reviews_str = '\n'.join(shorten_reviews)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Summarize these product reviews in a few short bullet points. \n {reviews_str}"}
        ]
    )
    # return completion['choices']
    content = completion['choices'][0].get('message', {}).get('content', '')
    content = content.replace('- ', '')
    content = content.replace('-', '')
    content = content.split('\n')
    return content
