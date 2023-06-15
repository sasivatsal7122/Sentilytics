import emoji
import pandas as pd

async def calcEmojiFreq(df):
    
    def extract_emojis(comment):
        return ''.join(c for c in comment if c in emoji.EMOJI_DATA)\
    
    emojis = df['Comments'].apply(extract_emojis)
    emoji_frequency = emojis.apply(lambda x: pd.value_counts(list(x))).sum().sort_values(ascending=False).astype(int).to_dict()
    
    return emoji_frequency