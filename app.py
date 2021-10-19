import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import bar_chart_race as bcr
from functools import reduce
import cv2
from wordcloud import WordCloud
from PIL import Image, ImageDraw, ImageFont
from sklearn import preprocessing
import streamlit as st
import time
import graphviz as graphviz
import pydeck as pdk 
import folium
from streamlit_folium import folium_static

# Change the fivicon and title of the page
st.set_page_config(page_title='My personal Twitch Data Analysis',page_icon = "logo.png", layout = 'wide', initial_sidebar_state = 'auto')


# Load all csv files
ads = pd.read_csv("Furraly_ads.csv")
chats = pd.read_csv("Furraly_chats_cheers_sub_notifications.csv")
follow = pd.read_csv("Furraly_follow_unfollow.csv")
watched = pd.read_csv("Furraly_minutes_watched.csv")
pages = pd.read_csv("Furraly_pages_viewed.csv")
played = pd.read_csv("Furraly_video_s_played.csv")

# Create a variable containing all the name of streamers I follow
follow2 = follow["channel"].drop_duplicates()
follow2 = pd.DataFrame(follow2)
follow2_copy = follow2.copy()
follow2_copy = follow2_copy.sort_values(by=["channel"])
follow2 = follow2.append({'channel': "All streamers"}, ignore_index=True)
follow2 = follow2.sort_values(by=["channel"])

# Create some functions
def get_weekday(dt):
    return dt.weekday()

def get_month(dt):
    return dt.month

def get_month2(dt):
    x = dt.month
    if 1 <= x <= 4:
        x = "Start of the year (0,4)"
    elif 5 <= x <= 8:
        x = "Middle of the year (5,8)"
    else:
        x = "End of the year (9,12)"
    return x

def get_dom(dt):
    return dt.day 

def get_year(dt):
    return dt.year

def get_hour(dt):
    return dt.hour

def count_rows(rows):
    return rows["context"].sum() / 60

def count_rows2(rows):
    return rows["event_type"].count()

def summ(total):
    return total["context"].sum()

# Menu 
add_selectbox = st.sidebar.selectbox(
    "Select a page:",
    ("Home","Analyse of my time spend", "Streamers follow", "Ads on Twitch")
)

if add_selectbox == "Home":
    st.image("https://gamernetwork.fr/wp-content/uploads/2020/05/twitch-2.gif", width=600)

    st.markdown('#')
    st.markdown('#')
 
    st.header("How work Twitch ?")
    ################## Create a tree ##################
    graph = graphviz.Digraph()

    graph.edge('Viewer', 'watch a streamer')
    graph.edge('Viewer', 'send a message online')
    graph.edge('preroll ads', 'Viewer')
    graph.edge('watch a streamer', 'preroll ads')
    
    graph.edge('Donation', 'Streamer')
    graph.edge('Viewer', 'Donation')
    graph.edge('send a message online', 'Streamer')
    graph.edge('Streamer', 'send an ad')
    graph.edge('send an ad', 'Viewer')

    st.graphviz_chart(graph)
    with st.expander("Description"):
        st.markdown(""" Twitch is a live streaming service, where streamer and viewers are interconnected. 
        On the platform, we called people who live online **'streamer'**. These people can share what they want. 
        They can show their hobbies in real life, or more often playing video game.
        Also, we called people who watch streamers **'viewers'**, they can interact with the streamer or with other viewers thanks to an online chat.
           """)
        st.image("twitch.png", caption='screenshot of a stream')
        st.markdown("""
        On the graph present above , I will present you the economic system of Twitch. When a viewer wants to watch a streamer he firstly need to watch a pre-roll ad. 
        Then the viewer will be able to watch the content of the streamer. Also, the streamer can send a request ad to all viewers during his session. Finally, streamers live of streaming thanks to donation coming from viewers and the revenue from the ads they sent to viewers . 
        
        """)
        
   
    st.markdown('#')
    st.markdown('#')
    st.markdown('#')
    st.markdown('#')

    
    # Create a map to plot the headquarter of Twitch
    st.header("Localisation of the Twitch seat")
    st.markdown("**Californie** - San Francisco")
    m = folium.Map(location=[37.79123255262682, -122.40349458435077], zoom_start=13)
    icon = folium.features.CustomIcon("logo.png",icon_size=(37, 40))
    folium.TileLayer('cartodbpositron').add_to(m)
    folium.Marker(
        location=[37.79123255262682, -122.40349458435077],popup="<b>Twitch Headquarters</b>", tooltip="Cliquez Ici !",icon=icon).add_to(m)
    folium_static(m)
    


