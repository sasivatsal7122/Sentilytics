import re

def FilterDF(df):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # Emojis
                               u"\U0001F300-\U0001F5FF"  # Symbols & Pictographs
                               u"\U0001F680-\U0001F6FF"  # Transport & Map Symbols
                               u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
                               u"\U00002500-\U00002BEF"  # Chinese/Japanese/Korean characters
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # Variation Selectors
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    
    hyperlink_pattern = re.compile(r"http\S+|www\S+")
    unwanted_chars_pattern = re.compile(r"[^a-zA-Z\s]")  # Updated pattern to include digits \d
    
    df['Comments'] = df['Comments'].apply(lambda comment: emoji_pattern.sub(r'', comment))  # Remove emojis
    df['Comments'] = df['Comments'].apply(lambda comment: hyperlink_pattern.sub(r'', comment))  # Remove hyperlinks
    df['Comments'] = df['Comments'].apply(lambda comment: unwanted_chars_pattern.sub(r'', comment))  # Remove unwanted characters
    df['Comments'] = df['Comments'].apply(lambda comment: re.sub(r'\d+', '', comment))  # Remove integers
    df['Comments'] = df['Comments'].apply(lambda comment: re.sub(r'\d+\.\d+', '', comment))  # Remove floats
    
    df['Comments'] = df['Comments'].str.strip().str.lower()
    
    df = df.dropna()  # Drop empty rows
    return df
