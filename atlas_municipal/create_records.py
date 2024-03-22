#!/usr/bin/env python3

import logging
import yaml
from datetime import datetime
import csv
import os
import sys
import json
def main():
  logging.basicConfig(level="DEBUG")
  # FIXME attantion le plan général n'a pas les mêmes planches que les atlas qui s'appuient dessus!
  # TODO gérer les parcs qui sont présents dans les derniers atlas...
  with open("atlas_municipal_entents.json", "r") as extent_file:
    extents = json.load(extent_file)
  events = [
    {"value": datetime.now().strftime("%Y-%m-%d"), "event": "publication"}
  ]
  # TODO review this extent to include the parks
  parisExtent = {
    "westBoundLongitude": "2.2434847",
    "eastBoundLongitude": "2.4178524",
    "southBoundLatitude": "48.8150095",
    "northBoundLatitude": "48.9033812",
  }
  keyword_file = {"value": "file", "typeOfKeyword": "taxon"}
  keyword_recordset = {"value": "RecordSet", "typeOfKeyword": "taxon"}
  keyword_record = {"value": "Record", "typeOfKeyword": "taxon"}
  keyword_instantiation = {"value": "Instantiation", "typeOfKeyword": "taxon"}
  keyword_paris = {"value": "Paris", "typeOfKeyword": "place"}
  keywords_atlas = {"value": "Atlas Municipal", "typeOfKeyword": "theme"}
  distributionInfo = {
      "distributor": "The SoDUCo Project",
      "distributor_mail": "contact@geohistoricaldata.org",
      "distributor_logo": "https://catalog.geohistoricaldata.org/geonetwork/images/harvesting/soduco.png",
  }
  processorInfo = {
      "processor": "The SoDUCo Project",
      "processor_mail": "contact@geohistoricaldata.org",
      "processor_logo": "https://catalog.geohistoricaldata.org/geonetwork/images/harvesting/soduco.png",
  }
  stakeholders = {
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
  # Série basée sur le plan https://bibliotheques-specialisees.paris.fr/ark:/73873/pf0000935006
  # commencé en 1857 et terminé en 1865
  csv_path = "atlas_municipal_list.csv"
  if not os.path.exists(csv_path):
    sys.exit("No csv at this path")
  filename = open(csv_path, "r", encoding="utf8")
  file = csv.DictReader(filename)
  def create_temporalExtent(start:int, end: int):
    return {"beginPosition": f"{start}-01-01", "endPosition": f"{end}-12-31"}
  atlas_municipal_entries=[]
  for row in file:
    identifier = row["identifier"]
    entry_type = row["type"]
    entry_start = row["date_start"]
    entry_end = row["date_end"]
    if not entry_end:
      entry_end = entry_start
    print(f"Dates = {entry_start} - {entry_end}")
    entry_title = row["title"]
    entry_abstract = row["abstract"]
    entry_ark = row["ark"]
    entry_annotation = row["annotation_file"]
    entry_wms = row["wms_id"]
    entry_iiif = row["iiif_base"]
    entry_diff = row["diff_image_sheet"]
    entry_largerWorkCitation = row["largerWorkCitation"]
    entry_resourceLineage = row["resourceLineage"]
    if entry_type == "file":
      # create a record for the atlas_municipal file
      entry = {
        "identifier": identifier,
        "identification": {"title": f"({identifier}) {entry_title}"},
        "abstract": f"{entry_abstract}",
        "events": events,
        "extent": {
            "geoExtent": parisExtent,
            "temporalExtent": create_temporalExtent(entry_start, entry_end),
        },
        "keywords": [keyword_paris, keywords_atlas, keyword_file],
        "distributionInfo": distributionInfo.copy(),
        "stakeholders": stakeholders,
      }
      atlas_municipal_entries.append(entry)
    else:
      entry = {
        "identifier": identifier,
        "identification": {"title": f"({identifier}) {entry_title}"},
        "abstract": f"{entry_abstract}",
        "events": events,
        "extent": {
            "geoExtent": parisExtent,
            "temporalExtent": create_temporalExtent(entry_start, entry_end),
        },
        "keywords": [keyword_paris, keywords_atlas, keyword_record],
        "distributionInfo": distributionInfo.copy(),
        "stakeholders": stakeholders,
        "associatedResource": [{
          "value": f"{entry_largerWorkCitation}",
          "typeOfAssociation": "largerWorkCitation"
        }]
      }
      if entry_resourceLineage:
        entry["resourceLineage"] = [entry_resourceLineage]
      atlas_municipal_entries.append(entry)
      # iterate over sheets
      for sheet_number in range(1,17):
        sheet_identifier = f"{identifier}_{sheet_number:02d}"
        if str(sheet_number) in extents:
          extent = extents[str(sheet_number)]
        sheet_entry = {
          "identifier": sheet_identifier,
          "identification": {"title": f"({sheet_identifier}) {entry_title}. Feuille {sheet_number:02d}"},
          "abstract": f"{entry_abstract}",
          "events": events,
          "extent": {
              "geoExtent": extent,
              "temporalExtent": create_temporalExtent(entry_start, entry_end),
          },
          "keywords": [keyword_paris, keywords_atlas, keyword_record],
          "distributionInfo": distributionInfo.copy(),
          "stakeholders": stakeholders,
          "associatedResource": [{
            "value": f"{identifier}",
            "typeOfAssociation": "largerWorkCitation"
          }]
        }
        atlas_municipal_entries.append(sheet_entry)
      entry_bhdv_exemplar_identifier = f"{identifier}_BHdV"
      entry_bhdv_exemplar = {
        "identifier": entry_bhdv_exemplar_identifier,
        "identification": {"title": f"({entry_bhdv_exemplar_identifier}) {entry_title}. Exemplaire Ville de Paris / BHdV."},
        "abstract": f"{entry_abstract}",
        "events": events,
        "extent": {
            "geoExtent": parisExtent,
            "temporalExtent": create_temporalExtent(entry_start, entry_end),
        },
        "keywords": [keyword_paris, keywords_atlas, keyword_instantiation],
        "distributionInfo": distributionInfo.copy(),
        "stakeholders": stakeholders,
        "resourceLineage": [identifier],
        "associatedResource": [{
          "value": f"{entry_largerWorkCitation}",
          "typeOfAssociation": "largerWorkCitation"
        }]
      }
      ex_online_resources = [{
        "linkage": f"https://bibliotheques-specialisees.paris.fr/{entry_ark}",
        "protocol": "WWW:LINK",
        "name": "Lien vers la notice en ligne (sur https://bibliotheques-specialisees.paris.fr)",
        "description": f"Notice et visualisation de la version numérisée.",
        "onlineFunctionCode": "browsing",
      }]
      if entry_wms:
        ex_online_resources.append({
          'linkage': "https://map.geohistoricaldata.org/mapproxy/service=WMS?REQUEST=GetCapabilities",
          'protocol': "OGC:WMS",
          'name': f"{entry_wms}",
          'description': f"({entry_bhdv_exemplar_identifier}) {entry_title}",
          'onlineFunctionCode': "browsing"
        })
      entry_bhdv_exemplar["distributionInfo"]["onlineResources"] = ex_online_resources
      atlas_municipal_entries.append(entry_bhdv_exemplar)
      # iterate over sheets
      if entry_wms:
        for sheet_number in range(1,17):
          sheet_identifier = f"{entry_bhdv_exemplar_identifier}_{sheet_number:02d}"
          sheet_entry = {
            "identifier": sheet_identifier,
            "identification": {"title": f"({sheet_identifier}) {entry_title}. Feuille {sheet_number:02d}"},
            "abstract": f"{entry_abstract}",
            "events": events,
            "extent": {
                "geoExtent": extents[str(sheet_number)],
                "temporalExtent": create_temporalExtent(entry_start, entry_end),
            },
            "keywords": [keyword_paris, keywords_atlas, keyword_instantiation],
            "distributionInfo": distributionInfo.copy(),
            "stakeholders": stakeholders,
            "associatedResource": [{
              "value": f"{entry_bhdv_exemplar_identifier}",
              "typeOfAssociation": "largerWorkCitation"
            }]
          }
          ex_sheet_online_resources = [{
            'linkage': "https://map.geohistoricaldata.org/mapproxy/service=WMS?REQUEST=GetCapabilities",
            'protocol': "OGC:WMS",
            'name': f"{entry_wms}_{sheet_number:02d}",
            'description': f"({entry_bhdv_exemplar_identifier}) {entry_title}. Feuille {sheet_number:02d}",
            'onlineFunctionCode': "browsing"
          }]
          sheet_entry["distributionInfo"]["onlineResources"] = ex_sheet_online_resources
          atlas_municipal_entries.append(sheet_entry)
  with open("atlas_municipal_records.yaml", "w") as output_file:
    for res in atlas_municipal_entries:
        yaml.dump(res, output_file, explicit_start=True, explicit_end=True, sort_keys=False)

if __name__ == "__main__":
  main()
