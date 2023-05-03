#!/usr/bin/env python3

import logging
import pandas
from pyproj import CRS, Transformer
import json
from os.path import exists

def create_annotation(directory, file_name, id, output_file_name, url, iiif_image_api_version, output_csv, old_format=False):
    source = f"{url}/full/max/0/default.jpg"
    # the proj string prior to the latest survey => should be updated!
    crs = CRS.from_proj4("+proj=omerc +gamma=0.00047289 +lonc=2.33652588 +lon_0=2.33652588 +lat_0=48.83635612 +lat_ts=48.83635612 +x_0=0 +y_0=0 +to_meter=1.9490363 +no_defs +ellps=GRS80")
    crs_4326 = CRS.from_epsg(4326)
    transformer = Transformer.from_crs(crs, crs_4326)
    # old format
    if old_format:
        imageX='pixelX'
        imageY='pixelY'
    else: 
        imageX='sourceX'
        imageY='sourceY'
    csvFile = pandas.read_csv(directory + file_name,usecols=["mapX","mapY",imageX,imageY],comment='#',skip_blank_lines=True)
    features = []
    for index, row in csvFile.iterrows():
        (lat,lon) = transformer.transform(row['mapX'], row['mapY'])
        logging.debug(f"{row['mapX']}, {row['mapY']} => {lat}, {lon}")
        features.append({
            "type": "Feature",
            "properties": {
                "pixelCoords": [round(row[imageX]), -round(row[imageY])]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon,lat]
            }
        })
    minX = round(csvFile[imageX].min())
    maxX = round(csvFile[imageX].max())
    minY = -round(csvFile[imageY].max())
    maxY = -round(csvFile[imageY].min())

    map_minX = csvFile["mapX"].min()
    map_maxX = csvFile["mapX"].max()
    map_minY = csvFile["mapY"].min()
    map_maxY = csvFile["mapY"].max()

    def to_point(df):
        round_df = df.filter(items=['sourceX', 'sourceY']).apply(round)
        round_df['sourceY'] = round_df['sourceY'].apply(lambda x: -x)
        return round_df.values.astype('int').astype(str).tolist()
    
    line = csvFile[csvFile["mapY"] == map_maxY].sort_values(by=["mapX"],ascending=False)
    points = to_point(line)
    line = csvFile[csvFile["mapX"] == map_minX].sort_values(by=["mapY"],ascending=False).iloc[1:, :]
    points.extend(to_point(line))
    line = csvFile[csvFile["mapY"] == map_minY].sort_values(by=["mapX"],ascending=True).iloc[1:, :]
    points.extend(to_point(line))
    line = csvFile[csvFile["mapX"] == map_maxX].sort_values(by=["mapY"],ascending=True).iloc[1:, :]
    points.extend(to_point(line))
    poly = ' '.join(list(map(','.join, points)))
    image_service_type = "ImageService1"
    if (iiif_image_api_version == 2):
        image_service_type = "ImageService1"
    else: 
        if (iiif_image_api_version == 3):
            image_service_type = "ImageService3"
    dictionary = {
        "type": "AnnotationPage",
        "@context": [
            "http://www.w3.org/ns/anno.jsonld"
        ],
        "items": [{
            "type": "Annotation",
            "id": id,
            "@context": [
                "http://www.w3.org/ns/anno.jsonld",
                "http://geojson.org/geojson-ld/geojson-context.jsonld",
                "http://iiif.io/api/presentation/3/context.json"
            ],
            "motivation": "georeferencing",
            "target": {
                "type": "Image",
                "source": source,
                "service": [
                {
                    "@id": url,
                    "type": image_service_type,
                }
                ],
                "selector": {
                "type": "SvgSelector",
                "value": f"<svg width=\"{maxX-minX}\" height=\"{maxY-minY}\"><polygon points=\"{poly}\" /></svg>"
                }
            },
            "body": {
                "type": "FeatureCollection",
                "purpose": "gcp-georeferencing",
                "transformation": {
                    "type": "polynomial",
                    "options": {
                        "order": 2
                    }
                },
                "features": features
            }
        }]
    }
    import os
    os.makedirs(output_file_name.rsplit('/',1)[0],exist_ok=True)
    with open(output_file_name, 'w') as output_file:
        output_file.write(json.dumps(dictionary, indent=2))
    output_csv_file = open(output_csv, 'a')
    output_csv_file.write('#CRS: PROJCRS["unknown",BASEGEOGCRS["unknown",DATUM["Unknown based on GRS80 ellipsoid",ELLIPSOID["GRS 1980",6378137,298.257222101,LENGTHUNIT["metre",1],ID["EPSG",7019]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8901]]],CONVERSION["unknown",METHOD["Hotine Oblique Mercator (variant B)",ID["EPSG",9815]],PARAMETER["Latitude of projection centre",48.83635864,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8811]],PARAMETER["Longitude of projection centre",2.33652533,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8812]],PARAMETER["Azimuth of initial line",0,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8813]],PARAMETER["Angle from Rectified to Skew Grid",0.00047289,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8814]],PARAMETER["Scale factor on initial line",1,SCALEUNIT["unity",1],ID["EPSG",8815]],PARAMETER["Easting at projection centre",0,LENGTHUNIT["unknown",1.9490363],ID["EPSG",8816]],PARAMETER["Northing at projection centre",0,LENGTHUNIT["unknown",1.9490363],ID["EPSG",8817]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["unknown",1.9490363]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["unknown",1.9490363]],REMARK["PROJ CRS string: +proj=omerc +gamma=0.00047289 +lonc=2.33652533 +lon_0=2.33652533 +lat_0=48.83635864 +x_0=0 +y_0=0 +no_defs +ellps=GRS80 +to_meter=1.9490363"]]\n')
    csvFile.to_csv(output_csv_file,index=False)
    output_csv_file.close()
    return {
        "id": id, 
        "source": source, 
        "url": url, 
        "image_type":image_service_type, 
        "width": maxX-minX, 
        "height": maxY-minY, 
        "polygon": poly,
        "features": features
    }
