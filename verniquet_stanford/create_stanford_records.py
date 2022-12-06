#!/usr/bin/env python3

import json
import logging
import urllib.request
import sys
import os.path
import yaml
import re
import pandas
import xml.etree.ElementTree as ET

def main():
    logging.basicConfig(level='DEBUG')
    collection = "RUMSEY~8~1"
    url = f"https://www.davidrumsey.com/luna/servlet/as/fetchMediaSearch?&sort=Pub_List_No_InitialSort%2CPub_Date%2CPub_List_No%2CSeries_No&lc={collection}&fullData=true&q=Pub_List_No=10110.000&bs=80"
    oai_base_url = "https://www.davidrumsey.com/luna/servlet/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:N/A:"
    associatedResources = [
        {
            'value': "5983d5b5-46f3-4189-925c-c5df8fa36a0b",#Atlas du plan général de la Ville de Paris [exemplaire Stanford G1844.P3 V4 1795 F] 
            'typeOfAssociation': "largerWorkCitation"
        },
        {
            'value': "697871b7-f663-4e0e-8785-c48ecfe05515",#Dossier Verniquet
            'typeOfAssociation': "largerWorkCitation"
        }
    ]
    lineage = pandas.read_csv('../uuids_verniquet.csv',index_col='yaml_identifier')
    with open('../verniquet/extents.yaml', 'r') as extent_file:
        data = yaml.safe_load(extent_file)
    logging.info(f"Loading manifest from URL {url}")
    ns = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'dc': 'http://purl.org/dc/elements/1.1/'}
    result = []
    with urllib.request.urlopen(url) as file:
        manifest = json.loads(file.read().decode("utf-8"))
        for record in manifest:
            id = record.get('id',None)
            logging.debug(f"record id = {id}")
            oai_url = f"{oai_base_url}{id}"
            with urllib.request.urlopen(oai_url) as record_file:
                parser = ET.parse(record_file)
                root = parser.getroot()
                logging.debug(f"root = {root} {root.tag}")
                # getrec= root.find('GetRecord')
                # logging.debug(getrec)
                rec = root.find(".//oai:record", ns)
                logging.debug(f"rec = {rec}")
                metadata = rec.find("oai:metadata", ns)
                logging.debug(f"metadata = {metadata}")
                metadata = metadata.find("oai_dc:dc", ns)
                logging.debug(f"metadata = {metadata}")
                identifiers = metadata.findall("dc:identifier", ns)
                titles = metadata.findall("dc:title", ns)
                formats = metadata.findall("dc:format", ns)
                dates = metadata.findall("dc:date", ns)
                logging.debug(f"titles = {titles}")
                logging.debug(f"identifiers = {identifiers}")
                logging.debug(f"formats = {formats}")
                link = formats[0].text
                logging.debug(f"link = {link}")
                href = re.search('(?<=<a href=)[\w\-\.\/:?=]+', link).group(0)
                logging.debug(f"href = {href}")
                name=titles.pop().text
                logging.debug(f"name = {name}") 
                number=None
                if (name.__contains__("Title")):
                    # name = 'Atlas national de la Ville de Paris, Page de titre [exemplaire Stanford G1844.P3 V4 1795 F]'
                    theoretical_sheet = lineage.loc['TITLE','uuid']
                elif (name.__contains__("Composite:")):
                    # name = 'Atlas national de la Ville de Paris, Carte d\'assemblage [exemplaire Stanford G1844.P3 V4 1795 F]]'
                    theoretical_sheet = None
                else:
                    number = int(re.search('(?<=Sheet )\w+', name).group(0))
                    logging.debug(number)
                    # name = f'Atlas national de la Ville de Paris, feuille N.[uméro] {number} [exemplaire Stanford G1844.P3 V4 1795 F]]'
                    theoretical_sheet = lineage.loc[str(number),'uuid']
                logging.debug(f"  theoretical_sheet: {theoretical_sheet}")
                instance = {
                    'type' : str("Instantiation"), 
                    'identifier': id,
                    'title': name,
                    # 'pub_title': label,
                    'overview': identifiers[1].text,
                    'associatedResource': associatedResources,
                    'keywords': [{'value': 'Instantiation'}],
                    'extent': {'temporalExtent': {'beginPosition': dates[0].text, 'endPosition': dates[1].text}},
                    'distributionInfo': [{
                        'distributionFormat': "JPEG2000",
                        'transferOptions': [{
                            'linkage': href,
                            'protocol': "WWW:LINK",
                            'name': "Scan de la Collection David Rumsey de bibliothèque de l'Université de Stanford",
                            'typeOfTransferOption': "OnlineResource"
                        }]
                    }]
                }
                if (theoretical_sheet):
                    instance.update({'resourceLineage': [theoretical_sheet]})
                if (number):
                    instance.update({'extent': {'geoExtent': data[number]['geoExtent']}})
                    instance.update({'presentationForm': "mapDigital"})
                result.append(instance)

        with open('verniquet_stanford_records.yaml', 'w') as output_file:
            for res in result:
                yaml.dump(res, output_file, explicit_start=True, explicit_end=True)

if __name__ == '__main__':
    main()