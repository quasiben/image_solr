Image Solr
===========


## Dev Guide

```
wget http://bit.ly/miniconda
bash Miniconda-latest-Linux-x86_64.sh
bash install.sh
conda env -n image_solr -f environment.yaml
python server.py
```


### DATABASE INTERACTIONS

- Models (models.py) defines db schema
- API (db_api.py) uses models.py
- VIEWS -- use API
