import pandas as pd
import numpy as np
import json
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from scipy.special import softmax


from textblob import TextBlob
from afinn import Afinn
import string
import asyncio
from postreq import send_telegram_message
import warnings

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
    
async def robert(robert_df):
    def preprocess(text):
        new_text = []
        for t in text.split(" "):
            t = '@user' if t.startswith('@') and len(t) > 1 else t
            t = 'http' if t.startswith('http') else t
            new_text.append(t)
        return " ".join(new_text)

    warnings.filterwarnings("ignore")
    MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    config = AutoConfig.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    warnings.filterwarnings("default")
    
    sentiment_scores = []
    sentiments = []

    for i, row in robert_df.iterrows():
        try:
            comment = row["Comments"]

            processed_comment = preprocess(comment)
            encoded_input = tokenizer(processed_comment, return_tensors='pt')
            output = model(**encoded_input)
            scores = output.logits.detach().numpy()
            scores = softmax(scores, axis=1)

            sentiment_label = config.id2label[np.argmax(scores)].title()
            sentiment_score = np.max(scores)

            sentiment_scores.append(sentiment_score)
            sentiments.append(sentiment_label)
        except Exception as e:
            sentiment_scores.append(None)
            sentiments.append(None)
            print(f"Skipping comment with error: {e}")
            continue

    robertSenti_df = pd.DataFrame({
        "Comments": robert_df["Comments"],
        "Comment ID": robert_df["Comment ID"],
        "Sentiment Scores": sentiment_scores,
        "Sentiment": sentiments
    })

    return robertSenti_df
    
    
async def performSentiandVoting(master_comments_df,comments_df,videoID):
    
    comment_ids = list(comments_df['Comment ID'].to_list())
    
    tb_df = comments_df.copy()
    af_df = comments_df.copy()
    vd_df = comments_df.copy()
    rb_df = comments_df.copy()
    
    results = await asyncio.gather(
        textblob(tb_df),
        afinn(af_df),
        vader(vd_df),        
        robert(rb_df)
    )
    textBlob_df, afinn_df, vader_df, robert_df = results
    
    vote_df = pd.DataFrame()
    vote_data = []
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
        
        robert_sentiment_pred = robert_df.loc[robert_df['Comment ID'] == comment_id, 'Sentiment'].values
        pos_count += sum(robert_sentiment_pred == 'Positive')
        neg_count += sum(robert_sentiment_pred == 'Negative')
        neu_count += sum(robert_sentiment_pred == 'Neutral')
        
        vote_data.append({'Comment ID': comment_id, 'Positive': [pos_count], 'Neutral': [neu_count], 'Negative': [neg_count]})
        
    vote_df = pd.concat([pd.DataFrame(data) for data in vote_data], ignore_index=True)
    vote_df = vote_df.fillna(0)

    print(vote_df.head())
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



async def performSentilytics(videoIDs,channelName):

    from database import get_FhlComments
    from database import get_MhlComments
    
    for videoID in videoIDs:
        comments_df = await get_FhlComments(videoID)
        master_comments_df = await get_MhlComments(videoID)

        hlSenti_df = await performSentiandVoting(master_comments_df,comments_df,videoID)
    
        from database import insert_hlSentiComments    
        await insert_hlSentiComments(hlSenti_df)
        
    completion_message = f"Sentiment Analysis completed for channel: {channelName}."
    await send_telegram_message({"text": completion_message})

    
    
    

    
    
    
    
    
