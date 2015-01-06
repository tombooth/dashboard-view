import json

from collections import OrderedDict

from formatting import format


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
        row = [{
            'formatted': format(x_value, x_axis_format),
            'raw': json.dumps(x_value),
        }]
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
                    'raw': json.dumps(value),
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
