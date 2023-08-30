#!/usr/bin/env python3

import json
import logging
import urllib.request
import sys
import os.path
import yaml
import re
import pandas

def main():
    logging.basicConfig(level='INFO')
    url = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b53243704g/manifest.json"
    associatedResources = [
        {
            'value': "365aa287-517b-4269-80fc-de8e336a52ec",#Atlas du plan général de la Ville de Paris [exemplaire BnF, GE DD-2998 & IFN-53243704] 
            'typeOfAssociation': "largerWorkCitation"
        },
        {
            'value': "697871b7-f663-4e0e-8785-c48ecfe05515",#Dossier Verniquet
            'typeOfAssociation': "largerWorkCitation"
        }
    ]
    exemplary_name = "exemplaire BnF, GE DD-2998 & IFN-53243704"
    lineage = pandas.read_csv('../uuids_verniquet.csv',index_col='yaml_identifier')
    with open('../verniquet/extents.yaml', 'r') as extent_file:
        data = yaml.safe_load(extent_file)
    dataverse = json.loads(open('../verniquet/dataverse.harvard.edu.json').read())
    dataverse_datafileurl = "https://dataverse.harvard.edu/api/access/datafile/"
    def addFiles(prefix, list):
        for e in dataverse["data"]["latestVersion"]["files"]:
            label = e["label"]
            fileId = e["dataFile"]["id"]
            link = dataverse_datafileurl+str(fileId)
            name = None
            if label == prefix + ".jpg.points":
                logging.debug(f"points found: {fileId}")
                name = "Georeferencing point file"
            if label == prefix + ".json":
                logging.debug(f"json found: {fileId}")
                name = "Georeferencing AllMaps annotation file"
            if label == prefix + ".tif":
                logging.debug(f"tif found: {fileId}")
                name = "Georeferenced tiff (geotif)"
            if name:
                list.append({
                        'onlineResources': [{
                            'linkage': link,
                            'protocol': "WWW:LINK",
                            'name': name,
                            'onlineFunctionCode': "download"
                        }]
                })

    logging.info(f"Loading manifest from URL {url}")
    with urllib.request.urlopen(url) as file:
        manifest = json.loads(file.read().decode("utf-8"))
        manifest_id = manifest.get('@id', None)
        logging.info(f"manifest id: {manifest_id}")
        label = manifest.get('label', None)
        logging.debug(f"manifest label: {label}")
        attribution = manifest.get('attribution', None)
        logging.debug(f"manifest attribution: {attribution}")
        related = manifest.get('related', None)
        logging.debug(f"manifest related (Gallica): {related}")
        description = manifest.get('description', None)
        logging.debug(f"manifest description: {description}")
        metadata = manifest.get('metadata', None)
        logging.debug(f"manifest metadata: {metadata}")
        documents = {}
        sequences = manifest.get('sequences', None)
        logging.debug(f"manifest sequences: {len(sequences)}")
        for sequence in sequences:
            canvases = sequence.get('canvases', None)
            for canvas in canvases:
                canvas_id = canvas.get('@id', None)
                logging.info(f"canvas id: {canvas_id}")
                canvas_label = canvas.get('label', None)
                logging.debug(f"  canvas label: {canvas_label}")
                canvas_images = canvas.get('images', None)
                canvas_width = canvas.get('width', None)
                canvas_height = canvas.get('height', None)
                logging.debug(f"  canvas size: {canvas_width} x {canvas_height}")
                canvas_thumbnail = canvas.get('thumbnail', None).get('@id', None)
                logging.debug(f"  canvas thumbnail: {canvas_thumbnail}")
                canvas_native = canvas_images[0].get('resource', None).get('@id',None)
                logging.debug(f"  canvas native: {canvas_native}")
                number = int(re.search('(?<=canvas/f)\w+', canvas_id).group(0))
                logging.debug(f"  canvas number: {number}")
                distributionInfos = [{
                        'distributionFormat': "JPEG",
                        'onlineResources': [{
                            'linkage': canvas_native,
                            'protocol': "WWW:LINK",
                            'name': "Scan de la BnF",
                            'onlineFunctionCode': "download"
                        }]
                    }]
                name = 'inconnu'
                if (number == 1):
                    name = 'Atlas du plan général de la ville de Paris, Page de titre [exemplaire BnF, GE DD-2998 & IFN-53243704]'
                    theoretical_sheet = lineage.loc['TITLE','uuid']
                elif (number == 2):
                    name = 'Atlas du plan général de la ville de Paris, Carte d\'assemblage [exemplaire BnF, GE DD-2998 & IFN-53243704]'
                    theoretical_sheet = lineage.loc['TA','uuid']
                else:
                    name = f'Atlas du plan général de la ville de Paris, feuille N.[uméro] {number-2} [exemplaire BnF, GE DD-2998 & IFN-53243704]'
                    theoretical_sheet = lineage.loc[str(number-2),'uuid']
                    addFiles("f"+str(number),distributionInfos)
                logging.debug(f"  theoretical_sheet: {theoretical_sheet}")
                logging.debug(f"  canvas name: {name}")
                instance = {
                    'type' : str("Instantiation"), 
                    'identifier': canvas_id,
                    'title': name,
                    'pub_title': label,
                    'overview': canvas_thumbnail,
                    'associatedResource': associatedResources,
                    'resourceLineage': [theoretical_sheet],
                    'keywords': [{'value': 'Instantiation'}],
                    'distributionInfo': distributionInfos
                }
                if number>2:
                    instance.update({'extent': {'geoExtent': data[number-2]['geoExtent']}})
                    instance.update({'presentationForm': "mapDigital"})
                documents[instance["identifier"]] = instance

        # Apply the patch file
        with open('verniquet_bnf_records.yaml.patch', 'r') as partial:
            patches = yaml.safe_load_all(partial)
            for p in patches:
                id = p["identifier"]
                documents[id].update(p)

        with open('verniquet_bnf_records.yaml', 'w') as output_file:
            # outputs = yaml.dump(result, output_file, default_style='"', explicit_start=True, encoding='ISO-8859-1')
            for res in documents.values():
                yaml.dump(res, output_file, explicit_start=True, explicit_end=True)

if __name__ == '__main__':
    main()