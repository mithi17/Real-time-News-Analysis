from application import app,render_template,request, redirect, url_for,db,datetime,requests,BeautifulSoup,re, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from urllib.parse import urlparse
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# from bson.objectid import ObjectId
# from flask import jsonify

# Download the necessary resources for Vader sentiment analysis

nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()  # Initialize the sentiment analyzer

   
# scheduler = BackgroundScheduler()


@app.route('/', methods=['GET','POST'])

@app.route("/home", methods=["GET","POST"])
def index():
    if request.method == 'POST':
        url = request.form['url']
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        db.home_url.insert_many([{'url': url, 'date_time': now }]) # adding "status: True"
        return redirect(url_for('matches')) 
    return render_template('index.html')

@app.route('/keyword', methods=['GET', 'POST'])
def keyword():
    return render_template('keyword.html')


@app.route('/overview', methods=['GET', 'POST'])
def overview():

    cursor = db.home_url.find()
    url_s = list(cursor)
    
    cursor = db.main_url.find()
    main_urls = list(cursor)
    
    cursor = db.information.find({'author': {'$ne': ''}})
    authors = list(cursor)

    unique_domains = set()  
    for doc in main_urls:
        parsed_url = urlparse(doc['url'])  # Parse the URL
        domain = parsed_url.netloc  # Extract the domain from the parsed URL
        unique_domains.add(domain)  # Add the domain to the set of unique domains

    # Convert the set to a list
    unique = list(unique_domains)

    # Count the number of unique domains
    domain_count = len(unique_domains)

    # Split the list one by one
    split_unique = []
    for domain in unique:
        split_unique.append([domain])

    unique_authors = set()  # Initialize an empty set to store unique non-empty authors
    for doc in authors:
        if doc['author']:  # Check if 'author' field is non-empty
            unique_authors.add(doc['author'])  # Add non-empty author to the set
    
    author_count = len(unique_authors)  # Count the number of unique non-empty authors

    return render_template('overview.html', url_s=url_s, main_urls=main_urls, author_count=author_count, authors=authors, domain_count=domain_count, unique=unique, split_unique=split_unique)

#To add new url in main collection
@app.route('/add', methods=['GET', 'POST'])
def add():
    return render_template('add_url.html')

@app.route('/search', methods=['POST'])
def search_articles():
    keyword = request.form['keyword']
    results = []

    # Perform full-text search in MongoDB
    cursor = db.information.find({"$text": {"$search": keyword}}, {"score": {"$meta": "textScore"}}).sort([("score", {"$meta": "textScore"})])
    # Append search results to the list
    for doc in cursor:
        # print(doc)
        results.append({'paragraph': doc['paragraph'], 'heading': doc['heading'], 'url': doc['url'], 'updated_on': doc['updated_on'], 'author': doc['author'], 'path': doc['path'], 'sentiment': doc['sentiment']},)

    return jsonify(results)

@app.route('/add_url', methods=['POST'])
def add_url():
    url = request.json.get('url')

    # Check if the URL already exists in the main_url collection
    if db.main_url.find_one({'url': url}):
        return jsonify({'error': 'URL already exists'}), 400

    # Save the new URL in the main_url collection
    db.main_url.insert_one({'url': url})
    return jsonify({'message': 'URL added successfully'}), 201


@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        # Get updated data from the frontend
        updated_data = request.get_json()

        # Update MongoDB with the new data
        for item in updated_data:
            field2 = item['date_time']
            url = item['url']
            status = item['status']  # Assuming status is sent from frontend
            db.home_url.update_one({'url': url}, {'$set': {'date_time': field2, 'status': status}})

        return 'updated successfully'

    

@app.route("/info", methods=['GET','POST'])
def matches():
    cursor = db.home_url.find() #{"status": True}
    url_s = list(cursor)
    cursor = db.main_url.find()
    main_urls = list(cursor)
    
    return render_template('Info.html', url_s=url_s, main_urls=main_urls)

@app.route("/main_url", methods=['GET','POST'])
def sub_urls():
    cursor = db.main_url.find()
    main_urls = list(cursor)
    return render_template('main_url.html', main_urls=main_urls)


@app.route("/stored", methods=['GET','POST'])
def main_urls():
    print("main_urls")
    cursor = db.home_url.find({'status': 'True'}) #filter the status to only show true urls
    url_data = list(cursor)
    for url_doc in url_data:
        url = url_doc['url']
        if not url.startswith("https://"):
            url = "https://" + url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and re.match('^https?://', href):
                # Check if the url already exists in the main_url collection
                if db.main_url.find_one({'url': href}):
                    continue                  # Skip the current iteration if the url already exists
                # Save each link as a separate document in the main_url collection
                db.main_url.insert_one({'url': href, 'date_time': url_doc['date_time']})
    sub_url_collection()
    return redirect(url_for('matches')) 

