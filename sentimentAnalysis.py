import pandas as pd
import numpy as np
import json
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from scipy.special import softmax
import csv
import urllib.request

from textblob import TextBlob
from afinn import Afinn
import string
import asyncio

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", message="oneDNN custom operations are on.")
warnings.filterwarnings("ignore", message="This TensorFlow binary is optimized to use available CPU instructions.")
warnings.filterwarnings("ignore", message="TF-TRT Warning: Could not find TensorRT")
warnings.filterwarnings("ignore", message="Some weights of the model checkpoint at cardiffnlp/twitter-roberta-base-sentiment-latest were not used when initializing RobertaForSequenceClassification")

async def vader(vader_df):
    vader_df['Comments'] = vader_df['Comments'].astype(str)
    vader_df['Comments'] = vader_df['Comments'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))
    vader_df['Comments'] = vader_df['Comments'].apply(lambda x:x.lower())

    tokenized_tweet = vader_df['Comments'].apply(lambda x: x.split())

    wnl = WordNetLemmatizer()

    tokenized_tweet.apply(lambda x: [wnl.lemmatize(i) for i in x if i not in set(stopwords.words('english'))]) 
    tokenized_tweet.head()

    for i in range(len(tokenized_tweet)):
        tokenized_tweet[i] = ' '.join(tokenized_tweet[i])
        
        
    vader_df['Comments'] = tokenized_tweet

    sia = SentimentIntensityAnalyzer()
    vader_df['Sentiment Scores'] = vader_df['Comments'].apply(lambda x:sia.polarity_scores(x)['compound'])
    vader_df['Sentiment'] = vader_df['Sentiment Scores'].apply(lambda s : 'Positive' if s > 0 else ('Neutral' if s == 0 else 'Negative'))
    
    classfication_cnt = vader_df.Sentiment.value_counts()
    vader_percentages = vader_df['Sentiment'].value_counts(normalize=True) * 100
    
    return vader_df

async def textblob(textBlob_df):
    textBlob_df['Comments'] = textBlob_df['Comments'].astype(str)
    textBlob_df['Sentiment Scores'] = ''
    textBlob_df['Sentiment'] = ''

    def preprocess_text(text):
        text = text.lower()    
        text = text.translate(str.maketrans('', '', string.punctuation))    
        tokens = text.split()

        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        preprocessed_text = ' '.join(tokens)

        return preprocessed_text

    for index, row in textBlob_df.iterrows():
        comment = row['Comments']    
        preprocessed_comment = preprocess_text(comment)

        blob = TextBlob(preprocessed_comment)
        polarity = blob.sentiment.polarity

        textBlob_df.at[index, 'Sentiment Scores'] = polarity

        if polarity > 0:
            textBlob_df.at[index, 'Sentiment'] = 'Positive'
        elif polarity < 0:
            textBlob_df.at[index, 'Sentiment'] = 'Negative'
        else:
            textBlob_df.at[index, 'Sentiment'] = 'Neutral'
    
    classfication_cnt = textBlob_df.Sentiment.value_counts()
    textBlob_percentages = textBlob_df['Sentiment'].value_counts(normalize=True) * 100
    
    return textBlob_df

async def afinn(afinn_df):
    afinn = Afinn()
    afinn_df['Comments'] = afinn_df['Comments'].astype(str)

    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    def preprocess_text(text):
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token.lower() not in stop_words]
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        preprocessed_text = ' '.join(tokens)
        return preprocessed_text

    def get_sentiment(text):
        sentiment_score = afinn.score(text)
        if sentiment_score > 0:
            return "Positive"
        elif sentiment_score < 0:
            return "Negative"
        else:
            return "Neutral"

    afinn_df["Sentiment"] = afinn_df["Comments"].apply(preprocess_text).apply(get_sentiment)
    afinn_df["Sentiment Scores"] = afinn_df["Comments"].apply(preprocess_text).apply(afinn.score)
    
    classfication_cnt = afinn_df.Sentiment.value_counts()
    afinn_percentages = afinn_df['Sentiment'].value_counts(normalize=True) * 100
    
    return afinn_df
    

