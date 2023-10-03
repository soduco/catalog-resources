#!/usr/bin/env python3

import json
import logging
import re
import urllib.request
from datetime import datetime

import pandas
import yaml


def main():
    logging.basicConfig(level='INFO')
    url = "https://gallica.bnf.fr/iiif/ark:/12148/btv1b53243704g/manifest.json"
    events = [
        {
            "value": str(datetime.now().strftime("%Y-%m-%d")),
            "event": str("publication")
        }
    ]
    temporal_extent = {"beginPosition": "1784-01-01", "endPosition": "1799-12-31"}
    paris_extent = {
        "westBoundLongitude": "2.2789487344052968",
        "eastBoundLongitude": "2.4080435114903960",
        "southBoundLatitude": "48.8244731921314568",
        "northBoundLatitude": "48.8904078536729116",
    }
    keywords = [
        {"value": "Instantiation", "typeOfKeyword": "taxon"},
        {"value": "Paris", "typeOfKeyword": "place"},
        {"value": "Verniquet", "typeOfKeyword": "theme"},
    ]
    stakeholders = {
        "individuals": [{"role": "originator", "name": "Edme Verniquet"}],
        "organisations": [
            {
                "role": "publisher",
                "name": "The SoDUCo project",
                "mail": "contact@geohistoricaldata.org",
                "logo": "https://catalog.geohistoricaldata.org/geonetwork/images/harvesting/soduco.png",
            },
            {
                "role": "custodian",
                "name": "The SoDUCo project",
                "mail": "contact@geohistoricaldata.org",
                "logo": "https://catalog.geohistoricaldata.org/geonetwork/images/harvesting/soduco.png",
            },
        ],
    }
    associated_resources = [
        {
            'value': "365aa287-517b-4269-80fc-de8e336a52ec",
            # Atlas du plan général de la Ville de Paris [exemplaire BnF, GE DD-2998 & IFN-53243704]
            'typeOfAssociation': "largerWorkCitation"
        },
        {
            'value': "697871b7-f663-4e0e-8785-c48ecfe05515",  # Dossier Verniquet
            'typeOfAssociation': "largerWorkCitation"
        }
    ]
    # exemplary_name = "exemplaire BnF, GE DD-2998 & IFN-53243704"
    lineage = pandas.read_csv('../uuids_verniquet.csv', index_col='yaml_identifier')
    with open('../verniquet/extents.yaml', 'r') as extent_file:
        data = yaml.safe_load(extent_file)
    dataverse = json.loads(open('../verniquet/dataverse.harvard.edu.json').read())
    dataverse_data_file_url = "https://dataverse.harvard.edu/api/access/datafile/"

    def add_files(prefix, resource_list):
        for e in dataverse["data"]["latestVersion"]["files"]:
            dataverse_label = e["label"]
            dataverse_file_id = e["dataFile"]["id"]
            link = dataverse_data_file_url + str(dataverse_file_id)
            resource_name = None
            if dataverse_label == prefix + ".jpg.points":
                logging.debug(f"points found: {dataverse_file_id}")
                resource_name = "Georeferencing point file"
            if dataverse_label == prefix + ".json":
                logging.debug(f"json found: {dataverse_file_id}")
                resource_name = "Georeferencing AllMaps annotation file"
            if dataverse_label == prefix + ".tif":
                logging.debug(f"tif found: {dataverse_file_id}")
                resource_name = "Georeferenced tiff (geotif)"
            if resource_name:
                resource_list.append({
                        'linkage': link,
                        'protocol': "WWW:DOWNLOAD",
                        'name': resource_name,
                        'onlineFunctionCode': "download"
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
                canvas_native = canvas_images[0].get('resource', None).get('@id', None)
                logging.debug(f"  canvas native: {canvas_native}")
                number = int(re.search('(?<=canvas/f)\w+', canvas_id).group(0))
                logging.debug(f"  canvas number: {number}")
                online_resources = [{
                    'linkage': canvas_native,
                    'protocol': "WWW:DOWNLOAD",
                    'name': "Scan de la BnF",
                    'onlineFunctionCode': "download"
                }]
                # name = 'inconnu'
                if number == 1:
                    name = 'Atlas du plan général de la ville de Paris, Page de titre [exemplaire BnF, GE DD-2998 & IFN-53243704]'
                    theoretical_sheet = lineage.loc['TITLE', 'uuid']
                elif number == 2:
                    name = 'Atlas du plan général de la ville de Paris, Carte d\'assemblage [exemplaire BnF, GE DD-2998 & IFN-53243704]'
                    theoretical_sheet = lineage.loc['TA', 'uuid']
                else:
                    name = f'Atlas du plan général de la ville de Paris, feuille N.[uméro] {number - 2} [exemplaire BnF, GE DD-2998 & IFN-53243704]'
                    theoretical_sheet = lineage.loc[str(number - 2), 'uuid']
                    add_files("f" + str(number), online_resources)
                logging.debug(f"  theoretical_sheet: {theoretical_sheet}")
                logging.debug(f"  canvas name: {name}")
                instance = {
                    'identifier': canvas_id.replace("https://gallica.bnf.fr/iiif/ark:/","").replace("/","_"),
                    "identification": {
                        "title": name
                    },
                    "events": events,
                    "keywords": keywords,
                    'pub_title': label,
                    'overview': canvas_thumbnail,
                    'associatedResource': associated_resources,
                    'resourceLineage': [theoretical_sheet],
                    "stakeholders": stakeholders,
                    'distributionInfo': {
                        "distributor": "The SoDUCo Project",
                        "distributor_mail": "contact@geohistoricaldata.org",
                        "distributor_logo": "https://catalog.geohistoricaldata.org/geonetwork/images/harvesting/soduco.png",
                        'distributionFormat': "JPEG",
                        'onlineResources': online_resources
                    }
                }
                if number > 2:
                    instance.update({'presentationForm': "mapDigital"})
                    instance.update(
                        {"extent": {
                            "geoExtent": data[number - 2]['geoExtent'],
                            "temporalExtent": temporal_extent
                        }}
                    )
                    instance.update({"presentationForm": "mapDigital"})
                else:
                    instance.update(
                        {"extent": {"geoExtent": paris_extent, "temporalExtent": temporal_extent}})
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
                yaml.dump(res, output_file, explicit_start=True, explicit_end=True, sort_keys=False)


if __name__ == '__main__':
    main()