# @app.route("/stored", methods=['GET','POST'])
def sub_url_collection():
    cursor = db.main_url.find()
    main_url_data = list(cursor)
    for main_url_doc in main_url_data:
        response = requests.get(main_url_doc['url'])
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and re.match('^https?://', href):
                # Check if the url already exists in the sub_url collection
                if db.sub_urls.find_one({'url': href}):
                    continue  # Skip the current iteration if the url already exists
                # Save each link as a separate document in the sub_url collection
                db.sub_urls.insert_one({'url': href})
    # return redirect(url_for('matches')) 


@app.route("/informations", methods=['GET','POST'])


def get_information():
    print("get_information")
    cursor = db.sub_urls.find()
    url_links = list(cursor)
    for url_link in url_links:
        url = url_link ['url']
        existing_doc = db.information.find_one({'url': url})
        if existing_doc:
            print("URL already exists, updating...")
            # db.information.update_one(information)
            continue
        else:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch {url}: {response.status_code}")
                continue
            soup = BeautifulSoup(response.content, 'html.parser')

            # author
            editor_div = soup.find('div', class_='editor-details-new-change')
            if editor_div:
                a_tag = editor_div.find('a', class_='bulletProj')
                if a_tag:
                    author_name = a_tag.text.strip()
                else:
                    author_name = "Express Web Desk" if not a_tag else a_tag.text.strip()
            else:
                author_name = ''
                
            # paragraph
            paragraph_texts = []
            paragraph_tags = soup.find_all('p')
            if paragraph_tags:
                paragraph_texts = [tag.get_text(strip=True) for tag in paragraph_tags]
            else:
                paragraph_texts = 'No paragraph Found'
                
            # Initialize variables to count the number of positive, negative, and neutral sentiment categories    
            positive_count = 0
            negative_count = 0
            neutral_count = 0
                
            # Sentiment analysis on each paragraph text
            paragraph_sentiment = []
            sia = SentimentIntensityAnalyzer()
            for paragraph_text in paragraph_texts:
                # Analyze each paragraph for sentiment
                sentiment_scores = sia.polarity_scores(paragraph_text)
                compound_score = sentiment_scores['compound']
                # Determine sentiment category directly in this function
                if compound_score >= 0.05:
                    sentiment_category = 'positive'
                    positive_count += 1
                elif compound_score <= -0.05:
                    sentiment_category = 'negative'
                    negative_count += 1
                else:
                    sentiment_category = 'neutral'
                    neutral_count += 1

                # Append paragraph with sentiment category
                paragraph_sentiment.append({sentiment_category})

            
            
            # Determine the majority sentiment category
            if positive_count > negative_count and positive_count > neutral_count:
                majority_sentiment = 'positive'
            elif negative_count > positive_count and negative_count > neutral_count:
                majority_sentiment = 'negative'
            else:
                majority_sentiment = 'neutral'

            # Save the majority sentiment category in the paragraph_sentiment variable
            paragraph_sentiment = [majority_sentiment]
                
            # date_time
            date_time_span = soup.find('span', {'itemprop': 'dateModified'})
            if date_time_span:
                date_time = date_time_span.get_text().replace('Updated: ', '')
            else:
                date_time = 'No date-time Found'

            # heading
            heading = soup.title.string if  soup.title else ''

            # path
            parsed_url = urlparse(url)
            path = parsed_url.path

            # Split the path into its components and extract the desired elements
            path_elements = path.split('/')
            paths = path_elements[2:3]

            information = {
                'url': url,
                'path': paths,
                'updated_on': date_time,
                'author': author_name,
                'heading': heading if heading else 'No Heading Found!',
                'paragraph': paragraph_texts,
                'sentiment' : paragraph_sentiment,
            }

            existing_docs = db.information.find_one({'url': url})
            if existing_docs:
                db.information.update_one(information)
                print("information, updating...")
            else:
                db.information.insert_one(information)
                
        db.information.create_index( { "url": "text", "updated_on": "text", "author": "text", "heading": "text", "paragraph": "text", "path": "text", "sentiment": "text" } )
        
    
    return redirect(url_for('matches'))

@app.errorhandler(404)
def error404(error):
    return "<h1>Invalid Page 'Error 404!!!'</h1>", 404

@app.errorhandler(500)
def error500(error):
    return "<h1>Template not found :( 'Error 500!!!'</h1>", 500

scheduler = BackgroundScheduler()
scheduler.add_job(sub_url_collection, 'interval', hours=1)
scheduler.add_job(get_information, 'interval', hours=1)
scheduler.start()