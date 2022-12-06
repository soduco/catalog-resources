#!/bin/bash

SAXON="/usr/share/java/Saxon-HE-9.9.1.5.jar"
XSL="./oaipmh_yaml.xsl"
OUT="./RUMSEY.yaml"
echo "%YAML 1.1" > $OUT
while read F
do
    echo "transforming record for id" $F;
    URL="${BASE_URL}${F}"
    XML="./records/record_${F}.xml"
    echo "    " $URL;
    java -jar $SAXON -s:$XML -xsl:$XSL >> $OUT
done < verniquet_rumsey_ids