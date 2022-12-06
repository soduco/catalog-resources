#!/usr/bin/env python3

import logging
import yaml

# Manque Lineage
#   statement = gravé d'après le plan général de la Ville de Paris
#   scope = dataset
def main():
    logging.basicConfig(level='DEBUG')
    with open('extents.yaml', 'r') as extent_file:
        data = yaml.safe_load(extent_file)
        result = []
        associatedResource = [
            {
                'value': "6a48afcf-6bdc-4880-b2d6-dd8e557253c2",#Atlas du plan général de la Ville de Paris
                'typeOfAssociation': "largerWorkCitation"
            },
            {
                'value': "697871b7-f663-4e0e-8785-c48ecfe05515",#Dossier Verniquet
                'typeOfAssociation': "largerWorkCitation"
            }
        ]
        result.append({
            # 'type' : str("Instantiation"), 
            'identifier': 'TITLE',
            'title': 'Atlas national de la Ville de Paris, Page de titre',
            'associatedResource': associatedResource,
            'keywords': [{'value': 'RecordSet'}]
        })
        result.append({
            # 'type' : str("Instantiation"), 
            'identifier': 'TA',
            'title': 'Atlas national de la Ville de Paris, Carte d\'assemblage',
            'associatedResource': associatedResource,
            'keywords': [{'value': 'RecordSet'}]
        })
        for sheet in range(1,73):
            logging.debug(f"Sheet: {sheet}")
            name = f'Atlas national de la Ville de Paris, feuille N.[uméro] {sheet}'
            logging.debug(f"  canvas name: {name}") 
            result.append({
                # 'type' : str("Instantiation"), 
                'identifier': str(sheet),
                'title': name,
                'associatedResource': associatedResource,
                'extent': {'geoExtent': data[sheet]['geoExtent']},
                'keywords': [{'value': 'RecordSet'}]
            })
        with open('verniquet_records.yaml', 'w') as output_file:
            # outputs = yaml.dump(result, output_file, default_style='"', explicit_start=True, encoding='ISO-8859-1')
            for res in result:
                yaml.dump(res, output_file, explicit_start=True, explicit_end=True)

if __name__ == '__main__':
    main()