from flask import Flask, render_template, request, redirect
import json, redis
app = Flask(__name__)
from google.cloud import datastore
from scrape import *
from taskqueue import create_http_task
from datetime import timedelta
import schedule, threading


def get_client():
    return datastore.Client()


def check_cache(type, key):
    redis_client = redis.Redis(host='', port=6379)
    client = get_client()
    response = redis_client.get(type+key)
    if response is None:
        response = client.get(client.key(type, key))
        if response is None:
            return response
        redis_client.set(type+key, json.dumps(response))
        redis_client.expire(type+key, timedelta(seconds=7200))
        print('database')
    else :
        response = json.loads(response)
        print('caching')
    return response

def scrapeAll():
    regions = ['in', 'us']
    languages = ['hi', 'en']
    for gl in regions:
        for hl in languages:
            allApps = None
            while(allApps is None):
                allApps = scrapeTopGames(hl=hl, gl=gl)
            client = get_client()
            topKey = client.key('Keys', hl+gl)
            topKeys = client.get(topKey)
            if(topKeys is None):
                topKeys = datastore.Entity(topKey)
            for types in allApps['category']:
                topKeys[types] = []
                for app in allApps['top'][types]:
                    key = client.key('Game', app['key']+hl+gl)
                    game = client.get(key)
                    if game is None:
                        game = datastore.Entity(key)
                        game['name'] = app['name']
                        game['type'] = app['type']
                        game['rating'] = app['rating']
                        game['logo'] = app['logo']
                        game['id'] = app['key']
                        client.put(game)
                    topKeys[types].append(game)
    # print(topKeys)
    
    client.put(topKeys)
    return 

@app.route('/check', methods=['GET', 'POST'])
def check():
    data = json.loads(request.data)
    print(data)
    hl = data['hl']
    gl = data['gl']
    allApps = None
    while(allApps is None):
        allApps = scrapeTopGames(hl=hl, gl=gl)
    client = get_client()
    topKey = client.key('Keys', hl+gl)
    topKeys = client.get(topKey)
    if(topKeys is None):
        topKeys = datastore.Entity(topKey)
    for types in allApps['category']:
        topKeys[types] = []
        for app in allApps['top'][types]:
            key = client.key('Game', app['key']+hl+gl)
            game = client.get(key)
            if game is None:
                game = datastore.Entity(key)
                game['name'] = app['name']
                game['type'] = app['type']
                game['rating'] = app['rating']
                game['logo'] = app['logo']
                game['id'] = app['key']
                client.put(game)
            topKeys[types].append(game)
    # print(topKeys)
    
    client.put(topKeys)
    return "scraping done"+hl+gl

@app.route('/Scrape')
def scrape():
    hl = request.args.get('hl')
    gl = request.args.get('gl')
    if(hl==None):
        hl='en'
    if(gl==None):
        gl='in'
    payload = {}
    payload['hl']=hl
    payload['gl']=gl
    response = create_http_task(payload)
    return redirect('/?hl='+hl+'&gl='+gl)


@app.route('/', methods=['GET', 'POST'])
def Home():
    hl = request.args.get('hl')
    gl = request.args.get('gl')
    if(hl==None):
        hl='en'
    if(gl==None):
        gl='in'
    
    allApps = check_cache('Keys', hl+gl)
    # print(allApps)
    return render_template('index.html', allApps = allApps, hl=hl, gl=gl)

@app.route('/app_details')
def show_app_details():
    id = request.args.get('id')
    hl = request.args.get('hl')
    gl = request.args.get('gl')
    if(hl==None):
        hl='en'
    if(gl==None):
        gl='in'
    client = get_client()
    detailsKey = client.key('Detail', id+hl+gl)
    game = check_cache('Game', id+hl+gl)
    gamedetail = check_cache('Detail', id+hl+gl)
    if gamedetail is None:
        details = []
        while len(details) == 0:
            details = getAppDetails(id, hl, gl)
        details = details[0]
        gamedetail = datastore.Entity(detailsKey, exclude_from_indexes=('desc', 'images', ))
        gamedetail['desc'] = details['desc']
        gamedetail['images'] = details['images']
        # print(gamedetail['desc'])
        client.put(gamedetail)
    return render_template('appDetails.html', game = game, details=gamedetail, hl=hl, gl=gl)


schedule.every(120).minutes.do(scrapeAll)

def run_scheduled_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    threading.Thread(target=run_scheduled_jobs).start()
    app.run(debug=True)




