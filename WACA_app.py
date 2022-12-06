import streamlit as st
import numpy as np, pandas as pd
import matplotlib.pyplot as  plt
import seaborn as sns
from PIL import Image
import helper_func

page_icon = Image.open('Other accessories/page_icon.png')
st.set_page_config(page_title='WACA-WhatsApp Chat Analyzer', page_icon=page_icon, layout='wide', initial_sidebar_state='collapsed')

import base64
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
        background-position-x: right;
        background-repeat: no-repeat

    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('Other accessories/dashboard_bg_ image.png')   

header = st.container()
user_input = st.container()
user_filters = st.container()
stat_display = st.container()
more_insights = st.container()

with header:
    st.markdown("<h1 style='text-align: center; color:#025E5A;'><u>WhatsApp Chat Analyzer</u></h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color:#2225AD;'><b>Find out insights about your WhatsApp Chat with Peoples</b> </h3>", unsafe_allow_html=True)
    st.markdown('``````````````````````````')


with user_input:
    col4, col1, col2, col3 = st.columns((0.6,7,4.5,0.8))

    col1.markdown("<h4 style='color:#071122;'>:: <u>Steps to follow</u> ::</h4><br>", unsafe_allow_html=True)
    col1.markdown("<h5 style='color:#310822;'><b> 1. Open the chat with the Person, or of a Group,</b> </h5>", unsafe_allow_html=True)
    col1.markdown("<h5 style='color:#310822;'><b> 2. Export Chat.. 'without media' (from three-dot icon),</b> </h5>", unsafe_allow_html=True)
    col1.markdown("<h5 style='color:#310822;'><b> 3. Upload that text file of your chat here...</b> </h5>", unsafe_allow_html=True)
    
    user = col2.text_input('What is your name?')
    uploaded_file = col2.file_uploader('Upload the EXPORTED Chat file')

    if (not user) and (uploaded_file is not None):
        col2.markdown("###### **Make sure you ENTERed YOUR NAME**")
    st.markdown('______________')