async def robert_new(robertNew_df):
    def preprocess_text(text):
        text = text.lower()    
        text = text.translate(str.maketrans('', '', string.punctuation))    
        tokens = text.split()

        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        preprocessed_text = ' '.join(tokens)

        return preprocessed_text
    
    mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt"
    with urllib.request.urlopen(mapping_link) as f:
        html = f.read().decode('utf-8').split("\n")
        csvreader = csv.reader(html, delimiter='\t')
    labels = [row[1] for row in csvreader if len(row) > 1]

    task = 'sentiment'
    MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL,from_tf=False)

    robertNew_df['Comments'] = robertNew_df['Comments'].astype(str)
    robertNew_df['Sentiment Scores'] = ''
    robertNew_df['Sentiment'] = ''

    for index, row in robertNew_df.iterrows():
        comment = row['Comments']
        preprocessed_comment = preprocess_text(comment)

        encoded_input = tokenizer(preprocessed_comment, return_tensors='pt')
        output = model(**encoded_input)
        scores = output.logits[0].detach().numpy()
        scores = softmax(scores)

        ranking = np.argsort(scores)
        ranking = ranking[::-1]
        for i in range(scores.shape[0]):
            l = labels[ranking[i]]
            s = scores[ranking[i]]
            if i == 0:
                robertNew_df.at[index, 'Sentiment Scores'] = np.round(float(s), 4)
                robertNew_df.at[index, 'Sentiment'] = l.title()
                break
            
    classfication_cnt = robertNew_df.Sentiment.value_counts()
    robertNew_percentages = robertNew_df['Sentiment'].value_counts(normalize=True) * 100
    
    return robertNew_df


async def robert_old(robertOld_df):
    def preprocess_text(text):
        text = text.lower()    
        text = text.translate(str.maketrans('', '', string.punctuation))    
        tokens = text.split()

        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        preprocessed_text = ' '.join(tokens)

        return preprocessed_text
    
    mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt"
    with urllib.request.urlopen(mapping_link) as f:
        html = f.read().decode('utf-8').split("\n")
        csvreader = csv.reader(html, delimiter='\t')
    labels = [row[1] for row in csvreader if len(row) > 1]

    task = 'sentiment'
    MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL,from_tf=False)

    robertOld_df['Comments'] = robertOld_df['Comments'].astype(str)
    robertOld_df['Sentiment Scores'] = ''
    robertOld_df['Sentiment'] = ''

    for index, row in robertOld_df.iterrows():
        comment = row['Comments']
        preprocessed_comment = preprocess_text(comment)

        encoded_input = tokenizer(preprocessed_comment, return_tensors='pt')
        output = model(**encoded_input)
        scores = output.logits[0].detach().numpy()
        scores = softmax(scores)

        ranking = np.argsort(scores)
        ranking = ranking[::-1]
        for i in range(scores.shape[0]):
            l = labels[ranking[i]]
            s = scores[ranking[i]]
            if i == 0:
                robertOld_df.at[index, 'Sentiment Scores'] = np.round(float(s), 4)
                robertOld_df.at[index, 'Sentiment'] = l.title()
                break
            
    classfication_cnt = robertOld_df.Sentiment.value_counts()
    robertOld_percentages = robertOld_df['Sentiment'].value_counts(normalize=True) * 100
    
    return robertOld_df

    
