import config
import json
import requests

from collections import OrderedDict
from flask import render_template

from data_source import DataSource
from formatting import format


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


def group_by_x(x_key, data):
    groupped = OrderedDict()
    for datum in data:
        k = tuple([datum[p] for p in x_key]) if isinstance(x_key, list) else datum[x_key]
        try:
            groupped[k].append(datum)
        except KeyError:
            groupped[k] = [datum]
    return groupped


def find_by_grouping(axis, data):
    key = axis['groupKey']
    value = axis['groupValue']

    for datum in data:
        try:
            if datum[key] == value:
                return datum
        except KeyError:
            print datum

    return None


def data_to_table(axes, data):
    if axes is None or 'x' not in axes or 'y' not in axes:
        return None

    groupped_data = group_by_x(axes['x']['key'], data)

    rows = []
    x_axis_format = axes['x'].get('format', {})
    for x_value, data in groupped_data.iteritems():
        row = [{ 'raw': x_value, 'formatted': format(x_value, x_axis_format)}]
        for axis in axes['y']:
            formatting = axis.get('format', {})

            if 'groupKey' in axis and 'groupValue' in axis:
                datum = find_by_grouping(axis, data)
            else:
                datum = data[0]

            if datum is not None:
                value = datum[axis['key']]
                row.append({
                    'formatted': format(value, formatting),
                    'raw': value,
                })
            else:
                row.append({
                    'formatted': None,
                    'raw': None,
                })
        rows.append(row)

    try:
        fields = [{
            'label': axes['x']['label'],
            'format': json.dumps(axes['x'].get('format', {}),)
        }] + [{
            'label': axis['label'],
            'format': json.dumps(axis.get('format', {})),
        } for axis in axes['y']]
    except KeyError:
        fields = [{
            'label': '',
            'format': '{}',
        }] * len(rows[0])
        print self.data_source.url()
        print self._json['module-type']

    return {
        'fields': fields,
        'rows': rows,
    }

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
        self.children = None
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


    def render(self, depth=1):
        rendered_children = None

        if self.children is not None:
            rendered_children = \
                '\n'.join([m.render(depth=depth+1) for m in self.children])

        return render_template('module.html',
            depth=depth,
            title=self.title,
            description=self.description,
            children=rendered_children,
            data=self.data(),
        )