if (uploaded_file is not None) and (user !=''):
    chat_data = uploaded_file.getvalue().decode('utf-8')
    chat_df = helper_func.preprocess_data(chat_data)
    wa_inApp_df = chat_df[chat_df.sender=='group']
    chat_df = chat_df[chat_df.sender!='group']

    with stat_display:
        col1, col2, col3 = st.columns(3)

    with user_filters:
        col1, col2, col3 = st.columns(3)
        sender_list = chat_df.sender.unique().tolist()

        n_participants  = len(sender_list)
        sender_list.sort()
        sender_list.insert(0, 'All Participants')
        
        month_list = chat_df.month.unique().tolist()
        year_list = chat_df.year.unique().tolist()
        #to sort the months
        month = ['January','February','March','April','May','June','July','August','September','October','November','December']
        month_list = [i for i in month if i in month_list]
        year_list.sort()
        month_list.insert(0, 'All Months')
        year_list.insert(0, 'All Years')

        if n_participants>10:
            selected_sender = col1.selectbox('Show Analysis for:--', sender_list)
            if selected_sender=='All Participants':
                selected_month = col2.selectbox('Show Analysis for Month:--', month_list)
                selected_year = col3.selectbox('Show Analysis Year:--', year_list)
            
                if selected_month!='All Months':
                    chat_df = chat_df[chat_df.month==selected_month]
                if selected_year!='All Years':
                    chat_df = chat_df[chat_df.year==selected_year]

            num_msgs, num_words, num_media = helper_func.get_grp_stat(chat_df)

            num_msg_df = helper_func.get_num_message_df(chat_df)
            num_msg_df.columns = ['Sender', 'Count']
            num_msg_df.sort_values('Count', ascending=False, inplace=True)
            #inserting overall data at the first row
            top_row = pd.DataFrame({'Sender':['Overall'],'Count':[num_msgs]})
            # Concat with old DataFrame and reset the Index.
            num_msg_df = pd.concat([top_row, num_msg_df]).reset_index(drop = True)
            
            
            num_words_df = helper_func.get_num_words_df(chat_df)
            num_words_df.sort_values('Count', ascending=False, inplace=True)
            #inserting overall data at the first row
            top_row = pd.DataFrame({'Sender':['Overall'],'Count':[num_words]})
            # Concat with old DataFrame and reset the Index.
            num_words_df = pd.concat([top_row, num_words_df]).reset_index(drop = True)
            

            num_media_df = helper_func.get_num_media_df(chat_df)
            num_media_df.columns = ['Sender', 'Count']
            num_media_df.sort_values('Count', ascending=False, inplace=True)
            #inserting overall data at the first row
            top_row = pd.DataFrame({'Sender':['Overall'],'Count':[num_media]})
            # Concat with old DataFrame and reset the Index.
            num_media_df = pd.concat([top_row, num_media_df]).reset_index(drop = True)

            with stat_display:
                if selected_sender == 'All Participants':
                    col1.markdown('')
                    col1.markdown('')
                    col1.markdown("<h5 style='text-align: left;'><b>Total no. of <u>messages</u> sent</b></h3>", unsafe_allow_html=True)
                    col1.dataframe(num_msg_df, 400, 265)
                    
                    col2.markdown('')
                    col2.markdown('')
                    col2.markdown("<h5 style='text-align: left;'><b>Total no. of <u>words</u> typed</b></h3>", unsafe_allow_html=True)
                    col2.dataframe(num_words_df, 400, 265)
                    
                    col3.markdown('')
                    col3.markdown('')
                    col3.markdown("<h5 style='text-align: left;'><b>Total no. of <u>media</u> shared</b></h3>", unsafe_allow_html=True)
                    col3.dataframe(num_media_df, 410, 265)
                else:
                    month_yr_grped_msg_df = helper_func.get_month_yr_grped_msg_df(chat_df[chat_df.sender==selected_sender])
                    month_yr_grped_media_df = helper_func.get_month_yr_grped_media_df(chat_df[chat_df.sender==selected_sender])
                    col2.markdown('')
                    col3.markdown('')
                    col2.markdown('')
                    col3.markdown('')
                    if len(month_yr_grped_msg_df)>1:
                        fig = plt.figure(figsize=(7,4))
                        ax = fig.add_subplot()
                        ax.plot(month_yr_grped_msg_df.monthYY, month_yr_grped_msg_df.message, color='#17ABD7', linewidth=5)
                        plt.title(f'Month-wise msg count of {selected_sender}', fontsize=17, color='#098765', fontweight='bold')
                        plt.xticks(fontsize=15, rotation='vertical')
                        plt.yticks(fontsize=13)
                        col2.pyplot(fig)
                    else:
                        col2.markdown("<h5 style='text-align: center;'><b>Month-wise message count of</b></h3>", unsafe_allow_html=True)
                        col2.markdown(f"<h5 style='text-align: center;'><b>'{selected_sender}'</b></h3>", unsafe_allow_html=True)
                        col2.markdown("--------")
                        if len(month_yr_grped_msg_df)==1:
                            col2.markdown(f"<h4 style='text-align: center; color: #8F2635;'><b>{month_yr_grped_msg_df.message.item()} message(s) <h5>during {month_yr_grped_msg_df.monthYY.item()}</b></h5></h4>", unsafe_allow_html=True)
                        else:
                            col2.markdown("<h4 style='text-align: center; color: #8F2635;'><b>0<h5> message sent</h5></b></h4", unsafe_allow_html=True)

                    
                    if len(month_yr_grped_media_df)>1:
                        fig = plt.figure(figsize=(8,5))
                        ax = fig.add_subplot()
                        ax.plot(month_yr_grped_media_df.monthYY, month_yr_grped_media_df.message, color='#17ABD7', linewidth=5)
                        plt.title(f'Month-wise media count of {selected_sender}', fontsize=17, color='#18AAAA', fontweight='bold')
                        plt.xticks(fontsize=15, rotation='vertical')
                        plt.yticks(fontsize=13)
                        col3.pyplot(fig)
                    else:
                        col3.markdown("<h5 style='text-align: center;'><b>Month-wise media count of</b></h3>", unsafe_allow_html=True)
                        col3.markdown(f"<h5 style='text-align: center;'><b>'{selected_sender}'</b></h3>", unsafe_allow_html=True)
                        col3.markdown("--------")
                        if len(month_yr_grped_media_df)==1:
                            col3.markdown(f"<h4 style='text-align: center; color: #8F2635;'><b>{month_yr_grped_media_df.message.item()} media shared <h5>during {month_yr_grped_media_df.monthYY.item()}</b></h5></h4>", unsafe_allow_html=True)

                        else:
                            col3.markdown("<h4 style='text-align: center; color: #8F2635;'><b>0<h5> media files shared</h5></b></h4", unsafe_allow_html=True)

        else:
            with stat_display:
                #No. of messages by each Participant
                num_msg_df = helper_func.get_num_message_df(chat_df)
                fig = plt.figure(figsize=(8,n_participants+1))
                ax = fig.add_subplot()
                ax.barh(num_msg_df.sender, num_msg_df.message, height=0.8, color='#059E69', edgecolor='black', align='center')
                plt.xticks(fontsize=15)
                plt.yticks(fontsize=20)
                col1.markdown("<h5 style='text-align: center;'><b>No. of <u>messages</u> sent by each Participant</b></h3>", unsafe_allow_html=True)
                col1.pyplot(fig)

                #No. of words sent by each Participant
                num_words_df = helper_func.get_num_words_df(chat_df)
                fig = plt.figure(figsize=(8,n_participants+1))
                ax = fig.add_subplot()
                ax.barh(num_words_df.Sender, num_words_df.Count, height=0.8, color='#843705', edgecolor='black', align='center')
                plt.xticks(fontsize=15)
                plt.yticks(fontsize=20)
                col2.markdown("<h5 style='text-align: center;'><b>Total no. of <u>words</u> typed by each Participant</b></h3>", unsafe_allow_html=True)
                col2.pyplot(fig)

                #No. of media shared by each Participant
                num_media_df = helper_func.get_num_media_df(chat_df)
                if len(num_media_df)>0:
                    fig = plt.figure(figsize=(8,n_participants+1))
                    ax = fig.add_subplot()
                    ax.barh(num_media_df.sender, num_media_df.message, height=0.8, color='#6456AB', edgecolor='black', align='center')
                    plt.xticks(fontsize=15)
                    plt.yticks(fontsize=20)
                    col3.markdown("<h5 style='text-align: center;'><b>No. of <u>media</u> shared by each Participant</b></h3>", unsafe_allow_html=True)
                    col3.pyplot(fig)
                else:
                    col3.markdown("<h5 style='text-align: center;'><b>No. of <u>media</u> shared by each Participant</b></h3>", unsafe_allow_html=True)
                    col3.markdown("----------")
                    col3.markdown("<h1 style='text-align: center; color: #8F2635;'><b>0</h1>", unsafe_allow_html=True)


    with more_insights:
        c_palette = ['#405d27', '#034f84', '#c94c4c', '#ffef96', '#622569', '#ff7b25', '#82b74b', '#80ced6', '#ff1a8c', '#000000']
        st.markdown('~~~~~~~~~~')
        col4, col1, col2, col3, col5 = st.columns((0.5,3,3,5,0.5))
        expand_insight = col1.expander('View More Insights')
        with expand_insight:
            insight = st.radio('Select any one among--', options=[' ', 'Monthly Trend', 'Week-wise Talk', 'Busiest Day', 'Buzziest_times', 'Emoji Insights', 'Generate Word-Cloud'], index=0)

            if insight == 'Monthly Trend' and n_participants<=10:
                monthly_trend_df = helper_func.get_monthly_trend(chat_df)
                fig = plt.figure(figsize=(5,3))
                sns.set_style('darkgrid')
                plot = sns.lineplot(monthly_trend_df.monthYY, monthly_trend_df.message, hue=monthly_trend_df.sender, linewidth=4)
                plot.set_title("Monthly message trend of Members",fontsize=14, fontweight='bold', color='#549DCE')
                plot.set_xlabel('')
                plot.set_xticklabels(fontsize=12, labels=monthly_trend_df.monthYY.unique(), rotation=80)
                plot.set_ylabel('no. of messages sent', fontsize=12, fontweight='bold')
                plot.legend(bbox_to_anchor=(1,1),fontsize=11, title='Sender', title_fontsize = "13")
                col3.pyplot(fig)

            if insight == 'Monthly Trend' and n_participants>10:
                monthly_trend_df = helper_func.get_month_yr_grped_msg_df(chat_df)
                fig = plt.figure(figsize=(7,3))
                plot = sns.lineplot(monthly_trend_df.monthYY, monthly_trend_df.message, linewidth=5, color='#4d004d', marker = "o")
                plot.set_title(f'Monthly message trend of the group', fontsize=15, color='#090172', fontweight='bold')
                plot.set_xlabel('')
                plot.set_ylabel('no. of messages', fontsize=13, fontweight='bold')
                plot.set_xticklabels(fontsize=13, labels=monthly_trend_df.monthYY.unique(), rotation=75)
                col3.pyplot(fig)

            if insight == 'Week-wise Talk':
                selected_year = col2.selectbox('Show Analysis Year:--', year_list, key='yr_inside_expander')
                selected_month = col2.selectbox('Show Analysis for Month:--', month_list, key='mon_inside_expander')
                if selected_year!='All Years':
                    chat_df = chat_df[chat_df.year==selected_year]
                if selected_month!='All Months':
                    chat_df = chat_df[chat_df.month==selected_month]

                sns.set_style('darkgrid')

                if n_participants>10:
                    fig = plt.figure(figsize=(8,4))
                    dateWise_df = helper_func.get_weekWise_grp_trend(chat_df)
                    plot = sns.lineplot(dateWise_df.week_no, dateWise_df.message, linewidth=5, color = '#003366', marker = "o")
                    plot.axes.set_title("Weekwise trend of the group",fontsize=17, fontweight='bold', color='#090172')
                else:
                    fig = plt.figure(figsize=(8,5))
                    dateWise_df = helper_func.get_weekWise_trend(chat_df)
                    plot = sns.lineplot(dateWise_df.week_no, dateWise_df.message, hue=dateWise_df.sender, linewidth=4)
                    plot.axes.set_title("Weekwise trend of the Members",fontsize=17, fontweight='bold', color='#090172')
                    plot.legend(bbox_to_anchor=(1.1,1),fontsize=13, title='Sender', title_fontsize = "14")
                plot.set_xlabel('')
                plot.set_xticklabels(['week1', 'week2', 'week3', 'week4', 'week5'], fontsize=14, fontweight='bold')
                plot.set_ylabel('No. of messages sent', fontsize=15, fontweight='bold')
                col3.pyplot(fig)

            if insight == 'Busiest Day':
                busiestDay_df, all_day_df = helper_func.get_busiest_day(chat_df)
                col2.markdown("<h5 style='text-align: center;'><b>Busiest day of whole chat</b></h3>", unsafe_allow_html=True)
                col2.table(all_day_df)

                busiestDay_df = busiestDay_df[:10]
                busiestDay_df = busiestDay_df.sample(len(busiestDay_df))
                fig = plt.figure(figsize=(7,4))
                plot = sns.barplot(data = busiestDay_df, x='sender', y='message', hue='Day_name', linewidth = 2, dodge=False)
                plot.set_title("Member's most active day", fontsize=17, color='#090172', fontweight='bold')
                plot.set_xlabel('')
                plot.set_ylabel('no. of messages', fontsize=13, fontweight='bold')
                if n_participants>3:
                    plot.set_xticklabels(fontsize=11, fontweight='bold', labels=busiestDay_df.sender, rotation='80')
                else:
                    plot.set_xticklabels(fontsize=11, fontweight='bold', labels=busiestDay_df.sender)

                plot.legend(bbox_to_anchor=(1,1),fontsize=11, title='Day', title_fontsize = "13")
                col3.pyplot(fig)


            if insight == 'Buzziest_times':
                selected_year = col2.selectbox('Show Analysis Year:--', year_list, key='year_inside_expander')
                selected_month = col2.selectbox('Show Analysis for Month:--', month_list, key='mon_inside_expander')
                if selected_year!='All Years':
                    chat_df = chat_df[chat_df.year==selected_year]
                if selected_month!='All Months':
                    chat_df = chat_df[chat_df.month==selected_month]

                fig = plt.figure(figsize=(6,3))
                try:
                    plot = sns.heatmap(chat_df.pivot_table(index='Day_name', columns='hour', values='message', aggfunc='count'),linewidths=.5, cmap="Accent_r")
                    plot.axes.set_title("Most active (Buzziest) hours",fontsize=14, fontweight='bold', color='#800040')
                    plot.set_xlabel('Hours of the Day', fontsize=11, fontweight='bold')
                    plot.set_ylabel('')
                    col3.pyplot(fig)
                except:
                    col3.markdown("")
                    col3.markdown("<h5 style='text-align: center;'><b>No activity in this month</b></h3>", unsafe_allow_html=True)

            if insight == 'Emoji Insights':
                emoji_df, member_emoji_cnt_df, member_emoji_grped_df, most_used_emoji_df = helper_func.get_emoji_insights(chat_df)
                if member_emoji_cnt_df.Emoji_count.max()>1:
                    member_emoji_cnt_df = member_emoji_cnt_df[member_emoji_cnt_df.Emoji_count>=2]
                if member_emoji_grped_df.Emoji_count.max()>1:
                    member_emoji_grped_df = member_emoji_grped_df[member_emoji_grped_df.Emoji_count>=2]
                if most_used_emoji_df.Emoji_count.max()>1:
                    most_used_emoji_df = most_used_emoji_df[most_used_emoji_df.Emoji_count>=2]
                
                if n_participants==2:
                    display_emoji_df = pd.merge(emoji_df, member_emoji_grped_df, how = 'right', on = ['Emoji_name'])

                    fig = plt.figure(figsize=(6,12))
                    plot = sns.barplot(member_emoji_grped_df.Emoji_count, member_emoji_grped_df.Emoji_name, hue=member_emoji_grped_df.Emoji_sender, palette = 'viridis')
                    plot.axes.set_title("Count of top20 Emojis used by the members",fontsize=22, fontweight='bold', color='#090172')
                    plot.set_xlabel('Emoji Count', fontsize=15, fontweight='bold')
                    plot.set_ylabel('Emoji name', fontsize=15, fontweight='bold')
                    plot.set_yticklabels(fontsize=15, labels=member_emoji_grped_df.Emoji_name.unique())
                    plot.legend(bbox_to_anchor=(1,1),fontsize=14, title='Sender', title_fontsize = "15")
                    
                    fig3 = plt.figure(figsize=(2,7))
                    plot3 = plt.pie(most_used_emoji_df.head(5).Emoji_count, labels = most_used_emoji_df.head(5).Emoji_name, colors = sns.color_palette('pastel')[0:5], autopct='%.0f%%', explode=[0.02]*5, textprops = {'color': '#002522','fontsize':7},)
                    
                else:
                    display_emoji_df = pd.merge(emoji_df, most_used_emoji_df, how = 'right', on = ['Emoji_name'])
                    fig = plt.figure(figsize=(7,4))
                    plot = sns.barplot(most_used_emoji_df.Emoji_count, most_used_emoji_df.Emoji_name)
                    plot.axes.set_title("Most Common Emojis, atleast 2 occurrence",fontsize=15, fontweight='bold', color='#090172')
                    plot.set_xlabel('Emoji Count', fontsize=13, fontweight='bold')
                    plot.set_ylabel('Emoji name', fontsize=13, fontweight='bold')
                    plot.set_yticklabels(fontsize=15, labels=most_used_emoji_df.Emoji_name.unique())

                fig2 = plt.figure(figsize=(2,3))
                plot2 = plt.pie(member_emoji_cnt_df.Emoji_count, labels = member_emoji_cnt_df.Emoji_sender, colors = sns.color_palette('pastel')[0:5], autopct='%.0f%%', explode=[0.02]*len(member_emoji_cnt_df), textprops = {'color': '#002522','fontsize':7},)
                
                col2.markdown("<h5 style='text-align: center;'><b>Emoji Reference</b></h3>", unsafe_allow_html=True)
                col2.table(display_emoji_df[['Emoji_name','Emoji']].drop_duplicates('Emoji').reset_index(drop=True))
                col3.write(' ')
                col3.pyplot(fig)
                col2.markdown("<h5 style='text-align: center;'><b>Total emoji Share-ratio</b></h3>", unsafe_allow_html=True)
                col2.pyplot(fig2)

                if n_participants==2:
                    col3.write(' ')
                    col3.markdown("<h5 style='text-align: center;'><b>Most occuring Emojis</b></h3>", unsafe_allow_html=True)
                    col3.pyplot(fig3)

            if insight=='Generate Word-Cloud':
                chosen_sender = col2.selectbox('Show Word-Cloud for:--', sender_list)
                most_common_words = col2.number_input("Generate with 'N' most common words-- ", min_value=10, max_value=70, value = 50, step=10)
                if chosen_sender=='All Participants':
                    wc_df = helper_func.get_word_cloud(chat_df, most_common_words)
                else:
                    wc_df = helper_func.get_word_cloud(chat_df[chat_df.sender==chosen_sender], most_common_words)
                fig4, ax = plt.subplots()
                ax.imshow(wc_df)
                plt.axis('off')
                col3.pyplot(fig4)
                  
