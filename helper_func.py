import re, string, pandas as pd, numpy as np
import emoji
import streamlit as st
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import collections

@st.cache 
def preprocess_data(chat_data):
    # for 12 hr date format:-- 24/04/20, 8:29 pm - msger: msg
    if 'm' in chat_data.split(' - ')[0]: #as in for 'am' and 'pm'
        pattern = '\d{1,2}.\d{1,2}.\d{2},\s\d{1,2}:\d{2}\s..\s-\s'
        time_format = '%d/%m/%y, %H:%M am - '  

    # for 24 gr date format:-- 24/04/20,, 20:29 - msger: msg
    else:
        pattern = '\d{1,2}.\d{1,2}.\d{2},\s\d{1,2}:\d{2}\s-\s'
        time_format = '%d/%m/%y, %H:%M - '
    
    messages = re.split(pattern, chat_data)[1:]
    dates = re.findall(pattern, chat_data)

    df = pd.DataFrame({'date':dates, 'messages':messages})
    df.date = pd.to_datetime(df.date, format=time_format)
    df['time'] = [str(date).split(' ')[1][:-3] for date in df.date]
    df['year'] = df.date.dt.year
    df['month'] = df.date.dt.month
    df['day'] = df.date.dt.day
    df['hour'] = df.date.dt.hour
    df['minute'] = df.date.dt.minute
    df['Day_name'] = df.date.dt.day_name()
    df['week_no'] = np.where(df.day<=7, 'week1', 
                        np.where(df.day<=14, 'week2', 
                        np.where(df.day<=21, 'week3', 
                        np.where(df.day<=28, 'week4', 'week5'))))

    df.month = df.month.map({1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September', 10:'October', 11:'November', 12:'December'})
    
    df['YYYY-mo'] = [str(i)[:7] for i in df.date]
    df['monthYY'] = df.month+(df.year%100).astype('str')

    df.date = [str(date).split(' ')[0] for date in df.date]

    Sender = []
    Message = []

    for message in df.messages:
        msg = message.split(':')
        if msg[1:]:
            Sender.append(msg[0])
            Message.append(msg[1])
        else:
            Sender.append('group')
            Message.append(msg[0])

    df['sender'] = Sender
    df['message'] = Message
    words = []
    for i in range(len(df)):
        words.append(df.iloc[i].message.split(' '))

    df['words'] = words

    df.drop(columns=['messages'], inplace=True)
    return df

def get_grp_stat(df):
    num_msgs = df.shape[0]
    
    words=[]
    for word_list in df.words:
        words.extend(word_list)
    new_words = [i for i in words if i!='']
    num_words = len(new_words)

    num_media = df[df.message==' <Media omitted>\n'].shape[0]

    return num_msgs, num_words, num_media

def get_num_message_df(df):
    return df.groupby('sender').message.count().reset_index()

def get_num_words_df(df):
    n_words=[]
    for sender in df.sender.unique():
        
        words=[]
        new_df = df[df.sender==sender]
        for word_list in new_df.words:
            words.extend(word_list)
        new_words = [i for i in words if i!='']
        n_words.append(len(new_words))
    
    return pd.DataFrame({'Sender':df.sender.unique().tolist(), 'Count':n_words})

def get_num_media_df(df):
    return df[df.message==' <Media omitted>\n'].groupby('sender').message.count().reset_index()

def get_month_yr_grped_msg_df(df):
    df = df.groupby(['monthYY', 'YYYY-mo']).message.count().reset_index().sort_values('YYYY-mo')
    return df
    
def get_month_yr_grped_media_df(df):
    df = df[df.message==' <Media omitted>\n']
    df = df.groupby(['monthYY', 'YYYY-mo']).message.count().reset_index().sort_values('YYYY-mo')
    return df

def get_monthly_trend(df):
    return df.groupby(['monthYY', 'YYYY-mo', 'sender']).message.count().reset_index().sort_values('YYYY-mo')

def get_weekWise_grp_trend(df):
    return df.groupby(['week_no']).message.count().reset_index().sort_values('week_no')

def get_weekWise_trend(df):
    return df.groupby(['week_no', 'sender']).message.count().reset_index().sort_values('week_no')

def get_busiest_day(df):
    individual_most_df = df.groupby(['sender', 'Day_name']).message.count().reset_index().sort_values(['message','sender'], ascending=False).drop_duplicates('sender').reset_index(drop=True)
    total_df = df.groupby(['Day_name']).message.count().reset_index().sort_values(['message'], ascending=False).reset_index(drop=True)
    total_df.columns = ['Day', 'Message Count']
    return individual_most_df, total_df

def get_emoji_insights(df):
    emojis = []
    emoji_sender = []
    for i in range(len(df)):
        if emoji.distinct_emoji_list(df.iloc[i].message):
            emojis.extend([emoji.distinct_emoji_list(df.iloc[i].message)])
            emoji_sender.append(df.iloc[i].sender)
    emoji_df = pd.DataFrame({'Emoji':emojis, 'Emoji_sender':emoji_sender})
    for i in range(len(emoji_df)):
        emoji_df.iloc[i].Emoji = ''.join(emoji_df.iloc[i].Emoji)
    
    emoji_name = []
    for i in range(len(emoji_df)):
        emoji_name.append(emoji.demojize(emoji_df.iloc[i].Emoji))
    emoji_df['Emoji_name'] = emoji_name

    member_emoji_cnt_df = emoji_df.groupby(['Emoji_sender']).Emoji.count().reset_index(name="Emoji_count").sort_values('Emoji_count', ascending=False).head(10).reset_index(drop=True)
    member_emoji_grped_df = emoji_df.groupby(['Emoji_name', 'Emoji_sender']).Emoji_sender.count().reset_index(name="Emoji_count").sort_values('Emoji_count', ascending=False).head(20).reset_index(drop=True)
    most_used_emoji_df = emoji_df.groupby(['Emoji_name']).Emoji_sender.count().reset_index(name="Emoji_count").sort_values('Emoji_count', ascending=False).reset_index(drop=True)
    return emoji_df, member_emoji_cnt_df, member_emoji_grped_df, most_used_emoji_df

def get_word_cloud(df, most_common):
    f = open("Other accessories/Stopwords.txt" ,'r')
    stop_words = f.read()
    maskArray = np.array(Image.open("Other accessories/word_cloud bg_image.png"))

    filtered_chat_words = [word.strip(string.punctuation) for word in ' '.join(df.message.str.lower()).split() if word.strip(string.punctuation) not in stop_words]
    counted_chat_words = collections.Counter(filtered_chat_words)
    word_string = ''
    for word, count in counted_chat_words.most_common(150):
        word_string = word_string+word+' '

    wc = WordCloud(font_path='Other accessories/word_cloud_font.ttf', width = 1000, height = 800, prefer_horizontal = 0.9, max_words = int(most_common), min_font_size=75-int(most_common), max_font_size=250-int(most_common), background_color='#027551', colormap='Set3', mask = maskArray, contour_width=3, contour_color='#DAF0B2', collocations=True, relative_scaling=0.7)
    df_wc = wc.generate(word_string)
    
    # image_colors = ImageColorGenerator(maskArray)
    # wc.recolor(color_func = image_colors)          # to recolor the text as the bg image 
    return df_wc
