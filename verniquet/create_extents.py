#!/usr/bin/env python3

import logging
import pandas
from pyproj import CRS, Transformer
import yaml
import csv

def main():
    logging.basicConfig(level='DEBUG')
    # the proj string prior to the latest survey => should be updated!
    directory = 'gcps/'
    crs = CRS.from_proj4("+proj=omerc +gamma=0.00047289 +lonc=2.33652588 +lon_0=2.33652588 +lat_0=48.83635612 +lat_ts=48.83635612 +x_0=0 +y_0=0 +to_meter=1.9490363 +no_defs +ellps=GRS80")
    crs_4326 = CRS.from_epsg(4326)
    transformer = Transformer.from_crs(crs, crs_4326)
    result = {}
    for sheet in range(1,73):
        logging.debug(f"Sheet: {sheet}")
        file_name = '{:02}.points'.format(sheet)
        logging.debug(f"  File_name: {file_name}")
        csvFile = pandas.read_csv(directory + file_name,usecols=["mapX","mapY"])
        minX = csvFile["mapX"].min()
        maxX = csvFile["mapX"].max()
        minY = csvFile["mapY"].min()
        maxY = csvFile["mapY"].max()
        print(f'min {minX}, {minY}')
        print(f'max {maxX}, {maxY}')
        min = transformer.transform(minX, minY)
        max = transformer.transform(maxX, maxY)
        print(f'min {min}')
        print(f'max {max}')
        result.update({
            sheet: {
                'mapExtent': {
                    'minX': str(minX),
                    'maxX': str(maxX),
                    'minY': str(minY),
                    'maxY': str(maxY)
                },
                'geoExtent': {
                    'westBoundLongitude': str(min[1]),
                    'eastBoundLongitude': str(max[1]),
                    'southBoundLatitude': str(min[0]),
                    'northBoundLatitude': str(max[0])
                }
            }
        })
    with open('extents.yaml', 'w') as output_file:
        yaml.dump(result, output_file, default_style='"', explicit_start=True, explicit_end=True)
    print("writing csv")
    with open('extents.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sheet', 'min_x', 'min_y', 'max_x', 'max_y'])
        for key in result:
            value = result[key]['mapExtent']
            writer.writerow([str(key), int(float(value['minX'])), int(float(value['minY'])), int(float(value['maxX'])), int(float(value['maxY']))])
    print("wrote csv")

if __name__ == '__main__':
    main()