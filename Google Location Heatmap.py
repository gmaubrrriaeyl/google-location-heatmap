import json
import pandas as pd
import shapely.geometry as sg
import datetime as dt
import folium
from folium.plugins import HeatMap, heat_map
import os
pd.set_option('display.max_colwidth', None)

os.chdir(r"C:\Users\gabee\OneDrive\Documents\Programming\Python\Google Location History")

##Variables
dataURI = "C:/Users/gabee/OneDrive/Documents/Data/Google/Takeout/Location History/Location History.json"
worldBox = sg.box(-140, -20, 140, 70)

##Helper functions
def pPrint(dictObj):
    print(json.dumps(dictObj, indent=4, sort_keys=True))

def extract_activity(record):
    try:
        return record["activity"][0]["activity"][0]["type"]
    except:
        return "MISSING"



######https://github.com/gboeing/data-visualization/blob/main/location-history/google-location-history-simple.ipynb

def parseData(json):
    df = pd.read_json(json)    
    # parse lat, lon, and timestamp from the dict inside the locations column
    df['lat'] = df['locations'].map(lambda x: x['latitudeE7'])
    df['lon'] = df['locations'].map(lambda x: x['longitudeE7'])
    df['timestamp_ms'] = df['locations'].map(lambda x: x['timestampMs'])

    # convert lat/lon to decimalized degrees and the timestamp to date-time
    df['lat'] = df['lat'] / 10.**7
    df['lon'] = df['lon'] / 10.**7
    df['timestamp_ms'] = df['timestamp_ms'].astype(float) / 1000
    df['datetime'] = df['timestamp_ms'].map(lambda x: dt.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    df = df.drop(labels=['locations', 'timestamp_ms'], axis=1, inplace=False)
    return df

df = parseData(dataURI)
date_range = '{}-{}'.format(df['datetime'].min()[:4], df['datetime'].max()[:4])

####FOLIUM try
map = folium.Map(location=[38.2424, -85.7214])


def drawMap(df):
    """(pd.dataframe) --> .html file
    Plots every data point where the coordinates are different than the previous timestamp's coordinates. 
    Is very slow to execute and will not work for ~>100,000 data points. Automatically stops are 100,000 points.
    See heat map for large data sets
    """
    map = folium.Map(location=[38.2424, -85.7214])
    for i in range(len(df)):
        #Draw lines
        if i == 0:
            x = df.lat.iloc[i]
            y = df.lon.iloc[i]
            folium.Marker([x, y], popup = "location #"+str(i+1)).add_to(map)
            continue
        else:
            #Draw markers
            x = df.lat.iloc[i]
            y = df.lon.iloc[i]
            x2 = df.lat.iloc[i-1]
            y2 = df.lon.iloc[i-1]
            if x2 == x and y2 == y:
                continue
            else:
                folium.Marker([x, y], popup = "location #"+str(i+1)).add_to(map)
                folium.PolyLine(locations = [(x, y), (x2, y2)], line_opacity = .5).add_to(map)
        if i > 10000:
            map.save("map.html")
            break
    map.save("map.html")


##Heat Map
#https://www.kaggle.com/daveianhickey/how-to-folium-for-maps-heatmaps-time-data
heat_df = pd.DataFrame()
heat_df['lat'] = df['lat'].astype(float)
heat_df['lon'] = df['lon'].astype(float)

heat_data = [[row['lat'],row['lon']] for index, row in heat_df.iterrows()]
heatMap = folium.Map(location=[38.2424, -85.7214], zoom_start=10)
HeatMap(heat_data).add_to(heatMap)
heatMap.save("heatmap.html")


#Parsing dates to create filter functions

def createTemporalHeatMap(df, start, end, zoomstart = [38.2424, -85.7214]):
    """
    """
    #Create map
    heatMap = folium.Map(location=zoomstart, zoom_start=10)
    #Create dataframe
    heat_df=pd.DataFrame()
    heat_df['lat'] = df['lat'].astype(float)
    heat_df['lon'] = df['lon'].astype(float)
    heat_df['datetime'] = pd.to_datetime(df['datetime'])
    #Set start and end times
    fileName = start + "-to-" +end
    start = start+ " 00:00:00"
    end = end+ " 23:59:59"
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    #Filter df by start and end dates
    heat_df = heat_df.loc[(heat_df['datetime'] >= start) & (heat_df['datetime']<= end)]
    #Iterate through map and add data if its between start and end
    heat_data = [[row['lat'],row['lon']] for index, row in heat_df.iterrows()]
    HeatMap(heat_data).add_to(heatMap)
    heatMap.save("heatmap"+fileName+".html")


#Pittsburgh heat map
pStart = "2021-07-9"
pEnd = "2021-07-11"
createTemporalHeatMap(df, pStart, pEnd, [40.433, -79.999])
#Hocking Hills heat map
hStart = "2021-10-03"
hEnd = "2021-10-04"
createTemporalHeatMap(df, hStart, hEnd, [39.509076384052534, -82.50102092166583])
