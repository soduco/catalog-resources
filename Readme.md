# Create the resources for the SoDUCo catalog

## Sources
The published resources are described in the following **csv** files:
- verniquet_file/verniquet.csv
- jacoubet/jacoubet.csv
- atlas_minicipal/atlas_municipal_list.csv
- directories/directories_index_20231204.csv (index of the directories)
- directories/directories_adress_lists_index_20231204.csv (list of addresses in the directories)

## Verniquet

1. Create the records as a **yaml** file from the **csv** file
```bash
cd verniquet_file
python create_verniquet_records.py 
```
2. (optional) If you have prior corresponding records, don't forget to clean them up from the catalog. For instance with:
```bash
soduco_geonetwork_cli delete yaml_list.csv
```
3. Create the **xml** files from the created **yaml** file
```bash
soduco_geonetwork_cli parse verniquet_records.yaml 
```
4. Upload the **xml** files to the geocatalog
```bash
soduco_geonetwork_cli upload yaml_list.csv
soduco_geonetwork_cli update-postponed-values yaml_list.csv temp.csv
```
5. Enjoy

## Jacoubet

```bash
cd jacoubet
python create_records.py 
```
2. (optional) If you have prior corresponding records, don't forget to clean them up from the catalog. For instance with:
```bash
soduco_geonetwork_cli delete yaml_list.csv
```
3. Create the **xml** files from the created **yaml** file
```bash
soduco_geonetwork_cli parse atlas_jacoubet_records.yaml 
```
4. Upload the **xml** files to the geocatalog
```bash
soduco_geonetwork_cli upload yaml_list.csv
soduco_geonetwork_cli update-postponed-values yaml_list.csv temp.csv
```
5. Enjoy


## Atlas Municipal

```bash
cd atlas_municipal
python create_records.py 
```
2. (optional) If you have prior corresponding records, don't forget to clean them up from the catalog. For instance with:
```bash
soduco_geonetwork_cli delete yaml_list.csv
```
3. Create the **xml** files from the created **yaml** file
```bash
soduco_geonetwork_cli parse atlas_municipal_records.yaml 
```
4. Upload the **xml** files to the geocatalog
```bash
soduco_geonetwork_cli upload yaml_list.csv
soduco_geonetwork_cli update-postponed-values yaml_list.csv temp.csv
```
5. Enjoy

## Directories

```bash
cd directories
python create_directory_records.py
```
2. (optional) If you have prior corresponding records, don't forget to clean them up from the catalog. For instance with:
```bash
soduco_geonetwork_cli delete yaml_list.csv
```
3. Create the **xml** files from the created **yaml** file
```bash
soduco_geonetwork_cli parse directories.yaml 
```
4. Upload the **xml** files to the geocatalog
```bash
soduco_geonetwork_cli upload yaml_list.csv
soduco_geonetwork_cli update-postponed-values yaml_list.csv temp.csv
```
5. Enjoy
