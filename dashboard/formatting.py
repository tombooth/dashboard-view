import arrow
import logging
import moment


def format_integer(value, options):
    if value is None:
        return "0"
    else:
        return str(int(value))


def format_date_range(value, options):
    start = arrow.get(value[0])
    end = arrow.get(value[1])

    start_format = 'D'
    if start.datetime.year != end.datetime.year:
        start_format += ' MMMM YYYY'
    elif start.datetime.month != end.datetime.month:
        start_format += ' MMMM'

    return '{0} to {1}'.format(
        start.format(start_format),
        end.format('D MMMM YYYY')
    )


def format_date(value, options):
    if isinstance(value, tuple) or isinstance(value, list):
        return format_date_range(value, options)
    else:
        return arrow.get(value).format('D MMMM YYYY')


def format_time(value, options):
    return arrow.get(value).format('h:mma')


type_fn_map = {
    'integer': format_integer,
    'date': format_date,
    'time': format_time,
}


def format(value, options):
    if isinstance(options, basestring):
        return format(value, { 'type': options })

    try:
        type_fn = type_fn_map[options['type']]
    except KeyError:
        logging.warning('No formatter for type "{0}"'.format(options['type']))
        return value

    return type_fn(value, options)
