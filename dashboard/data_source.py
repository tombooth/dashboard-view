import config
import urllib


class DataSource(object):

    def __init__(self, json):
        self._json = json
        self._got = None

    def _query_string(self):
        query_string = ''

        if 'query-params' in self._json:
            query_tuples = []
            for k, v in self._json['query-params'].iteritems():
                if isinstance(v, list):
                    for sv in v:
                        query_tuples.append((k, sv))
                else:
                    query_tuples.append((k, v))
            query_string = '?flatten=true&' + urllib.urlencode(query_tuples) 

        return query_string

    def url(self):
        return '{0}/{1}/{2}{3}'.format(
            config.DATA_URL, self._json['data-group'],
            self._json['data-type'], self._query_string())

    def parse_response(self, response):
        if response.status_code == 200:
            self._got = response.json()['data']
            return self._got
        elif response.status_code == 404:
            return None
        else:
            #should raise error
            print response.status_code, response.text
            return None

    def get(self):
        return self._got
