#!/usr/bin/env python3

import logging
import yaml
from datetime import datetime
import csv
import os
import sys
import json
from pyproj import CRS, Transformer
import uuid
def main():
  logging.basicConfig(level="DEBUG")
  events = [
    {"value": datetime.now().strftime("%Y-%m-%d"), "event": "publication"}
  ]
  keyword_file = {"value": "file", "typeOfKeyword": "taxon"}
  keyword_recordset = {"value": "RecordSet", "typeOfKeyword": "taxon"}
  keyword_record = {"value": "Record", "typeOfKeyword": "taxon"}
  keyword_instantiation = {"value": "Instantiation", "typeOfKeyword": "taxon"}
  keyword_paris = {"value": "Paris", "typeOfKeyword": "place"}
  keywords_atlas = {"value": "Verniquet", "typeOfKeyword": "theme"}
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
  spatialResolution = '1728'
  def create_temporalExtent(start:int, end: int):
    return {"beginPosition": f"{start}-01-01", "endPosition": f"{end}-12-31"}
  verniquet_proj4 = "+proj=aeqd +lat_0=48.83635863 +lon_0=2.33652533 +x_0=0 +y_0=0 +ellps=GRS80 +to_meter=1.94903631 +no_defs"
  crs = CRS.from_proj4(verniquet_proj4)
  crs_4326 = CRS.from_epsg(4326)
  transformer = Transformer.from_crs(crs, crs_4326)

  def create_geoExtent(min_x:float, min_y: float, max_x:float, max_y: float):
    (lat_sw,lon_sw) = transformer.transform(min_x, min_y)
    (lat_ne,lon_ne) = transformer.transform(max_x, max_y)
    return {
      "westBoundLongitude": str(lon_sw),
      "eastBoundLongitude": str(lon_ne),
      "southBoundLatitude": str(lat_sw),
      "northBoundLatitude": str(lat_ne),
    }
  entries=[]
  csv_path = "verniquet.csv"
  if not os.path.exists(csv_path):
    sys.exit("No csv at this path")
  filename = open(csv_path, "r", encoding="utf8")
  file = csv.DictReader(filename)
  for row in file:
    identifier = row["identifier"]
    entry_type = row["type"]
    entry_source = row["source"]
    entry_start = row["date_start"]
    entry_end = row["date_end"]
    if not entry_end:
      entry_end = entry_start
    print(f"Dates = {entry_start} - {entry_end}")
    entry_title = row["title"]
    entry_abstract = row["abstract"]
    entry_min_x=float(row["min_x"])
    entry_min_y=float(row["min_y"])
    entry_max_x=float(row["max_x"])
    entry_max_y=float(row["max_y"])
    entry_notice=row["notice"]
    entry_resource_num=row["resource_numerisee"]
    entry_oai=row["oai-pmh"]
    entry_points=row["points"]
    entry_geotiff=row["geotiff"]
    entry_annotation = row["annotation_file"]
    entry_iiif = row["iiif_manifest"]
    entry_overview=row["overview"]
    entry_native=row["native"]
    entry_wms = row["wms_id"]
    entry_largerWorkCitation = row["largerWorkCitation"]
    entry_resourceLineage = row["resourceLineage"]
    extent = {
      "geoExtent": create_geoExtent(entry_min_x,entry_min_y,entry_max_x,entry_max_y),
      "temporalExtent": create_temporalExtent(entry_start, entry_end),
    }
    keywords = [keyword_paris, keywords_atlas]
    if entry_type == "file":
      keywords.append(keyword_file)
    elif entry_type == "recordset":
      keywords.append(keyword_recordset)
    elif entry_type == "record":
      keywords.append(keyword_record)
    else:
      keywords.append(keyword_instantiation)
    if entry_source:
      keywords.append({"value": entry_source, "typeOfKeyword": "service"})
    # create the Verniquet file
      # create Plan général de la Ville de Paris
      # create Verniquet sheets
      # create BnF Verniquet sheets
      # create Stanford Verniquet sheets

    entry = {
      "identifier": identifier,
      "identification": {"title": f"({identifier}) {entry_title}"},
      "abstract": f"{entry_abstract}",
      "events": events,
      "extent": extent,
      "keywords": keywords,
      "distributionInfo": distributionInfo.copy(),
      "stakeholders": stakeholders,
      "spatialResolution": spatialResolution
    }
    if entry_largerWorkCitation:
      entry["associatedResource"] = [{
          "value": f"{entry_largerWorkCitation}",
          "typeOfAssociation": "largerWorkCitation"
        }]
    if entry_resourceLineage:
      entry["resourceLineage"] = [entry_resourceLineage]
    online_resources = []
    if entry_notice:
      online_resources.append(
        {
          "linkage": entry_notice,
          "protocol": "WWW:LINK",
          "name": "Lien vers la notice en ligne",
          "description": f"Notice de la version numérisée.",
          "onlineFunctionCode": "information",
        })
    if entry_resource_num:
      online_resources.append(
        {
          "linkage": entry_resource_num,
          "protocol": "WWW:LINK",
          "name": "Lien vers la version numérisée en ligne",
          "description": f"Visualisation de la version numérisée.",
          "onlineFunctionCode": "browsing",
        })
    if entry_oai:
      online_resources.append(
        {
          "linkage": entry_oai,
          "protocol": "WWW:DOWNLOAD",
          "name": "Lien vers les métadonnées de la source",
          "description": f"Métadonnées OAI-PMH.",
          "onlineFunctionCode": "information",
        })
    if entry_points:
      online_resources.append(
        {
          "linkage": entry_points,
          "protocol": "WWW:DOWNLOAD",
          "name": "Points de géoréférencement",
          "description": f"Lien vers les points de géoréférencement au format QGIS (.points).",
          "onlineFunctionCode": "download",
        })
    if entry_geotiff:
      online_resources.append(
        {
          "linkage": entry_geotiff,
          "protocol": "WWW:DOWNLOAD",
          "name": "Image géoréférencée",
          "description": f"Lien vers l'image géoréférencée au format GeoTIFF (sans masquage).",
          "onlineFunctionCode": "download",
        })
    if entry_annotation:
      online_resources.append(
        {
          "linkage": entry_annotation,
          "protocol": "WWW:DOWNLOAD",
          "name": "Annotation de géoréférencement IIIF",
          "description": f"Lien vers l'annotation de géoréférencement IIIF (Allmaps).",
          "onlineFunctionCode": "information",
        })
      online_resources.append(
        {
          "linkage": "https://allmaps.xyz/{z}/{x}/{y}.png?url="+entry_annotation,
          "protocol": "WWW:LINK",
          "name": "Allmaps tiled map",
          "description": f"Lien vers le service XYZ (Allmaps) pour la visualisation de la resource géoréférencée depuis un SIG.",
          "onlineFunctionCode": "browseGraphic",
        })
      online_resources.append(
        {
          "linkage": f"https://viewer.allmaps.org/?url={entry_annotation}",
          "protocol": "WWW:LINK",
          "name": "Visualisation depuis le viewer Allmaps",
          "description": f"Lien vers la visualisation de l'annotation de géoréférencement IIIF dans le viewer Allmaps.",
          "onlineFunctionCode": "browseGraphic",
        })
    if entry_iiif:
      online_resources.append(
        {
          "linkage": entry_iiif,
          "protocol": "WWW:LINK",
          "name": "Image IIIF",
          "description": f"Lien vers l'image à travers l'API IIIF.",
          "onlineFunctionCode": "browseGraphic",
        })
    if entry_overview:
      entry["overview"] = entry_overview
    if entry_native:
      online_resources.append(
        {
          "linkage": entry_native,
          "protocol": "WWW:DOWNLOAD",
          "name": "Image au format natif",
          "description": f"Lien vers l'image numérisée.",
          "onlineFunctionCode": "download",
        })
    if entry_wms:
      online_resources.append({
        'linkage': "https://map.geohistoricaldata.org/mapproxy/service=WMS?REQUEST=GetCapabilities",
        'protocol': "OGC:WMS",
        'name': f"{entry_wms}",
        'description': f"({identifier}) {entry_title}",
        'onlineFunctionCode': "browseGraphic"
      })
    if len(online_resources)>0:
      entry["distributionInfo"]["onlineResources"] = online_resources
    # process steps
    process_steps = []
    if entry_geotiff:
      process_step = {
        "title": f"Géoréférencement",
        "description": "Utilisation des points de contrôle pour géoréférencer l'image.",
        "processingIdentifier": str(uuid.uuid5(uuid.NAMESPACE_X500, entry_native+entry_points)),
        "processorInfo": processorInfo.copy(),
        "typeOfActivity": "Georeferencement",
        "processStepSource": [
          {
            "title": "Document source (image)",
            "description": f"Document récupéré depuis {entry_native}",
            "identifier": str(uuid.uuid5(uuid.NAMESPACE_X500, entry_native)),
            "url": entry_native
          },
          {
            "title": "Document source (points de contrôle)",
            "description": f"Document récupéré depuis {entry_points}",
            "identifier": str(uuid.uuid5(uuid.NAMESPACE_X500, entry_points)),
            "url": entry_points
          }
        ],
        "softwareTitle": "GDAL",
        "softwareIdentifier": "cc69657a-6cf3-42f9-9109-6b196d7917d1",
        "ProcessStepOutput": [
          {
            "title": f"Image géoréférencée",
            "description": f"Image géoréférencée au format GeoTIFF pour {entry_native} avec les points de contrôle {entry_points}.",
            "identifier": str(uuid.uuid5(uuid.NAMESPACE_X500, entry_geotiff)),
            "url": entry_geotiff
          }
        ]
      }
      process_steps.append(process_step)
    if len(process_steps) > 0:
      entry["processStep"] = process_steps
    entries.append(entry)
  with open("verniquet_records.yaml", "w") as output_file:
    for res in entries:
        yaml.dump(res, output_file, explicit_start=True, explicit_end=True, sort_keys=False)

if __name__ == "__main__":
  main()
