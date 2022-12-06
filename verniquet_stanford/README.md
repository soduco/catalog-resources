# Extracting Information from the Rumsey collection

Ids could be extracted using the following API:
https://www.davidrumsey.com/luna/servlet/as/fetchMediaSearch?&sort=Pub_List_No_InitialSort%2CPub_Date%2CPub_List_No%2CSeries_No&lc=RUMSEY~8~1&fullData=true&q=Pub_List_No=10110.000&bs=80

- For now, the Ids were saved in a *verniquet_rumsey_ids* ... should dissapear?
- The **get_rumsey_records.sh** script downloads the records using OAI.
- The **transform_rumsey_records.sh** script uses xslt to create the YAML file
    - This require *Saxon-HE* to be installed