def main():
    logging.basicConfig(level='DEBUG')
    entries = []
    source = 'bnf'
    output_directory = 'output'
    if source == 'rumsey':
        #rumsey
        output_directory = 'output/rumsey'
        directory = 'gcps_rumsey/'
        for sheet_number in range(1, 73):
            file_name = '{}.jp2.points'.format(sheet_number+10110001)
            id = 'verniquet_rumsey_{}'.format(str(sheet_number).zfill(2))
            #output_file_name = 'annotation_verniquet_rumsey/annotation_verniquet_rumsey_{}.json'.format(str(sheet_number).zfill(2))
            output_file_name = output_directory + '/{}/{}.json'.format(str(sheet_number).zfill(2),sheet_number+10110001)
            output_csv_file_name = output_directory + '/{}/{}.jp2.points'.format(str(sheet_number).zfill(2),sheet_number+10110001)
            sheetIdDf = pandas.read_csv('../uuids_verniquet_stanford.csv',usecols=["yaml_identifier"],skip_blank_lines=True)
            sheetIdList = sheetIdDf.drop(sheetIdDf.index[[0]])['yaml_identifier'].tolist()
            url = 'https://www.davidrumsey.com/luna/servlet/iiif/{}'.format(sheetIdList[sheet_number])
            if not exists(directory + file_name):
                logging.debug(f"  Skipping missing file: {directory + file_name}")
            else: 
                logging.debug(f"  Creating annotation for file: {directory + file_name}")
                entry = create_annotation(directory, file_name, id, output_file_name, url, iiif_image_api_version=3, output_csv=output_csv_file_name)
                entries.append(entry)
        items = []
        for entry in entries:
            item = {
                "type": "Annotation",
                "id": entry['id'],
                "@context": [
                    "http://www.w3.org/ns/anno.jsonld",
                    "http://geojson.org/geojson-ld/geojson-context.jsonld",
                    "http://iiif.io/api/presentation/3/context.json"
                ],
                "motivation": "georeferencing",
                "target": {
                    "type": "Image",
                    "source": entry['source'],
                    "service": [
                    {
                        "@id": entry['url'],
                        "type": entry['image_type'],
                        "profile": "http://iiif.io/api/image/3/level2.json"
                    }
                    ],
                    "selector": {
                    "type": "SvgSelector",
                    "value": f"<svg width=\"{entry['width']}\" height=\"{entry['height']}\"><polygon points=\"{entry['polygon']}\" /></svg>"
                    }
                },
                "body": {
                    "type": "FeatureCollection",
                    "purpose": "gcp-georeferencing",
                    "transformation": {
                        "type": "polynomial",
                        "options": {
                            "order": 2
                        }
                    },
                    "features": entry['features']
                }
            }
            items.append(item)
        dictionary = {
            "type": "AnnotationPage",
            "@context": [
                "http://www.w3.org/ns/anno.jsonld"
            ],
            "items": items
        }
        #output_file_name = 'annotation_verniquet_rumsey/annotation_verniquet_rumsey.json'
        output_file_name = output_directory + '/annotation_verniquet_rumsey.json'
        with open(output_file_name, 'w') as output_file:
            output_file.write(json.dumps(dictionary, indent=2))
    elif source == 'bnf':
        for sheet_number in range(1, 73):
            #bnf
            output_directory = 'output/bnf'
            directory = 'gcps_bnf/'
            file_name = 'f{}.jpg.points'.format(sheet_number+2)
            id = 'verniquet_bnf_{}'.format(str(sheet_number).zfill(2))
            #output_file_name = 'annotation_verniquet_bnf/annotation_verniquet_bnf_{}.json'.format(str(sheet_number).zfill(2))
            output_file_name = output_directory + '/{}/f{}.json'.format(str(sheet_number).zfill(2),sheet_number+2)
            output_csv_file_name = output_directory + '/{}/f{}.jpg.points'.format(str(sheet_number).zfill(2),sheet_number+2)
            #url = 'https://iiif.geohistoricaldata.org/iiif/3/ATLAS_NATIONAL_DE_LA_VILLE_DE_PARIS_BNF_28.jpg'
            #url = 'http://localhost:8000/12148/btv1b53243704g/f{}'.format(sheet_number+2)
            url = 'https://gallica.bnf.fr/iiif/ark:/12148/btv1b53243704g/f{}'.format(sheet_number+2)
            if not exists(directory + file_name):
                logging.debug(f"  Skipping missing file: {directory + file_name}")
            else: 
                logging.debug(f"  Creating annotation for file: {directory + file_name}")
                entry = create_annotation(directory, file_name, id, output_file_name, url, iiif_image_api_version=1,output_csv=output_csv_file_name)
                entries.append(entry)
        items = []
        for entry in entries:
            item = {
                "type": "Annotation",
                "id": entry['id'],
                "@context": [
                    "http://www.w3.org/ns/anno.jsonld",
                    "http://geojson.org/geojson-ld/geojson-context.jsonld",
                    "http://iiif.io/api/presentation/3/context.json"
                ],
                "motivation": "georeferencing",
                "target": {
                    "type": "Image",
                    "source": entry['source'],
                    "service": [
                    {
                        "@id": entry['url'],
                        "type": entry['image_type'],
                    }
                    ],
                    "selector": {
                    "type": "SvgSelector",
                    "value": f"<svg width=\"{entry['width']}\" height=\"{entry['height']}\"><polygon points=\"{entry['polygon']}\" /></svg>"
                    }
                },
                "body": {
                    "type": "FeatureCollection",
                    "purpose": "gcp-georeferencing",
                    "transformation": {
                        "type": "polynomial",
                        "options": {
                            "order": 2
                        }
                    },
                    "features": entry['features']
                }
            }
            items.append(item)
        dictionary = {
            "type": "AnnotationPage",
            "@context": [
                "http://www.w3.org/ns/anno.jsonld"
            ],
            "items": items
        }
        #output_file_name = 'annotation_verniquet_bnf/annotation_verniquet_bnf.json'
        output_file_name = output_directory + '/annotation_verniquet_bnf.json'
        with open(output_file_name, 'w') as output_file:
            output_file.write(json.dumps(dictionary, indent=2))


if __name__ == '__main__':
    main()