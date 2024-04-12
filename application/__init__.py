from flask import Flask, render_template,request, redirect, url_for, jsonify
import requests
from flask_pymongo import PyMongo
from datetime import datetime
from bs4 import BeautifulSoup
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


app = Flask(__name__)
# app.config["SECRET_KEY"] = "0b843bd82ddf4e8fe85e93a77e29e1b73561c06a"
# app.config["MONGO_URI"] = "mongodb://localhost:27017/FlaskApp"

mongo = PyMongo(app,uri="mongodb://localhost:27017/database")
db = mongo.db

from application import routes

class Sentiment():

    def analyze_sentiment_vader(self, paragraph):
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(paragraph)
        compound_score = sentiment['compound']

        # Classify sentiment based on the compound score
        if compound_score > 0:
            return "positive"
        elif compound_score < 0:
            return "negative"
        else:
            return "neutral"

@app.route('/test-sentiment')
def test_sentiment():
    # Sample paragraph
    sample_paragraph = ("Six people went missing from spiritual leader ‘Sadhguru’ Jaggi Vasudev’s Isha Foundation "
                        "centre in Tamil Nadu’s Coimbatore since 2016, but it’s unclear if any of them returned, police have told the Madras High Court."
                        "Police made this submission Thursday before a division bench of Justices M S Ramesh and Sunder Mohan during the hearing of a habeas corpus petition by one Thirumalai, who has sought the whereabouts of his brother, Ganesan."
                        "Thirumalai told the court that his brother, who had been involved in charity work with Isha Foundation since 2007, had gone missing from its centre in Coimbatore in March 2023."
                        "The Tamil Nadu Police, the respondent, submitted that there have been multiple cases of people going missing from the Isha Foundation since 2016."
                        "Represented by Additional Public Prosecutor E Raj Thilak, police indicated that an investigation was ongoing."
                        "However, they mentioned that while some of the missing individuals might have returned, comprehensive details were not readily available."
                        "The bench took note of the police submission and directed them to provide a detailed status report on the ongoing investigation by April 18, the next scheduled hearing."
                        "Thirumalai told the court that it was the foundation that informed him of Ganesan’s two-day unaccounted absence."
                        "Following this, a police complaint was lodged by Dinesh Raja of the Isha Foundation on March 5, 2023, resulting in an FIR for a missing case."
                        "Thirumalai’s petition prayed for urgent court intervention to locate his brother."
                        "According to the missing complaint, Ganesan, left the centre on the evening of February 28, 2023."
                        "It says he took an auto-rickshaw to Poondi Temple at the base of Velliangiri Mountain, and has been missing since."
                        "Reacting to the news, Isha Foundation said that it was “totally false”."
                        "“The news claiming that six people have disappeared from Isha Yoga Center since 2016 is totally false and baseless,” the foundation said in a statement."
                        "The BJD has accused the BJP of misusing ECI's name and threatening Odisha officials on poll duty with transfers if they don't support the party."
                        "BJD leader Sasmit Patra claimed BJP candidates and leaders are using recent transfers as an example."
                        "Patra has written to the CEC, alleging violation of MCC and criminal activity."
                        "BJP denies allegations and challenges BJD to provide proof to ECI.")

    # Create an instance of the Sentiment class
    sen = Sentiment()
    sentiment_classification = sen.analyze_sentiment_vader(sample_paragraph)

    # Return the sentiment classification as a response
    return f"The sentiment classification of the paragraph is: {sentiment_classification}"


