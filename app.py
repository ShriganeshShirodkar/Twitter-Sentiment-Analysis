import os
from flask import Flask, request, render_template, jsonify
#from twitter import TwitterClient

import tweepy
import re
#textblob for sentiment analysis
from textblob import TextBlob
from flask import Flask, render_template,request
from configobj import ConfigObj

config = ConfigObj('config.txt')

#create a twitter app and get authentication details from there and insert them for below keys and secret values accordingly
consumer_key = config['CONSUMER_KEY']
consumer_secret = config['CONSUMER_SECRET']
access_token = config['ACCESS_TOKEN']
access_token_secret = config['ACCESS_TOKEN_SECRET']

#authentication process
auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api=tweepy.API(auth)

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])


def index():
    result=None
    ds={ }
    keys = ['Neutral','Positive','Negative']
    data={key: 0 for key in keys}
    tweets = []
    labels=[]
    values=[]
    if request.method == 'POST':
        result=request.form['thecontent']   #get the value input from website form
        public_tweet=api.search(result+ " -filter:retweets",count=50)     #search tweets regarding that word

        def clean_tweet( tweet):
            return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

        def get_tweet_sentiment( tweet):
            analysis = TextBlob(clean_tweet(tweet))
            if analysis.sentiment.polarity > 0:
                return 'Positive'
            elif analysis.sentiment.polarity == 0:
                return 'Neutral'
            else:
                return 'Negative'

        
        for tweet in public_tweet:
            parsed_tweet = {}
            parsed_tweet['text'] = tweet.text
            
            parsed_tweet['user'] = tweet.user.screen_name    
            parsed_tweet['sentiment'] = get_tweet_sentiment(tweet.text)

            if parsed_tweet['sentiment']=='Neutral':
                data['Neutral']+=1
            elif parsed_tweet['sentiment']=='Positive':
                data['Positive']+=1
            else:
                data['Negative']+=1

            
            tweets.append(parsed_tweet)

        colors = ["#F7464A", "#46BFBD", "#FDB45C"]
        labels=data.keys()
        values=data.values()
        #for tweet in public_tweet:
            
         #   analysis = TextBlob(' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet.text).split()))  #tweet.text gives us those sentences found on twitter
          #  result=analysis.sentiment       #gives the result of polarity
            
           # ds[analysis]=result             #store as key:value pair
            #print ds

            
    return render_template('index.html',result=tweets,values=values, labels= labels)
    #,username=parsed_tweet['user'].values(),sentiments=parsed_tweet['sentiment'] )  #return result back to website
            
    #return jsonify({'data': tweets, 'count': len(tweets)})
port = int(os.environ.get('PORT', 5000))
app.run(host="0.0.0.0", port=port, debug=True)