if add_selectbox == "Analyse of my time spend":
    

    
    ################## Create an heatmap ##################
    st.header("Heatmap showing the timespend in hours on Twitch")
    ans = st.select_slider('Choose a year',options=['2015', '2016', '2017', '2018', '2019', '2020', '2021','All'])
    values = st.slider('Choose a period (1:January / 12:December)',1, 12 ,(5, 7))

    values2 = list(range(values[0], values[1]+1))

    watched2 = watched.copy()
    watched2["day"] = pd.to_datetime(watched2["day"])
    watched2["year"] = watched2["day"].map(get_year) 
    watched2["month"] = watched2["day"].map(get_month) 


    if ans != "All":
        watched2 = watched2[watched2["year"] == int(ans)]
        watched2 = watched2[watched2["month"].isin(values2)]
        
    else:
        watched2["year"] = "All"
        watched2 = watched2[watched2["month"].isin(values2)]

    df = watched2.groupby(['year', 'month']).apply(count_rows).unstack() 
    df = df.round(0)
    df = df.rename({1: 'January',2:'February',3:'Mars',4:'April',5:'Mai',6:'June',7:'Jully',8:'Aout',9:'September',10:'October',11:"November",12:"December"}, axis='columns')

    fig3 = go.Figure(data=go.Heatmap(
                    z=df,
                    y=[ans],
                    x=df.columns,
                    hoverongaps = False, 
                    xgap=1,
                    ygap=1,
                    ))
 
    st.plotly_chart(fig3)
    
    st.markdown('#')
    st.markdown('#')

    ################## Create an aera plot ##################
    st.subheader("Aera plot showing the distribution of the number of hours watched on Twitch during the year 2021 ")
    watched3 = watched.copy()
    watched3["day"] = pd.to_datetime(watched3["day"])
    watched3 = watched3.set_index(watched3["day"])
    
    vision = watched3[(watched3["day"] > "2020-12-31")].groupby(["channel_name",pd.Grouper(freq='M')], as_index=True).apply(summ)

    df2 = pd.DataFrame(vision)
    df2 = df2.reset_index()
    df2.columns = "channel","2021 months","time watched in minutes"
    df2["2021 months"] = df2["2021 months"].map(get_month) 

    df2 = pd.merge(df2,follow[['day', 'channel']],on='channel', how='outer')
    df2["day"] = pd.to_datetime(df2["day"])
    df2["day"] = df2["day"].map(get_year)
    
    df2.dropna(subset = ["day"], inplace=True)
    df2.dropna(subset = ["time watched in minutes"], inplace=True)

    df2["day"] = df2["day"].astype(int).round(0)
    df2 = df2.sort_values(by=['day'])
    df2.columns = "channel","2021 months","time watched in minutes","Chain subscription year"

    fig8 = px.area(df2, x="2021 months", y="time watched in minutes", color="Chain subscription year",line_group="channel",width=850,height=700)
    st.plotly_chart(fig8)

    st.markdown('#')
    st.markdown('#')
    
    
    ################## Create a bar plot ##################
    st.subheader("Graph representing the number of hours watched per streamers as a function of periods of 2021")
    watched4 = watched.copy()
    watched4["day"] = pd.to_datetime(watched4["day"])
    watched4 = watched4.set_index(watched4["day"])
    
    vision2 = watched4[(watched4["day"] > "2020-12-31")].groupby(["channel_name",pd.Grouper(freq='M')], as_index=True).apply(summ)

    df3 = pd.DataFrame(vision)
    df3 = df3.reset_index()
    df3.columns = "channel_name","Annee","context"
    df3["Annee"] = df3["Annee"].map(get_month2) 
    df3["context"] = (df3["context"] / 60).round(0)

    df3.columns = ("channel_name","2021 year","Hours")

    fig5 = px.histogram(df3, x='channel_name', y='Hours',color='2021 year')
    fig5.update_layout(xaxis={'categoryorder':'total descending'},width=900,height=700)
    st.plotly_chart(fig5)

    st.markdown('#')    
    st.markdown('#')

    ################## Create a second bar plot ##################
    st.subheader("Graph representing the number of hours watched per streamers as a function of years")
    
    df4 = watched.copy()
    df4["day"] = pd.to_datetime(df4["day"])
    df4 = df4.set_index(df4["day"])
    df4["day"] = df4["day"].map(get_year) 
    df4["context"] = (df4["context"] / 60).round(0)
    
    df4.columns = ("event","Years","device","player","Viewer","channel_name","Hours")
    
    fig6 = px.histogram(df4, x='channel_name', y='Hours',color='Years')
    fig6.update_layout(xaxis={'categoryorder':'total descending'},bargroupgap=0.8,width=800,height=700)
    st.plotly_chart(fig6)

    st.markdown('#')
    st.markdown('#')
    st.markdown('#')
    st.markdown('#')
    
