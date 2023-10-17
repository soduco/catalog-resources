# create the theoretical verniquet records
cd verniquet
python create_records.py
# creates the verniquet/verniquet_records.yaml
soduco_geonetwork_cli parse verniquet_records.yaml
# creates the verniquet/yaml_list.csv
soduco_geonetwork_cli upload yaml_list.csv
# updates the verniquet/yaml_list.csv with uuids

cd ../verniquet_bnf
python create_bnf_records.py
# creates the verniquet_bnf/verniquet_bnf_records.yaml
soduco_geonetwork_cli parse verniquet_bnf_records.yaml
# creates the verniquet_bnf/yaml_list.csv
soduco_geonetwork_cli upload yaml_list.csv
# updates the verniquet_bnf/yaml_list.csv with uuids

cd ../verniquet_stanford
python create_stanford_records.py
# creates the verniquet_stanford/verniquet_stanford_records.yaml
soduco_geonetwork_cli parse verniquet_stanford_records.yaml
# creates the verniquet_stanford/yaml_list.csv
soduco_geonetwork_cli upload yaml_list.csv
# updates the verniquet_stanford/yaml_list.csv with uuids
