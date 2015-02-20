import json
import string
import time

import copytext
import geopy
from flask import Flask, render_template

import settings

app = Flask(__name__)


@app.route('/')
def make_emeddable():
    context = {
        'JSON': getTheJSON()
    }
    return render_template('index.html', **context)

def getTheJSON():
    copy = copytext.Copy(settings.COPYSHEET_LOCATION)
    sheet = copy['Sheet1']
    markers = []
    geocoder = geopy.geocoders.GoogleV3(api_key = settings.GOOGLE_API_KEY)

    startTime = time.clock() # RATE LIMITING
    for row in sheet:
        ### RATE LIMITING ###
        if time.clock() - startTime < 0.2: # rate limited to 5 per second
            sleepTime = .2 - (time.clock() - startTime) # prevent giving time.sleep
                                                        # a negative number
            if sleepTime > 0:
                time.sleep(sleepTime)
        startTime = time.clock()
        #####################

        loc = geocoder.geocode(query = row['Location'].unescape())
        markerToAdd = {}
        markerToAdd['latLong'] = [loc.latitude, loc.longitude]
        popup = []
        if row['Name']:
            popup.append('<b>' + row['Name'].unescape() + '</b><br>')
        for key in row.columns():
            if key != 'Name':
                popup.append('<b>' + key + ': </b>' + row[key].unescape() + '<br>')
            if key.startswith('MarkerFormat:'):
                markerToAdd[key.split()[1]] = row[key].unescape()
        markerToAdd['popUp'] = string.join(popup)
        markers.append(markerToAdd)


    return json.dumps(obj=markers, 
                      ensure_ascii=False, 
                      separators=(',',':'))
        

if __name__ == '__main__':
    app.run(debug=True)