################## Create a personalize bar chart race ##################
    st.header("Create your own bar chart based on the total number of minutes spent on a channel")
    st.markdown('#')
    st.markdown('#')
    
    streamer2 = st.multiselect('Choose some streamers names :',follow2_copy["channel"])
    
    col1,col2 = st.columns(2)
    debut = col1.date_input("Select a start date :")
    fin = col2.date_input("Select a end date :")
    col1,col2,col3 = st.columns(3)
    bar = col2.button("Launch a bar chart race")

    if bar:
        warning = st.warning("video being created, please wait...")

        liste = streamer2
        total = []

        watched["day"] = pd.to_datetime(watched["day"])
        watched = watched[(watched["day"] >= pd.to_datetime(debut)) & (watched["day"] < pd.to_datetime(fin))]

        for i in range (0,len(liste)):
            total.append(watched[(watched["channel_name"] == liste[i])])
            total[i] = total[i].drop(columns=['event_type','device_id','player','user_login','channel_name'])         
            total[i] = total[i].groupby("day",as_index=True).sum() 
        
        fin = reduce(lambda df_left,df_right: pd.merge(df_left, df_right,left_index=True, right_index=True,how='outer'),total)
 
        fin.columns = liste
        fin = fin.fillna(0)
        fin = fin.cumsum()    
        
        # Create a function to plot the total of minutes I have watched for all streamers
        def summary(values, ranks):
            total_minutes = int(round(values.sum(), -2))
            s = f'Total minutes  : {total_minutes: .0f}'
            return {'x': .99, 'y': .05, 's': s, 'ha': 'right', 'size': 8}
 
        st.write(bcr.bar_chart_race(df=fin, sort='asc',period_summary_func=summary))
    
        warning.empty()
        

if add_selectbox == "Streamers follow":
    
################## Create a wordcloud ##################
    st.header("Creating a wordcloud")
    streamer = st.multiselect('Choose some streamers names :',follow2["channel"])
    
    if streamer:
        chats = chats[chats["event_type"] == "chat"]
        
        if "All streamers" not in streamer:    
            chats = chats[chats["channel"].isin(streamer)]
            
        chats["context"] = chats["context"].astype('string')
        chats["context"].dtypes
        text = chats["context"].tolist()
        text = ' '.join([str(item) for item in text])
        mask = np.array(Image.open("logo2.png"))
        mask = cv2.bitwise_not(mask)
        
        # Create a function to change the color of letters
        def random_color_func(word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=None):
            h = int(360.0 * 21.0 / 100)
            s = int(100.0 * 255.0 / 100)
            l = int(100.0 * float(random_state.randint(60, 120)) / 100)

            return "hsl({}, {}%, {}%)".format(h, s, l)

        wordcloud = WordCloud(background_color = '#9924f1',font_path="polic.ttf",color_func=random_color_func, max_words = len(chats),width=1600,mask = mask, height=800,stopwords = ['de','la','c est','il','est','que','va','pour','a',"c'est",'pas','c','le','les','un']).generate(text)
        fig, ax = plt.subplots(figsize=(20,10))
        plt.axis("off")
        plt.imshow(wordcloud)
        st.metric(label="", value="Count of words", delta=len(text))
        st.pyplot(fig)

    st.markdown('#')
    st.markdown('#')
    
################## Create a pie chart ##################
    st.header("Numbers of streamer followed per year")
    follow2 = follow.copy()
    follow2 = follow2[follow2["event_type"] == "follow"]

    follow2["day"] = pd.to_datetime(follow2["day"])
    follow2["day"] = follow2["day"].map(get_year)

    x = follow2.groupby("day").size()

    fig7 = go.Figure(data=[go.Pie(labels=["2016","2017","2018","2019","2020","2021"], values=x, hole=0.5, pull=[0.1, 0.1, 0.1, 0.1,0.03,0])])
    fig7.update_traces(marker=dict(colors=['#03071e','#9d0208','#6a040f','#370617','#ffba08','#d00000']))
    fig7.update_layout(annotations=[dict(text='Total : 98', x=0.5, y=0.5, font_size=20, showarrow=False)])
    fig7.update_traces(textinfo='value')
    st.write(fig7)

