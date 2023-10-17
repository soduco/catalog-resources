import logging

def add_files(dataverse, dataverse_datafileurl:str, prefix: str, list: list):
    for e in dataverse["data"]["latestVersion"]["files"]:
        label = e["label"]
        fileId = e["dataFile"]["id"]
        link = dataverse_datafileurl + str(fileId)
        files = []

        def resource(link: str, name: str, description: str, protocol: str):
            return {
                "linkage": link,
                "protocol": protocol,
                "name": name,
                "description": description,
                "onlineFunctionCode": "download",
            }
        if label == prefix + ".jpg.points":
            logging.debug(f"points found: {fileId}")
            files = [resource(link, "Georeferencing point file", "Georeferencing point file exported from QGIS", "WWW:DOWNLOAD")]
        if label == prefix + ".json":
            logging.debug(f"json found: {fileId}")
            files = [
                resource(link, "Allmaps georeferencing IIIF annotation file", "Georeferencing annotation file in IIIF annotation format", "WWW:DOWNLOAD"),
                resource(
                    "https://allmaps.xyz/{z}/{x}/{y}.png?url=" + link,
                    "Allmaps tiled map",
                    "Open IIIF annotation file in Allmaps tiled map",
                    "WWW:LINK"
                ),
                resource(
                    "https://viewer.allmaps.org/?url=" + link,
                    "Allmaps viewer",
                    "Open IIIF annotation file in Allmaps viewer",
                    "WWW:LINK"
                ),
            ]
        if label == prefix + ".tif":
            logging.debug(f"tif found: {fileId}")
            files = [resource(link, "Georeferenced tiff", "Georeferenced image as GeoTIFF","WWW:DOWNLOAD")]

        if files:
            list.extend(files)