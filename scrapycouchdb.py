import couchdb
from scrapy.conf import settings
from scrapy import log
import datetime
from w3lib.http import headers_dict_to_raw, headers_raw_to_dict
from scrapy.http import Headers
from scrapy.responsetypes import responsetypes
from urlparse import urlparse

class CouchDBPipeline(object):
    def __init__(self):
        couch = couchdb.Server(settings['COUCHDB_SERVER'])
        self.db = couch[settings['COUCHDB_DB']]

    def process_item(self, item, spider):
        data = {}
        for key in item.keys():
            if key in settings['COUCHDB_IGNORE_FIELDS']:
                continue
            elif isinstance(item[key], datetime.datetime):
                data[key] = item[key].isoformat()
            else:
                data[key] = item[key]
            #Throw exception if unknow type
        data['_id'] = data[settings['COUCHDB_UNIQ_KEY']]
        try:
            old = self.db[data['_id']]
            data['_rev'] = old['_rev']
        except couchdb.http.ResourceNotFound:
            change = True

        #Only save the document if new content
        if data.has_key('_rev'):
            change = False
            for key in data.keys():
                if not old.has_key(key):
                    change = True
                else:
                    if old[key] != data[key]:
                        change = True
        if change:
            self.db.save(data)
            log.msg("Item wrote to CouchDB database %s/%s" %
                    (settings['COUCHDB_SERVER'], settings['COUCHDB_DB']),
                    level=log.DEBUG, spider=spider)  
        return item


class CouchDBCacheStorage(object):

    def __init__(self, settings):
        couch = couchdb.Server(settings['COUCHDB_SERVER'])
        try:
            self.db = couch[settings['COUCHDB_DB']]
        except couchdb.http.ResourceNotFound:
            couch.create(settings['COUCHDB_DB'])
            self.db = couch[settings['COUCHDB_DB']]

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def retrieve_response(self, spider, request):
        """Return response if present in cache, or None otherwise."""
        try:
            document = self.db[self._inverse_url(request.url)]
        except couchdb.http.ResourceNotFound:
            return
            # @TODO expiration
        body = document['response_body']
        url = document['response_url']
        status = document['status']
        headers = Headers(headers_raw_to_dict(document['response_headers']))
        encoding = document['encoding']
        respcls = responsetypes.from_args(headers=headers, url=url)
        response = respcls(url=url, headers=headers, status=status, body=body,
                encoding=encoding)
        return response

    def store_response(self, spider, request, response):
        """Store the given response in the cache."""
        data = {
            '_id': self._inverse_url(request.url),
            'url': request.url,
            'method': request.method,
            'status': response.status,
            'response_url': response.url,
            'timestamp': datetime.datetime.now().strftime("%s"),
            'response_body': response.body_as_unicode(),
            'response_headers': headers_dict_to_raw(response.headers),
            'request_headers': headers_dict_to_raw(request.headers),
            'request_body': request.body,
            'encoding': response.encoding
        }
        self.db.save(data)

    def _inverse_url(self, url):
        elements = urlparse(url)
        return ".".join(elements.netloc.split('.')[::-1])+':'+elements.scheme\
               +elements.path+elements.query