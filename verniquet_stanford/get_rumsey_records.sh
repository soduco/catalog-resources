#!/bin/bash
BASE_URL="https://www.davidrumsey.com/luna/servlet/oai?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:N/A:"
mkdir records
while read F
do
    echo "getting record for id" $F;
    URL="${BASE_URL}${F}"
    FILE="./records/record_${F}.xml"
    echo "    " $URL;
    wget "$URL" -O $FILE
done < verniquet_rumsey_ids