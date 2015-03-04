Image Solr
===========


## Dev Guide

```
wget http://bit.ly/miniconda
bash Miniconda-latest-Linux-x86_64.sh
bash install.sh
conda env create -n image_solr -f environment.yaml
source activate image_solr
python server.py
```


### DATABASE INTERACTIONS

- Models (models.py) defines db schema
- API (db_api.py) uses models.py
- VIEWS -- use API
