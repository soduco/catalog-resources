from osgeo import ogr
from pyproj import CRS, Transformer
import json
fileName = "/home/JPerret/data/quartiers_paris_post_1860.shp"
driverName = "ESRI Shapefile"      # e.g.: GeoJSON, ESRI Shapefile
driver = ogr.GetDriverByName(driverName)
dataSource = driver.Open(fileName, 0) # 0 means read-only. 1 means writeable.
layer = dataSource.GetLayer()

feuilles = {}
for feature in layer:
  arrondissement = feature.GetField("arrond")
  if arrondissement == 1 or arrondissement == 2:
    feuille = "1"
  elif arrondissement == 3 or arrondissement == 4:
    feuille = "2"
  elif arrondissement == 5 or arrondissement == 6:
    feuille = "3"
  elif arrondissement == 7:
    feuille = "4"
  elif arrondissement == 8:
    feuille = "5"
  elif arrondissement == 9 or arrondissement == 10:
    feuille = "6"
  elif arrondissement == 11:
    feuille = "7"
  elif arrondissement == 12:
    feuille = "8"
  elif arrondissement == 13:
    feuille = "9"
  elif arrondissement == 14:
    feuille = "10"
  elif arrondissement == 15:
    feuille = "11"
  elif arrondissement == 16:
    feuille = "12"
  elif arrondissement == 17:
    feuille = "13"
  elif arrondissement == 18:
    feuille = "14"
  elif arrondissement == 19:
    feuille = "15"
  elif arrondissement == 20:
    feuille = "16"
  geom = feature.GetGeometryRef()
  env = geom.GetEnvelope()
  if feuille in feuilles:
    feuilles[feuille]["minX"]=min(feuilles[feuille]["minX"],env[0])
    feuilles[feuille]["maxX"]=max(feuilles[feuille]["maxX"],env[1])
    feuilles[feuille]["minY"]=min(feuilles[feuille]["minY"],env[2])
    feuilles[feuille]["maxY"]=max(feuilles[feuille]["maxY"],env[3])
  else:
    feuilles[feuille] = {
      "minX":env[0],
      "maxX":env[1],
      "minY":env[2],
      "maxY":env[3],
    }
crs_2154 = CRS.from_epsg(2154)
crs_4326 = CRS.from_epsg(4326)
transformer = Transformer.from_crs(crs_2154, crs_4326)
output = {}
for feuille,env in feuilles.items():
  min = transformer.transform(env["minX"], env["minY"])
  max = transformer.transform(env["maxX"], env["maxY"])
  output[feuille] = {
    'westBoundLongitude': str(min[1]),
    'eastBoundLongitude': str(max[1]),
    'southBoundLatitude': str(min[0]),
    'northBoundLatitude': str(max[0])
  }
with open("atlas_municipal_entents.json", "w") as output_file:
  json.dump(output, output_file, indent = 1) 