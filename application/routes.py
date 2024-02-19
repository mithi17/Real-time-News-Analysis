from application import app,render_template,request, redirect, url_for,db,datetime,requests,BeautifulSoup,re
from apscheduler.schedulers.background import BackgroundScheduler
from urllib.parse import urlparse
from bson.objectid import ObjectId
   
scheduler = BackgroundScheduler()

@app.route('/', methods=['GET','POST'])

@app.route("/home", methods=["GET","POST"])
def index():
    if request.method == 'POST':
        url = request.form['url']
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        db.urls.insert_many([{'url': url, 'date_time': now }])
        return redirect(url_for('matches')) 
    return render_template('index.html')

@app.route("/keys", methods=["GET","POST"])
def keys():
    if request.method == 'POST':
        keyword = request.form['keyword'].split(',')  #split input by comma
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        for keywords in keyword:
            db.key.insert_many([{'keyword': keywords.strip(), 'date_time': now }])  #remove any whitespace using strip()
        return redirect(url_for('matches')) 
    return render_template('index.html')

@app.route("/matches", methods=['GET','POST'])
def matches():
    cursor = db.key.find()
    match_data = list(cursor)
    cursor = db.urls.find()
    url_s = list(cursor)
    info_cursor = db.information.find().sort('_id', 1).limit(1)
    latest_info = list(info_cursor)[0]
    return render_template('index.html', match_data=match_data, latest_info=latest_info, url_s=url_s)

    # return render_template('index.html', match_data=match_data)

@app.route("/stored", methods=['GET','POST'])
def stored():
    cursor = db.urls.find()
    url_data = list(cursor)
    for url_doc in url_data:
        url = url_doc['url']
        if not url.startswith("https://"):
            url = "https://" + url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and re.match('^https?://', href):
                links.append(href)
        # Check if the URL already exists in the url_links collection
        url_exists = db.url_links.find_one({'url': url}, {'_id': 1})
        if url_exists:
            # If the URL exists, update the existing document
            db.url_links.update_one({'url': url}, {'$set': {'links': links, 'date_time': url_doc['date_time']}})
        else:
            # If the URL does not exist, insert a new document
            db.url_links.insert_one({'url': url,'links': links, 'date_time': url_doc['date_time']})
    get_information()
    return redirect(url_for('matches'))

def get_information():
    print("checking completed")
    cursor = db.key.find()
    keywords = list(cursor)
    cursor = db.url_links.find()
    url_links = list(cursor)
    for url_link in url_links:
        url = url_link['url']
        links = url_link['links']
        for link in links:
            if any(keyword_text in link for keyword_text in (keyword['keyword'] for keyword in keywords)):
                if not db.information.find_one({'url': link}):
                    response = requests.get(link)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # author
                    editor_div = soup.find('div', class_='editor-details-new-change')
                    if editor_div:
                        a_tag = editor_div.find('a', class_='bulletProj')
                        if a_tag:
                            author_name = a_tag.text.strip()
                        else:
                            author_name = "Express Web Desk" if not a_tag else a_tag.text.strip()

                    # paragraph
                    paragraph_tags = soup.find_all('p')
                    paragraph_texts = [tag.get_text(strip=True) for tag in paragraph_tags]

                    # date_time
                    date_time_span = soup.find('span', {'itemprop': 'dateModified'})
                    if date_time_span:
                        date_time = date_time_span.get_text().replace('Updated: ', '')
                    else:
                        date_time = ''

                    # heading
                    heading = soup.title.string

                    # path
                    parsed_url = urlparse(url)
                    path = parsed_url.path

                    information = {
                        'keyword': [keyword_text for keyword_text in (keyword['keyword'] for keyword in keywords) if keyword_text in link],
                        'url': link,
                        'path': path,
                        'updated_on': date_time,
                        'author': author_name,
                        'heading': heading,
                        'paragraph': [paragraph_texts]
                    }
                    db.information.insert_one(information)


scheduler = BackgroundScheduler()
scheduler.add_job(get_information, 'interval', hours=3)
scheduler.start()
