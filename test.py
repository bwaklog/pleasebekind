import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import unicodedata
import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import TweetTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import re

from textblob import TextBlob

import pickle

text = 'Fucking bitch ass show' 


def simplify(text):
    # function to handle the diacritics in text
    import unicodedata
    try:
        text = unicode(text, 'utf-8')
    except NameError:
        pass
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return str(text)

text = simplify(text)

url_pattern = re.compile(r'https?://\S+|www\.\S+')
text = url_pattern.sub('', text)

tokenizer = TweetTokenizer(preserve_case=True)
textTokenized = tokenizer.tokenize(text)

stop_words = stopwords.words('english')
additional_lst = ['amp', 'rt', 'u', "can't", 'ur']
stop_words.extend(additional_lst)

def remove_stopwords(text):
    return [word for word in text if word not in stop_words]

text = remove_stopwords(textTokenized)

def remove_hashsymbol(text):
    pattern = (r'#')
    text = ' '.join(text)
    clean_text = re.sub(pattern, '', text)
    return tokenizer.tokenize(clean_text)

text = remove_hashsymbol(text)


def remove_shorwords(text):
    length = [1, 2]
    new_text = ' '.join(text)
    for word in text:
        text = [word for word in tokenizer.tokenize(new_text) if len(word) not in length]
    return text

text = remove_shorwords(text)

def rem_digits(text):
    no_digits = [re.sub(r'\d', '', word) for word in text]
    return tokenizer.tokenize(' '.join(no_digits))

text = rem_digits(text)

def rem_noalpha(text):
    text = [word for word in text if word.isalpha()]
    return text

def join_lst(x):
    return ' '.join(x)

text = join_lst(text)
print(text)


# model = LogisticRegression(pickle.load(open('test1.pkl', 'rb')))
model = pickle.load(open('test1.pkl', 'rb'))
model = pickle.load(open('clf2.pkl', 'rb'))
textT = tokenizer.tokenize(text)

vectorize = TfidfVectorizer(max_features=5000)
# X_train import from file X_train.pkl
X_train = pickle.load(open('X_train.pkl', 'rb'))
X_train = vectorize.fit_transform(X_train)
X_test = vectorize.transform([text])
predict = model.predict(X_test)
print(predict)