################## Creata a sunburst ##################
    st.markdown('#')
    st.markdown('#')
    st.header("Name of streamers followed per year")
    
    follow3 = follow.copy()
    follow3 = follow3[follow3["event_type"] == "follow"]
    follow3 = follow3.drop_duplicates() #ISSUE
    follow3["day"] = pd.to_datetime(follow3["day"])
    
    follow3["day"] = follow3["day"].map(get_year)

    fig10 = px.sunburst(follow3, path=['day','channel'])
    fig10.update_traces(textfont=dict(color="white"))
    st.write(fig10)


if add_selectbox == "Ads on Twitch":
################## Fidelisation by channel ################## 
    st.header("Graphic representing my loyalty by channels")
    test = ads.groupby(["channel","event_type"]).agg('count')
    test = test.reset_index()

    response = test[((test["event_type"] == "video_ad_request_declined") & (test["day"] > 40)) | ((test["event_type"] == "video_ad_request_response") & (test["day"] > 170)) ]
    
    # I delete all these streamers because the bar plot wont be nice to watch
    index_names = response[response['channel'] == "solaryfortnite"].index
    index_names2 = response[response['channel'] == "alexclick"  ].index              
    index_names3 = response[response['channel'] == "rasmelthor" ].index                      
    index_names4 = response[response['channel'] == "alderiate"  ].index                   
    index_names5 = response[response['channel'] == "rocketbaguette"].index
    index_names6 = response[response['channel'] == "lestream"   ].index                   
    index_names7 = response[response['channel'] == "scream"     ].index              
    index_names8 = response[response['channel'] == "squeezie"   ].index                         
                      
    response.drop(index_names, inplace = True)
    response.drop(index_names2, inplace = True)
    response.drop(index_names3, inplace = True)
    response.drop(index_names4, inplace = True)
    response.drop(index_names5, inplace = True)
    response.drop(index_names6, inplace = True)
    response.drop(index_names7, inplace = True)
    response.drop(index_names8, inplace = True)
    
    
    for i in range (0,len(response) - 1):
        if i % 2 == 0:
            numb = response.iloc[i]["day"] + response.iloc[i+1]["day"]
            response.at[response.index[i], "day"] = (response.iloc[i]["day"] * 100) / numb
            if (((response.iloc[i+1]["day"] * 100) / numb) + response.iloc[i]["day"]) < 100:
                response.at[response.index[i+1], "day"] = ((response.iloc[i+1]["day"] * 100) / numb) + 1
            else:
                response.at[response.index[i+1], "day"] = (response.iloc[i+1]["day"] * 100) / numb

    response = response.sort_values(by=["day"])

    response.columns = "channel","event_type","percentages","device_id","player","Viewer","context"

    fig11 = px.bar(response, x="percentages", y="channel",text='percentages', color="event_type",orientation='h', color_discrete_map={'video_ad_request_response': 'rgba(8,230,48,0.53)','video_ad_request_declined': 'rgba(230,18,27,0.95)'})
    fig11.update_layout(barmode='stack',width=900,height=600) 
    st.write(fig11)

    with st.expander("See explanation"):
        st.markdown("""As explain in the main page, streamers are allowed to send an ad for viewers. 
        So the viewer can **visualize** the ad and the server will receive the message **'video_ad_request_response'** . 
        But if he delete the Twitch page he **won't visualize** it, so the server will receive the message **'video_ad_request_declined'**.""")
        st.markdown("This graph is showing if I often accept or decline ads sent from the streamer. Total number of response or decline video request has been converting into percentage.")


################## Time spend on preroll live ads  ################## 
    st.markdown('#')
    st.markdown('#')
    st.header("Graphic showing the total hours spending on pre-roll ads by channels")
    ads2 = ads.copy()
    ads2 = ads2[(ads2["event_type"] == "video_ad_impression") | (ads2["event_type"] == "video_ad_impression_complete")]

    ads2 = ads2.sort_values(by=['channel',"day"])
    ads2["day"] = pd.to_datetime(ads2["day"])

    for i in range (0,len(ads2)-1):
        if (ads2.iloc[i]["event_type"] == "video_ad_impression") & (ads2.iloc[i+1]["event_type"] == "video_ad_impression_complete"):
            ads2.at[ads2.index[i], "sum"] = pd.Timedelta(ads2.iloc[i+1]["day"] - ads2.iloc[i]["day"]).seconds

    ads2.dropna(subset = ["sum"], inplace=True)
    ads2 = ads2.groupby("channel").agg("sum")
    ads2 = ads2.reset_index()

    ads2["sum"] = ads2["sum"] / 3600
    ads2 = ads2.sort_values(by=["sum"])

    test2 = ads2["sum"].sum()
    test2 = test2 / len(ads2)

    fig13 = px.bar(ads2[130:], x="channel", y="sum")
    fig13.update_layout(barmode='stack',width=800,height=600)
    color = ['rgb(158,202,225)']*100
    color[37] = "red"
    color[36] = "red"
    fig13.update_traces(marker_color=color, marker_line_color='rgb(8,48,107)', opacity=0.8)
    fig13.add_shape(type="line",xref="paper",x0=0, y0=test2,x1=1, y1=test2,line=dict(color="magenta",width=2,dash="dash"))
    text=" - - mean of timespend per chains (8h) "
    fig13.add_annotation(x=0,y=170,text=text,xref="paper",font=dict(color="magenta"),showarrow=False,font_size=17)
  
    st.write(fig13)

     

