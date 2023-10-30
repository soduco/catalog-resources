#!/usr/bin/env python3

import logging
import uuid
import yaml
from datetime import datetime
import pandas
import math

def main():
  logging.basicConfig(filename='temp.log', encoding='utf-8', format='%(asctime)s-%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

  parisExtent = {
      "westBoundLongitude": "2.2789487344052968",
      "eastBoundLongitude": "2.4080435114903960",
      "southBoundLatitude": "48.8244731921314568",
      "northBoundLatitude": "48.8904078536729116",
  }
  keyword_file = {"value": "file", "typeOfKeyword": "taxon"}
  keyword_recordset = {"value": "RecordSet", "typeOfKeyword": "taxon"}
  keyword_record = {"value": "Record", "typeOfKeyword": "taxon"}
  keyword_instantiation = {"value": "Instantiation", "typeOfKeyword": "taxon"}
  keyword_paris = {"value": "Paris", "typeOfKeyword": "place"}
  keywords_directory = {"value": "Directory", "typeOfKeyword": "theme"}
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
  def time_instants_df(lines):
    annee_deb=int(lines["annee_deb"].min())
    annee_fin=int(lines["annee_deb"].max())
    maxdatefin=lines["annee_fin"].max()
    if pandas.notna(maxdatefin):
      annee_fin = max(annee_fin,int(maxdatefin))
    return annee_deb,annee_fin

  events = [
    {"value": datetime.now().strftime("%Y-%m-%d"), "event": "publication"}
  ]
  df = pandas.read_excel(r"/home/JPerret/devel/directories_annotation/directories_index_20231024.xlsx")
  annee_deb,annee_fin = time_instants_df(df)
  temporalExtent = {"beginPosition": f"{annee_deb}-01-01", "endPosition": f"{annee_fin}-12-31"}

  # create a record for the directory file
  directory_entries = [{
      "identifier": "directory_file",
      "identification": {"title": "Dossier Annuaires"},
      "abstract": "Research and resource file dedicated to the directories of the city of Paris.",
      "events": events,
      "extent": {
          "geoExtent": parisExtent,
          "temporalExtent": temporalExtent,
      },
      "keywords": [keyword_paris, keywords_directory, keyword_file],
      "distributionInfo": distributionInfo,
      "stakeholders": stakeholders,
    }]
  collections = sorted(df["collection"].unique())
  for collection in collections:
    logging.info(f"Collection {collection}")
    collection_lines = df[df['collection']==collection]
    series = collection_lines["serie"].unique()
    collection_first_line = collection_lines.iloc[0]
    coll_titre = collection_first_line['coll_titre']
    coll_nt = collection_first_line['coll_nt']
    annee_deb,annee_fin = time_instants_df(collection_lines)
    temporalExtent = {"beginPosition": f"{annee_deb}-01-01", "endPosition": f"{annee_fin}-12-31"}
    logging.info(f"\t{coll_titre} - {coll_nt} - [{annee_deb} - {annee_fin}]")
    # create a recordset for the collection
    directory_entries.append({
      "identifier": f"Collection:{collection}",
      "identification": {"title": f"({collection}) {coll_titre}"},
      "abstract": f"Collection d'annuaires comprenant {len(series)} séries et {len(collection_lines.index)} annuaires répertoriés dans le cadre du projet SoDUCo.",
      "events": events,
      "extent": {
          "geoExtent": parisExtent,
          "temporalExtent": temporalExtent,
      },
      "keywords": [keyword_paris, keywords_directory, keyword_recordset],
      "distributionInfo": distributionInfo,
      "stakeholders": stakeholders,
      "associatedResource": [{
        "value": "directory_file",
        "typeOfAssociation": "largerWorkCitation"
      }]
    })

  series = sorted(df["serie"].unique())
  for serie in series:
    logging.info(f"Serie {serie}")
    serie_lines = df[df['serie']==serie]
    serie_first_line = serie_lines.iloc[0]
    serie_titre = serie_first_line['Série_titre']
    serie_nt = serie_first_line['serie_nt']
    serie_redacteur = serie_first_line['redacteur']
    collection_id = serie_first_line['collection']
    annee_deb,annee_fin = time_instants_df(serie_lines)
    temporalExtent = {"beginPosition": f"{annee_deb}-01-01", "endPosition": f"{annee_fin}-12-31"}
    logging.info(f"\t{serie_titre} - {serie_nt} - [{annee_deb} - {annee_fin}] - in {collection_id} - {serie_redacteur}")
    # create a recordset for the serie
    directory_entries.append({
      "identifier": f"Serie:{serie}",
      "identification": {"title": f"({serie}) {serie_titre}"},
      "abstract": f"Série d'annuaires comprenant {len(collection_lines.index)} annuaires répertoriés dans le cadre du projet SoDUCo.",
      "events": events,
      "extent": {
          "geoExtent": parisExtent,
          "temporalExtent": temporalExtent,
      },
      "keywords": [keyword_paris, keywords_directory, keyword_recordset],
      "distributionInfo": distributionInfo,
      "stakeholders": stakeholders,
      "associatedResource": [{
        "value": f"Collection:{collection_id}",
        "typeOfAssociation": "largerWorkCitation"
      }]
    })

  logging.info(f"There are {len(series)} series")

  df_complement = pandas.read_excel(r"/home/JPerret/Documents/SODUCO/directories_adress_lists_index_20230915.xlsx")
  directories = sorted(df["code_ouvrage"].unique())
  def rename_na_exemplar(name: str):
    if pandas.isna(name):
      return "ex1"
    else:
      return name
  for directory in directories:
    directory_lines = df[df['code_ouvrage']==directory]
    directory_exemplars = sorted([rename_na_exemplar(item) for item in directory_lines["exemplaire"].unique()])
    directory_first_line = directory_lines.iloc[0]
    directory_lines_first_exemplar = directory_lines[pandas.isna(directory_lines['exemplaire'])]
    serie_id = directory_first_line["serie"]
    directory_title = directory_first_line["titre ouvrage"]
    if pandas.isna(directory_first_line["titre ouvrage"]):
      directory_title = directory.replace("_"," ")
    directory_title_complement = directory_first_line["titre_complement"]
    if pandas.isna(directory_title_complement):
      directory_title_complement = ""
    annee_deb=int(directory_first_line["annee_deb"].min())
    annee_fin=int(directory_first_line["annee_deb"].max())
    if pandas.isna(annee_fin):
      annee_fin=annee_deb
    temporalExtent = {"beginPosition": f"{annee_deb}-01-01", "endPosition": f"{annee_fin}-12-31"}
    logging.info(f"Directory {directory} [{annee_deb} - {annee_fin}] in {serie_id} - with {len(directory_lines.index)} parts/exemplars {directory_exemplars} with {len(directory_lines_first_exemplar.index)} parts for the first ex")
    # create a record for the directory
    directory_entries.append({
      "identifier": directory,
      "identification": {"title": f"({directory}) {directory_title}"},
      "abstract": f"{directory_title}. {directory_title_complement}",
      "events": events,
      "extent": {
          "geoExtent": parisExtent,
          "temporalExtent": temporalExtent,
      },
      "keywords": [keyword_paris, keywords_directory, keyword_record],
      "distributionInfo": distributionInfo,
      "stakeholders": stakeholders,
      "associatedResource": [{
        "value": f"Serie:{serie_id}",
        "typeOfAssociation": "largerWorkCitation"
      }]
    })
    # TODO iterate over exemplars and create a directory instantiation for each
    for exemplar in directory_exemplars:
      exemplar_id = f"{directory}_{exemplar}"
      logging.info(f"\tExemplar {exemplar_id}")
      if exemplar == "ex1":
        exemplar_lines = directory_lines[pandas.isna(directory_lines["exemplaire"])]
      else:
        exemplar_lines = directory_lines[directory_lines["exemplaire"]==exemplar]
      source=None
      for _, exemplar_line in exemplar_lines.iterrows():
        if pandas.notna(exemplar_line["Vnum_lien_Gallica"]):
          source="Exemplaire BnF"
        else:
          if pandas.notna(exemplar_line["Vnum_lien_retronews"]):
            source="Exemplaire RetroNews - BnF"
          else:
            if pandas.notna(exemplar_line["Vnum_autre_source_lien"]):
              source=f"Exemplaire {exemplar_line['Vnum_autre_source']}"
      if not source:
        source = "Aucun exemplaire numérique trouvé dans le cadre du projet."
      #TODO where do we add the "source"?
      exemplar_distributionInfo = distributionInfo.copy()
      directory_entry = {
        "identifier": exemplar_id,
        "identification": {"title": f"({exemplar_id}) {directory_title}. {source}."},
        "abstract": f"{directory_title}. {directory_title_complement}",
        "events": events,
        "extent": {
            "geoExtent": parisExtent,
            "temporalExtent": temporalExtent,
        },
        "keywords": [keyword_paris, keywords_directory, keyword_instantiation],
        "distributionInfo": exemplar_distributionInfo,
        "stakeholders": stakeholders,
        "resourceLineage": [directory]
      }
      #online links and overview
      online_resources=[]
      for _, exemplar_line in exemplar_lines.iterrows():
        link=None
        source=None
        overview=None
        if pandas.notna(exemplar_line["Vnum_lien_Gallica"]):
          source="BnF"
          link=exemplar_line["Vnum_lien_Gallica"]
          overview=link.rstrip('/')+".lowres"
        else:
          if pandas.notna(exemplar_line["Vnum_lien_retronews"]):
            source="RetroNews - BnF"
            link=exemplar_line["Vnum_lien_retronews"]
          else:
            if pandas.notna(exemplar_line["Vnum_autre_source_lien"]):
              source=exemplar_line["Vnum_autre_source"]
              link=exemplar_line["Vnum_autre_source_lien"]
              if pandas.notna(link) and link.__contains__("google"):
                overview=link+"&printsec=frontcover&img=1"
        if overview:
          directory_entry["overview"]=overview
        if link:
          complements = []
          if pandas.notna(exemplar_line["titre_complement"]):
            complements.append(exemplar_line["titre_complement"])
          if pandas.notna(exemplar_line["contenant"]):
            complements.append(exemplar_line["contenant"])
          online_resources.append(
            {
              "linkage": link,
              "protocol": "WWW:LINK",
              "name": "Lien vers le document en ligne",
              "description": f"Scan de l'annuaire. {'.'.join(complements)}. {source}.",
              "onlineFunctionCode": "browsing",
            }
          )
      if len(online_resources) > 0:
        exemplar_distributionInfo["onlineResources"] = online_resources
      #use the complementary file to get additional content (lists, pages, etc.)
      if exemplar == "ex1":
        exemplar_complement_lines = df_complement[df_complement["code_ouvrage"]==directory]
      else:
        exemplar_complement_lines = df_complement[df_complement["code_ouvrage"]==directory+"_"+exemplar]
      logging.info(f"\tThere are {len(exemplar_complement_lines.index)} lines for exemplar {exemplar}")
      process_steps = []
      lists = sorted(exemplar_complement_lines['liste_type'].unique())
      for list in lists:
        list_lines = exemplar_complement_lines[exemplar_complement_lines['liste_type']==list]
        for list_index, (_,row_complement) in enumerate(list_lines.iterrows()):
          list_name = f"{list}-p{list_index+1}"
          code_fichier = row_complement['Code_fichier']
          code_collection = row_complement['collection_almanach']
          code_serie = row_complement['serie_almanach']
          #code_ouvrage = row_complement['code_ouvrage']
          #annee = row_complement['Liste_annee']
          url = row_complement['lien_ouvrage_en_ligne']
          selection = row_complement['selection_trait_soduco']
          if selection and selection > 0:
            diff_vuepdf_vueark = row_complement['diff_vuepdf_vueark']
            if pandas.isna(row_complement['diff_vuepdf_vueark']):
              diff_vuepdf_vueark = 0
            else:
              diff_vuepdf_vueark = int(diff_vuepdf_vueark)
            page_start = int(row_complement['npage_pdf_d'])#-diff_vuepdf_vueark
            page_end = int(row_complement['npage_pdf_f'])#-diff_vuepdf_vueark
            url_output = f"https://api.geohistoricaldata.org/directories/entries?and=(source.eq.{code_fichier},and(page.gte.{page_start:04d},page.lte.{page_end:04d}))&order=page.asc,id.asc"
            process_step = {
              "title": f"({list_name}) Application de la chaîne de traitement SoDUCo",
              "description": "Application de la chaîne de traitement SoDUCo impliquant, entre autres, l'extraction de la structure du document, l'extraction des entrées, la reconnaissance de caractères et la détection des entités nommées.",
              "identifier": str(uuid.uuid4()),
              "processorInfo": processorInfo.copy(),
              "typeOfActivity": "directory_analysis",
              "processStepSource": [
                {
                  "title": "Document source (image)",
                  "description": f"Document récupéré depuis {url}",
                  "identifier": str(uuid.uuid5(uuid.NAMESPACE_URL, url))
                }
              ],
              "softwareTitle": "Chaîne de traitement SoDUCo",
              "softwareIdentifier": str(uuid.uuid5(uuid.NAMESPACE_URL, "https://gitlab.lre.epita.fr/soduco/directory-annotator-back")),
              "ProcessStepOutput": [
                {
                  "title": "Données créées par la chaîne detraitement",
                  "description": f"Données créées par la chaîne detraitement et récupérable en ligne sur {url_output}",
                  "identifier": str(uuid.uuid5(uuid.NAMESPACE_URL, url_output))
                }
              ]
            }
            online_resources.append(
              {
                "linkage": url_output,
                "protocol": "WWW:DOWNLOAD",
                "name": f"({list_name}) Lien vers le résultat de la chaîne de traitement SoDUCo",
                "description": f"Entrées de la liste {list} correspondant aux pages ({page_start} - {page_end}) extraites de l'annuaire {directory}. {'.'.join(complements)}. {source}",
                "onlineFunctionCode": "download",
              }
            )
            url_mirador = f"https://directory.geohistoricaldata.org/?manifest=https://directory.geohistoricaldata.org/iiif/{code_collection}/{code_serie}/{directory}/{list}/part_{list_index}/manifest.json"
            online_resources.append(
              {
                "linkage": url_mirador,
                "protocol": "WWW:LINK",
                "name": f"({list_name}) Visualisation du résultat de la chaîne de traitement SoDUCo (IIIF)",
                "description": f"Entrées de la liste {list} correspondant aux pages ({page_start} - {page_end}) extraites de l'annuaire {directory}. {'.'.join(complements)}. {source}",
                "onlineFunctionCode": "browsing",
              }
            )
            process_steps.append(process_step)
          #ark_index = url.find("ark")
      if len(process_steps) > 0:
        directory_entry["processStep"] = process_steps
      directory_entries.append(directory_entry)
  logging.info(f"There are {len(directories)} directories")
  with open("directories.yaml", "w") as output_file:
    for res in directory_entries:
      yaml.dump(res, output_file, explicit_start=True, explicit_end=True, sort_keys=False)

if __name__ == "__main__":
  main()
