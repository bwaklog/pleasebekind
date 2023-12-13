import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import unicodedata
import re

# language processing modules
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


"""
The following functions are used to clean the data
"""

# simpiiy the text
def simplify(text):
    # function to handle the diacritics in text
    import unicodedata
    try:
        text = unicode(text, 'utf-8')
    except NameError:
        pass
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return str(text)


# using regex to remove the url
def remove_url(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    text = url_pattern.sub('', text)

    tokenizer = TweetTokenizer(preserve_case=True)
    return tokenizer.tokenize(text)


# using stopwords to remove the stopwords
def remove_stopwords(text):
    stop_words = stopwords.words('english')
    additional_lst = ['amp', 'rt', 'u', "can't", 'ur']
    stop_words.extend(additional_lst)
    return [word for word in text if word not in stop_words]


# using regex to remove the hash symbol
def remove_hashsymbol(text):
    pattern = (r'#')
    text = ' '.join(text)
    clean_text = re.sub(pattern, '', text)
    tokenizer = TweetTokenizer(preserve_case=True)
    return tokenizer.tokenize(clean_text)


# removing short words
def remove_shorwords(text):
    length = [1, 2]
    new_text = ' '.join(text)
    tokenizer = TweetTokenizer(preserve_case=True)
    for word in text:
        text = [word for word in tokenizer.tokenize(new_text) if len(word) not in length]
    return text


# removing digits
def rem_digits(text):
    no_digits = [re.sub(r'\d', '', word) for word in text]
    # return TweetTokenizer.tokenize(' '.join(no_digits))
    tokenizer = TweetTokenizer(preserve_case=True)
    return tokenizer.tokenize(' '.join(no_digits))


# removing non alpha
def rem_noalpha(text):
    text = [word for word in text if word.isalpha()]
    return text


# joining the list
def join_lst(x):
    return ' '.join(x)


def retrain(text):
    try:
        tweets = pd.read_csv('./dfWithReported.csv')
    except FileNotFoundError:
        tweets = pd.read_csv('./ml_models/hsc-twitter-1/TwitterHate.csv')

    try:
        tweets.drop('id', axis=1, inplace=True)
    except KeyError:
        pass

    """
    Cleaning data using langauge processing and
    adding the text to the column with index 1
    """
    tweets.columns = ['label', 'tweet']
    

    """
    Data frame is of the structure
    label   tweet
    0       'text from post.content'
    """
    text = pd.DataFrame({'label': 1, 'tweet': text}, index=[0])

    # create a copy of the tweets dataframe
    df_save = tweets.copy()
    # concating text data frame to the tweets data frame
    df_save = pd.concat([text, tweets], ignore_index=True)
    # savinfg the dataframe to csv file
    df_save.to_csv('./dfWithReported.csv', index=False)

    df = tweets.copy()

    """
    Cleaning the data using langauge processing
    - we clean the csv file separately
    - we clean the text data frame separately
    """
    df['tweet'] = df['tweet'].apply(simplify)
    text['tweet'] = text['tweet'].apply(simplify)

    df['tweet'].replace(r'https?://\S+|www.\.\S+', '', regex=True, inplace=True)
    text['tweet'].replace(r'https?://\S+|www.\.\S+', '', regex=True, inplace=True)

    tokenizer = TweetTokenizer(preserve_case=True)
    df['tweet'] = df['tweet'].apply(tokenizer.tokenize)
    text['tweet'] = text['tweet'].apply(tokenizer.tokenize)

    df['tweet'] = df['tweet'].apply(remove_stopwords)
    text['tweet'] = text['tweet'].apply(remove_stopwords)

    df['tweet'] = df['tweet'].apply(remove_hashsymbol)
    text['tweet'] = text['tweet'].apply(remove_hashsymbol)

    df['tweet'] = df['tweet'].apply(remove_shorwords)
    text['tweet'] = text['tweet'].apply(remove_shorwords)

    df['tweet'] = df['tweet'].apply(rem_digits)
    text['tweet'] = text['tweet'].apply(rem_digits)

    df['tweet'] = df['tweet'].apply(rem_noalpha)
    text['tweet'] = text['tweet'].apply(rem_noalpha)

    df['tweet'] = df['tweet'].apply(join_lst)
    text['tweet'] = text['tweet'].apply(join_lst)

    # shuffle only the df dataframe
    df = df.sample(frac=1).reset_index(drop=True)

    # appending the text dataframe to the top of the df dataframe
    df = pd.concat([text, df], ignore_index=True)

    X = df['tweet']
    y = df['label']

    from sklearn.model_selection import train_test_split
    import random
    seed = random.randint(1, 100)
    test_size = 0.2
    # X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle = False, stratify = None)

    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorize = TfidfVectorizer(max_features=5000)

    import pickle
    pickle.dump(X, open('X_train_retrain.pkl', 'wb'))

    from sklearn.linear_model import LogisticRegression

    from scipy.stats import loguniform
    space = {
        'solver': ['newton-cg', 'lbfgs', 'liblinear'],
        'penalty': ['l2'],
        'C': loguniform(1e-5, 100),
    }

    X_train = vectorize.fit_transform(X)
    # X_test = vectorize.transform(X_test)

    weights = {0:1.0,1:13}
    clf = LogisticRegression(C=23.871926754399514,penalty='l1',solver='liblinear',class_weight=weights)
    clf.fit(X_train, y)

    import pickle
    with open('model_retrain.pkl', 'wb') as f:
        pickle.dump(clf, f)


"""
The following function is used to classify the text has hate speech or not

- The function loads the pretrained model and uses this model to predict the text
"""
def predict(text):

    """
    The following functions are used to clean the text

    We use this so that the text is in the same format as the training data
    """
    text_simplified = simplify(text)
    text_without_url = remove_url(text_simplified)
    text_without_stopwords = remove_stopwords(text_without_url)
    text_without_hash = remove_hashsymbol(text_without_stopwords)
    text_without_shortwords = remove_shorwords(text_without_hash)
    text_without_digits = rem_digits(text_without_shortwords)
    text_without_nonalpha = rem_noalpha(text_without_digits)
    text = join_lst(text_without_nonalpha)


    """
    -   We load the pretraained model and then use the same model to 
        predict the text.
    -   Incase there has been a reported tweet, and we retrain the model,
        that model is saved in the piceled file model_retrain.pkl, 
        which if exists is called to make a prediction for hate speech classification
    """
    try:
        model = pickle.load(open('model_retrain.pkl', 'rb'))
    except FileNotFoundError:
        model = pickle.load(open('test1.pkl', 'rb'))


    tokenizer = TweetTokenizer(preserve_case=True)
    textT = tokenizer.tokenize(text)

    vectorize = TfidfVectorizer(max_features=5000)

    """
    traning data is obtained from a pickel save, which basically
    has a list of pre tokenised tweets, to save some time...

    Incase the picel file for the retrained model isn't found, we
    use the original pickle file, which has the original training
    """
    try:
        X_train = pickle.load(open('X_train_retrain.pkl', 'rb'))
    except FileNotFoundError:
        X_train = pickle.load(open('X_train.pkl', 'rb'))


    X_train = vectorize.fit_transform(X_train)
    X_test = vectorize.transform([text])
    predict = model.predict(X_test)
    return predict


if __name__=="__main__":
    predict('Fucking bitch ass show')
    text = "Honestly this bitch can go rot in hell."

    