async def performSentiandVoting(master_comments_df,comments_df,videoID):
    
    comment_ids = list(comments_df['Comment ID'].to_list())
    
    tb_df = comments_df.copy()
    af_df = comments_df.copy()
    vd_df = comments_df.copy()
    rbn_df = comments_df.copy()
    rbo_df = comments_df.copy()
    
    # textBlob_df = await textblob(tb_df)
    # afinn_df = await afinn(af_df)
    # vader_df = await vader(vd_df)
    # robertNew_df = await robert_new(rbn_df)
    # robertOld_df = await robert_old(rbo_df)
    results = await asyncio.gather(
                    textblob(tb_df),
                    afinn(af_df),
                    vader(vd_df),
                    robert_new(rbn_df),
                    robert_old(rbo_df)
            )

    textBlob_df, afinn_df, vader_df, robertNew_df, robertOld_df = results
    vote_df = pd.DataFrame()
    for comment_id in comment_ids:
        pos_count = 0
        neg_count = 0
        neu_count = 0

        vader_sentiment_pred = vader_df.loc[vader_df['Comment ID'] == comment_id, 'Sentiment'].values
        pos_count += sum(vader_sentiment_pred == 'Positive')
        neg_count += sum(vader_sentiment_pred == 'Negative')
        neu_count += sum(vader_sentiment_pred == 'Neutral')

        textblob_sentiment_pred = textBlob_df.loc[textBlob_df['Comment ID'] == comment_id, 'Sentiment'].values
        pos_count += sum(textblob_sentiment_pred == 'Positive')
        neg_count += sum(textblob_sentiment_pred == 'Negative')
        neu_count += sum(textblob_sentiment_pred == 'Neutral')

        afinn_sentiment_pred = afinn_df.loc[afinn_df['Comment ID'] == comment_id, 'Sentiment'].values
        pos_count += sum(afinn_sentiment_pred == 'Positive')
        neg_count += sum(afinn_sentiment_pred == 'Negative')
        neu_count += sum(afinn_sentiment_pred == 'Neutral')
        
        robertNew_sentiment_pred = robertNew_df.loc[robertNew_df['Comment ID'] == comment_id, 'Sentiment'].values
        pos_count += sum(robertNew_sentiment_pred == 'Positive')
        neg_count += sum(robertNew_sentiment_pred == 'Negative')
        neu_count += sum(robertNew_sentiment_pred == 'Neutral')
        
        robertOld_sentiment_pred = robertOld_df.loc[robertOld_df['Comment ID'] == comment_id, 'Sentiment'].values
        pos_count += sum(robertOld_sentiment_pred == 'Positive')
        neg_count += sum(robertOld_sentiment_pred == 'Negative')
        neu_count += sum(robertOld_sentiment_pred == 'Neutral')

        vote_df = vote_df.append({'Comment ID': comment_id, 'Positive': pos_count, 'Negative': neg_count, 'Neutral': neu_count}, ignore_index=True)

    vote_df = vote_df.fillna(0)

    vote_df['Positive'] = vote_df['Positive'].astype(int)
    vote_df['Negative'] = vote_df['Negative'].astype(int)
    vote_df['Neutral'] = vote_df['Neutral'].astype(int)
    
    sentiment_df = vote_df[['Comment ID', 'Positive', 'Negative', 'Neutral']].copy()
    sentiment_df['Sentiment'] = sentiment_df[['Positive', 'Negative', 'Neutral']].idxmax(axis=1)

    merged_df = pd.merge(master_comments_df, sentiment_df, left_on='Comment ID', right_on='Comment ID', how='left')
    
    sentiment_df_final = merged_df[['Comment ID', 'Comments', 'Sentiment']].copy()
    sentiment_df_final['Video ID'] = videoID
    
    return sentiment_df_final


def create_comments_json(hlSenti_df):

    comments_json = {
        "Sentiment Metrics": {
            "Comments Count": {"High Level": str(hlSenti_df.shape[0])},
            "Sentiment Percentages": {
                "High Level Percentages": {
                    "Positive": str(round(hlSenti_df["Sentiment"].value_counts(normalize=True).get("Positive", 0) * 100,2))+" %",
                    "Negative": str(round(hlSenti_df["Sentiment"].value_counts(normalize=True).get("Negative", 0) * 100,2))+" %",
                    "Neutral": str(round(hlSenti_df["Sentiment"].value_counts(normalize=True).get("Neutral", 0) * 100,2))+" %"
                },
            },
            "Sentiment Count": {
                "High Level Count": {
                    "Positive": str(hlSenti_df["Sentiment"].value_counts().get("Positive", 0)),
                    "Negative": str(hlSenti_df["Sentiment"].value_counts().get("Negative", 0)),
                    "Neutral": str(hlSenti_df["Sentiment"].value_counts().get("Neutral", 0))
                },
            }
        },
        "Comments": {},
    }

    hl_comments = []
    for index, row in hlSenti_df.iterrows():
        comment_dict = {
            "Comment ID": row["Comment ID"],
            "Comment": row["Comments"],
            "Sentiment": row["Sentiment"]
        }
        hl_comments.append(comment_dict)
    comments_json["Comments"][hlSenti_df["Video ID"].iloc[0]] = hl_comments

    json_string = json.dumps(comments_json)
    json_data = json.loads(json_string)
    
    return json_data



async def performSentilytics(videoID):

    from database import get_FhlComments
    from database import get_MhlComments
    
    comments_df = await get_FhlComments(videoID)
    master_comments_df = await get_MhlComments(videoID)

    hlSenti_df = await performSentiandVoting(master_comments_df,comments_df,videoID)
  
    from database import insert_hlSentiComments    
    await insert_hlSentiComments(hlSenti_df)

    
    
    

    
    
    
    
    
