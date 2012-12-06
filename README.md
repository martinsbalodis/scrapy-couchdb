Description
===========
Pipeline which allow you to store scrapy items in CouchDB database.
Downloader middleware wich will cache downloaded web pages in couchdb.

Install
=======
   pip install "ScrapyCouchDB"

Configure your settings.py:
----------------------------
    ITEM_PIPELINES = [
      'scrapycouchdb.CouchDBPipeline',
    ]


    COUCHDB_SERVER = 'http://192.168.84.84:5984/'
    COUCHDB_DB = 'offers'
    COUCHDB_UNIQ_KEY = 'uuid'
    COUCHDB_IGNORE_FIELDS = ['visit_id', 'visit_status']


    DOWNLOADER_MIDDLEWARES = {
        'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware':543,
    }
    HTTPCACHE_ENABLED=True
    HTTPCACHE_STORAGE='scrapycouchdb.CouchDBCacheStorage'


Changelog
=========
0.1
* Initial version

0.2
* Do not create a new revision if document already exist with same data

Licence
=======
Copyright 2011 Julien Duponchelle, Martins Balodis

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
