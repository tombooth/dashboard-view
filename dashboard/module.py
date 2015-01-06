import config
import grequests
import itertools
import json
import requests

from collections import OrderedDict
from flask import render_template

from data_source import DataSource
from formatting import format
from table import data_to_table


def pluck(fields, datum):
    row = []
    for field in fields:
        if isinstance(field, list):
            cell = []
            for element in field:
                cell.append(datum[element])
            row.append(cell)
        else:
            row.append(datum[field])
    return row


def merge_axes(base, extra):
    if extra is None:
        return base
    else:
        return dict(base.items() + extra.items())


class Module(object):

    @staticmethod
    def from_slug(slug):
        url = '{0}/public/dashboards?slug={1}'.format(config.METADATA_URL, slug)
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            return Module(response.json())
        elif response.status_code == 404:
            return None
        else:
            #should raise error
            print response.status_code, response.body
            return None

    def __init__(self, json):
        self._json = json

        self.title = json['title']
        self.description = json.get('description', None)
        self.children = []
        self.data_source = None

        if 'dashboard-type' in json:
            self.children = \
                [Module(child) for child in json['modules']]
        elif json['module-type'] == 'tab':
            self.children = \
                [Module(child) for child in json['tabs']]
        else:
            self.data_source = DataSource(json['data-source'])


    def axes(self):
        module_type = self._json['module-type']
        json_axes = self._json.get('axes', None)

        if module_type == 'kpi':
            axes = {
                'x': {
                    'label': 'Quarter',
                    'key': '_quarter_start_at',
                    'format': 'date',
                },
                'y': [{
                    'label': self.title,
                    'key': self._json['value-attribute'],
                    'format': self._json['format'],
                }]
            }
        elif module_type == 'realtime':
            axes = merge_axes({
                'x': {
                    'label': 'Time',
                    'key': '_timestamp',
                    'format': 'time'
                },
                'y': [
                    {
                        'label': 'Number of unique visitors',
                        'key': 'unique_visitors',
                        'format': 'integer'
                    }
                ]
            }, json_axes)
        elif module_type == 'grouped_timeseries':
            axes = merge_axes({
                'x': {
                    'label': 'Date',
                    'key': '_start_at',
                    'format': {
                        'type': 'date',
                        'format': 'MMMM YYYY'
                    }
                }
            }, json_axes)

            for axis in axes['y']:
                axis['groupValue'] = axis['groupId']
                axis['groupKey'] = 'channel'
                axis['key'] = self._json['value-attribute']
                del axis['groupId']
        else:
            axes = None

        return axes


    def data(self):
        if self.data_source is None:
            return None

        raw_data = self.data_source.get()

        if raw_data is None:
            return None

        return data_to_table(self.axes(), raw_data)

    def all_data_sources(self):
        if self.data_source is None:
            return list(itertools.chain.from_iterable(
                [child.all_data_sources() for child in self.children]))
        else:
            return [self.data_source]

    def fetch(self):
        data_sources = self.all_data_sources()
        requests = [grequests.get(ds.url()) for ds in data_sources]
        responses = grequests.map(requests)

        for data_source, response in zip(data_sources, responses):
            data_source.parse_response(response)

    def render(self, depth=1):
        rendered_children = \
            '\n'.join([m.render(depth=depth+1) for m in self.children])

        return render_template('module.html',
            depth=depth,
            title=self.title,
            description=self.description,
            children=rendered_children,
            data=self.data(),
        )