##################Create a scatter plot################## 
    st.markdown('#')
    st.markdown('#')
    st.subheader("Scatter plot showing the total number group by platforms I use to watch Twitch by channels")
    
   
    liste = []
    
    scat = st.multiselect('Choose a streamer name :',follow2["channel"],['All streamers'])
    
    col1,col2,col3,col4,col5 = st.columns(5)
    site = col1.checkbox('site', value=True)
    android = col2.checkbox('android')
    frontpage = col3.checkbox('frontpage')
    mobile_player = col4.checkbox('mobile_player')
    android_pip = col5.checkbox('android_pip')    

    if site:
        liste.append("site")
    if android:
        liste.append("android")
    if frontpage:
        liste.append("frontpage")
    if mobile_player:
        liste.append("mobile_player")
    if android_pip:
        liste.append("android_pip")

    watched5 = watched.copy()
    
    watched5 = watched5[watched5["player"].isin(liste)]

    test3 = watched5.groupby(["channel_name","player"],as_index=False).agg("count")

    le = preprocessing.LabelEncoder()
    le.fit(test3["channel_name"])
    trans = le.transform(test3["channel_name"])
    test3["index"] = trans
                
    if "All streamers" not in scat:
        test3 = test3[test3["channel_name"].isin(scat)]

    fig14 = px.scatter(test3, x="index", y="channel_name",size="event_type",color="player", symbol="player",color_discrete_map={'site': 'rgba(8,230,48,0.42)'})
    fig14.update_layout(yaxis={'categoryorder':'category descending'},shapes=[
 dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=-20,
            y0=0,
            x1=400,
            y1=1,
            fillcolor="steelblue",
            opacity=0.5,
            layer="below",
            line_width=0,
        )],
        width=800,
        height=700)
    st.write(fig14)


##################Create an heatmap for hours ##################   
    st.markdown('#')
    st.markdown('#')
    st.header("Heatmap showing the number of ads I watched during weekdays")
    ans3 = st.select_slider('Choose a year',options=['2015', '2016', '2017', '2018', '2019', '2020', '2021','All'])
    values3 = st.slider('Choose a period (1:January / 12:December)',1, 12 ,(5, 7))

    values4 = list(range(values3[0], values3[1]+1))
    ads3 = ads.copy()

    ads3["day"] = pd.to_datetime(ads3["day"])
    ads3 = ads3.set_index(["day"])

    ads3 = ads3.tz_localize('America/Los_Angeles').tz_convert('Europe/Paris')
    ads3 = ads3[(ads3["event_type"] == "video_ad_impression") | (ads3["event_type"] == "video_ad_request")]
    ads3 = ads3.reset_index()
    ads3["hours"] = ads3["day"].map(get_hour) 
    ads3["week"] = ads3["day"].map(get_weekday)
    ads3["year"] = ads3["day"].map(get_year)
    ads3["month"] = ads3["day"].map(get_month)

    if ans3 != "All":
        ads3 = ads3[ads3["year"] == int(ans3)]
        ads3 = ads3[ads3["month"].isin(values4)]
        
    else:
        ads3["year"] = "All"
        ads3 = ads3[ads3["month"].isin(values4)]

    df5 = ads3.groupby(['hours', 'week']).apply(count_rows2).unstack() #unstack command will change the Hours column to be above and horizontal
    df5 = df5.sort_index()
    df5 = df5.fillna(0)

    fig15 = go.Figure(data=go.Heatmap(
                        z=df5,
                        y=df5.index,
                    x=['Monday', 'Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
                    hoverongaps = False, 
                        
                        colorscale='Viridis'
                        ))
    fig15.update_layout(width=820,height=600)
    st.write(fig15)







