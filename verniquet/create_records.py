#!/usr/bin/env python3

import logging
import yaml
from datetime import datetime


# Manque Lineage
#   statement = gravé d'après le plan général de la Ville de Paris
#   scope = dataset
def main():
    logging.basicConfig(level="DEBUG")
    with open("extents.yaml", "r") as extent_file:
        data = yaml.safe_load(extent_file)
        events = [
            {"value": datetime.now().strftime("%Y-%m-%d"), "event": "publication"}
        ]
        parisExtent = {
            "westBoundLongitude": "2.2789487344052968",
            "eastBoundLongitude": "2.4080435114903960",
            "southBoundLatitude": "48.8244731921314568",
            "northBoundLatitude": "48.8904078536729116",
        }
        temporalExtent = {"beginPosition": "1784-01-01", "endPosition": "1799-12-31"}
        keywords = [
            {"value": "RecordSet", "typeOfKeyword": "taxon"},
            {"value": "Paris", "typeOfKeyword": "place"},
            {"value": "Verniquet", "typeOfKeyword": "theme"},
        ]
        distributionInfo = {
            "distributor": "The SoDUCo Project",
            "distributor_mail": "contact@geohistoricaldata.org",
        }
        stakeholders = {
            "individuals": [{"role": "originator", "name": "Edme Verniquet"}],
            "organisations": [
                {
                    "role": "publisher",
                    "name": "The SoDUCo project",
                    "mail": "contact@geohistoricaldata.org",
                },
                {
                    "role": "custodian",
                    "name": "The SoDUCo project",
                    "mail": "contact@geohistoricaldata.org",
                },
            ],
        }
        documents = {}
        associatedResource = [
            {
                "value": "6a48afcf-6bdc-4880-b2d6-dd8e557253c2",  # Atlas du plan général de la Ville de Paris
                "typeOfAssociation": "largerWorkCitation",
            },
            {
                "value": "697871b7-f663-4e0e-8785-c48ecfe05515",  # Dossier Verniquet
                "typeOfAssociation": "largerWorkCitation",
            },
        ]
        identifier = "TITLE"
        documents[identifier] = {
            "identifier": identifier,
            "identification": {
                "title": "Atlas national de la Ville de Paris, Page de titre"
            },
            "events": events,
            "extent": {"geoExtent": parisExtent, "temporalExtent": temporalExtent},
            "keywords": keywords,
            "associatedResource": associatedResource,
            "distributionInfo": distributionInfo,
            "stakeholders": stakeholders,
        }

        identifier = "TA"
        documents[identifier] = {
            "identifier": "TA",
            "identification": {
                "title": "Atlas national de la Ville de Paris, Carte d'assemblage"
            },
            "events": events,
            "extent": {"geoExtent": parisExtent, "temporalExtent": temporalExtent},
            "keywords": keywords,
            "associatedResource": associatedResource,
            "distributionInfo": distributionInfo,
            "stakeholders": stakeholders,
        }

        for sheet in range(1, 73):
            logging.debug(f"Sheet: {sheet}")
            name = f"Atlas national de la Ville de Paris, feuille N.[uméro] {sheet}"
            logging.debug(f"  canvas name: {name}")

            identifier = str(sheet)
            documents[identifier] = {
                "identifier": identifier,
                "identification": {"title": name},
                "events": events,
                "extent": {
                    "geoExtent": data[sheet]["geoExtent"],
                    "temporalExtent": temporalExtent,
                },
                "keywords": keywords,
                "associatedResource": associatedResource,
                "distributionInfo": distributionInfo,
                "stakeholders": stakeholders,
            }

        # Apply the patch file
        with open("verniquet_records.yaml.patch", "r") as partial:
            patches = yaml.safe_load_all(partial)
            for p in patches:
                id = p["identifier"]
                documents[id].update(p)

        with open("verniquet_records.yaml", "w") as output_file:
            # outputs = yaml.dump(result, output_file, default_style='"', explicit_start=True, encoding='ISO-8859-1')
            for res in documents.values():
                yaml.dump(res, output_file, explicit_start=True, explicit_end=True, sort_keys=False)


if __name__ == "__main__":
    main()
