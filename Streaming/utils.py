import os
import gdal
from os import path

from sentinelsat import SentinelAPI
import json
import pandas as pd
import zipfile
import math


def connect_to_api(file):
    with open(file, 'r') as f:
        user_dict = json.load(f)

    user = user_dict[0]['user']
    password = user_dict[0]['pass']
    api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
    return api


def extract_district_polygon(jsonfile, district_name):
    with open(jsonfile) as f:
        district_polygon = json.load(f)

    district_polygon = pd.DataFrame(data=district_polygon, columns=["district", "WKT"])
    district_geojson = district_polygon.loc[district_polygon['district'] == district_name]

    return district_geojson['WKT'].values[0]


def unzip(dir, file):
    if not path.exists("{}/{}.SAFE".format(dir, file)):
        print("unzipping file")
        with zipfile.ZipFile('{}/{}.zip'.format(dir, file), 'r') as zip_ref:
            zip_ref.extractall(dir)


def split_into_tiles(in_path, out_path, filename, n):
    n = int(math.sqrt(n))
    ds = gdal.Open(in_path)
    band = ds.GetRasterBand(1)

    xsize = band.XSize
    ysize = band.YSize

    tile_size_x = xsize // n
    tile_size_y = ysize // n

    for i in range(0, xsize, tile_size_x):
        for j in range(0, ysize, tile_size_y):
            com_string = "gdal_translate -of GTIFF -srcwin " + str(i) + ", " + str(j) + ", " + str(tile_size_x) + ", " + str(tile_size_y) + " " + str(in_path) + " " + str(out_path) + str(filename) + "_"+ str(i/tile_size_x) + "_" + str(j/tile_size_y) + ".tiff"
            os.system(com_string)
