import config
import requests
import urllib


class DataSource(object):

    def __init__(self, json):
        self._json = json

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

    def get(self):
        response = requests.get(self.url(), verify=False)

        if response.status_code == 200:
            return response.json()['data']
        elif response.status_code == 404:
            return None
        else:
            #should raise error
            print response.status_code, response.text
            return None
