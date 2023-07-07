import pymongo
import time
import datetime
import pandas as pd
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer
import snscrape.modules.twitter as snt 

#Connect to mongodb
cursor=pymongo.MongoClient("mongodb://localhost:20107/")

#To create Database
Data_base=cursor["TwitterScrapping"]

#Getting into GUI or Webapp
#st.write function will used to write something in the interface
st.write("#TwitterScrapping")

#By using sidebar we getting a input from user how they want to search a data, Time interval, and No of data
title=st.sidebar.title("#Userinput#")

select=st.sidebar.selectbox("How you want to search a data by using?",("keyword","hashtag"))
input=st.sidebar.text_input("Enter a "+ select, "Eg:Balaji")

startdate=st.sidebar.date_input("Select the start date", datetime.date(2019,1,1), key="a1")
enddate=st.sidebar.date_input("select the end date", datetime.date(2023,7,7), key="a2")


no_of_tweet=st.sidebar.number_input("How many data need to scrap", 0, 1000, 5)

#Creating an empty list to store a data scraped from twitter
Tweet=[]

#perform basedupon the input from user
st.subheader("Details")

if select=="keyword":
  st.info("keyword is "+ input)
else:
  st.info("hashtag is "+ input)

st.info("Start date is"+ str(startdate))
st.info("End date is"+ str(enddate))
st.info("No.of.Tweets"+ str(no_of_tweet))

if input:
  if select=="keyword":
    for i, tweet in enumerate(snt.TwitterSearchScraper(f"{input} since:{startdate} until:{enddate}").get_items()):
      if i > no_of_tweet:
        break
      Tweet.append([tweet.id, tweet.date, tweet.content, tweet.url, tweet.user, tweet.replyCount, tweet.retweetCount, tweet.language, tweet.source, tweet.likeCount ])
      Tweetdf=pd.Dataframe(Tweet, columns=["ID", "Date", "Content", "URL", "User", "Replycount", "Retweetcount", "Language", "Source", "LikeCount" ],)
  else:
    for i, tweet in enumerate(snt.TwitterHashtagsScraper(f"{input} since:{startdate} until:{enddate}").get_items()):
      if i > no_of_tweet:
        break
      Tweet.append([tweet.id, tweet.date, tweet.content, tweet.url, tweet.user, tweet.replyCount, tweet.retweetCount, tweet.language, tweet.source, tweet.likeCount ])
      Tweetdf=pd.Dataframe(Tweet, columns=["ID", "Date", "Content", "URL", "User", "Replycount", "Retweetcount", "Language", "Source", "LikeCount" ],)
else:
  st.warning(select, "cant be empty")

st.info("total no of tweets scraped:" + str(len(Tweetdf)-1))

filtered_df = dataframe_explorer(Tweetdf)
if st.sidebar.button("Show Tweets"):
  st.dataframe(filtered_df, use_container_width=True)


#Download JSon
Jsonstrings=Tweetdf.to_json(orient='records')
st.download_button(label="Download data as JSON", file_name="Twitter_data.json", mime="application/json", data=Jsonstrings,)


#upload to database

if st.button("Upload to database"):
  col1=input
  col1=col1.replace(" ","_")+"_Tweets"
  mycol1=Data_base[col1]
  dict=Tweetdf.to_dict("records")
  if dict:
    mycol1.insert_many(dict)
    ts=time.time()
    mycol1.update_many({}, {"$set":{"keyword_or_Hashtag": input + str(ts)}}, upsert=False, array_filters=None,)
    st.success("successfullt uploaded to the database")
    st.balloons()
  else:
    st.warning("Cant upload")

st.subheader("Uploaded Database")

for i in Data_base.list_collection_names():
  mycollection=Data_base[i]
  if st.button(i):
    dfm=pd.DataFrame(list(mycollection.find()))

if not dfm.empty:
  st.write(len(dfm)-1, "Records found")
  st.write(dfm)


#Download Csv

def convertdf(df):
  return df.to_csv().enclose("utf-8")

if not Tweetdf.empty:
  csv=convertdf(Tweetdf)
  st.download_button(label="Download Csv file", data=csv, file_name="Twitter_data.csv", mime="text/csv",)


