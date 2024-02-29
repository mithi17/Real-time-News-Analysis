from application import app,render_template,request, redirect, url_for,db,datetime,requests,BeautifulSoup,re
from apscheduler.schedulers.background import BackgroundScheduler
from urllib.parse import urlparse
from bson.objectid import ObjectId
from flask import jsonify

   
scheduler = BackgroundScheduler()

@app.route('/', methods=['GET','POST'])

@app.route("/home", methods=["GET","POST"])
def index():
    if request.method == 'POST':
        url = request.form['url']
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        db.home_url.insert_many([{'url': url, 'date_time': now }])
        return redirect(url_for('matches')) 
    return render_template('index.html')

# @app.route('/update_table', methods=['POST'])
# def update_table():
#     data = request.get_json()
#     row_index = data['rowIndex']
#     column_index = data['columnIndex']
#     value = data['value']

#     return jsonify({'Updated': 'success'})

@app.route("/keys", methods=["GET","POST"])
def keys():
    if request.method == 'POST':
        keyword = request.form['keyword'].split(',')  #split input by comma
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        for keywords in keyword:
            db.key.insert_many([{'keyword': keywords.strip(), 'date_time': now }])  #remove any whitespace using strip()
        return redirect(url_for('matches')) 
    return render_template('index.html')

@app.route("/info", methods=['GET','POST'])
def matches():
    cursor = db.main_url.find()
    main_urls = list(cursor)
    cursor = db.key.find()
    match_data = list(cursor)
    cursor = db.home_url.find()
    url_s = list(cursor)
    info_cursor = db.information.find().sort('_id', -1).limit(1)
    latest_info = list(info_cursor)[0]
    return render_template('info.html', match_data=match_data, latest_info=latest_info, url_s=url_s, main_urls=main_urls)

    # return render_template('index.html', match_data=match_data)

@app.route("/main_url", methods=['GET','POST'])
def sub_urls():
    cursor = db.main_url.find()
    main_urls = list(cursor)
    return render_template('main_url.html', main_urls=main_urls)

@app.route("/stored", methods=['GET','POST'])
def main_urls():
    cursor = db.home_url.find()
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
                db.sub_urls.insert_one({'url': href, 'date_time': main_url_doc['date_time']})
    # return redirect(url_for('matches'))


@app.route("/informations", methods=['GET','POST'])
def get_information():
    cursor = db.sub_urls.find()
    url_links = list(cursor)
    for url_link in url_links:
        url = url_link['url']
        if not db.information.find_one({'url': url}):
            response = requests.get(url_link['url'])
            # print(url_link)
            soup = BeautifulSoup(response.content, 'html.parser')
            # print(soup)

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
            paragraph_tags = soup.find_all('p')
            if paragraph_tags:
                paragraph_texts = [tag.get_text(strip=True) for tag in paragraph_tags]
            else:
                paragraph_texts = 'No paragraph Found'
                
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

            information = {
                'url': url,
                'path': path,
                'updated_on': date_time,
                'author': author_name,
                'heading': heading if heading else 'No Heading Found!',
                'paragraph': [paragraph_texts]
            }
            db.information.insert_one(information)
    return redirect(url_for('matches'))

# scheduler = BackgroundScheduler()
# scheduler.add_job(get_information, 'interval', hours=3)
# scheduler.start()