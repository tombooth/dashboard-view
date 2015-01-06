(function(d3, c3, format) {

  var modules = document.querySelectorAll('section.module');

  function parse_axes(table) {
    var header_cells = table.querySelectorAll('th'),
        rows = table.querySelectorAll('tr'),
        axes = new Array(header_cells.length);

    [].forEach.call(header_cells, function(header_cell, i) {
      axes[i] = {
        format_options: JSON.parse(header_cell.getAttribute('data-format')),
        label: header_cell.innerText,
        data: [],
      }
    });

    [].forEach.call(rows, function(row) {
      [].forEach.call(row.querySelectorAll('td'), function(cell, i) {
        axes[i].data.push(JSON.parse(cell.getAttribute('data-raw')));
      });
    });

    return axes;
  }

  [].forEach.call(modules, function(module_element) {
    var table = module_element.querySelector('details:first-of-type'),
        axes = parse_axes(table);

    var chart = c3.generate({
      data: {
        x: axes[0].label,
        xFormat: "%Y-%m-%dT%H:%M:%S+00:00",
        columns: axes.map(function(axis) {
          var data = axis.data;

          if (Array.isArray(data[0])) {
            data = data.map(function(datum) { return datum[0]; });
          } else {
            data = data.slice();
          }

          data.unshift(axis.label);

          return data;
        })
      },
      axis: {
        x: {
          type: 'timeseries',
          tick: { format: format.bind(null, axes[0].format_options) }
        },
        y: {
          tick: { format: format.bind(null, axes[1].format_options) }
        }
      }
    });

    module_element.querySelector('.visualisation').appendChild(chart.element);
  });

})(window.d3, window.c3, window.format);
