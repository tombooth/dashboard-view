(function(d3, c3, format) {

  var module_tables = document.querySelectorAll('section.module > table');

  [].forEach.call(module_tables, function(table) {
    var header_cells = table.querySelectorAll('th'),
        rows = table.querySelectorAll('tr'),
        axes = new Array(header_cells.length);

    [].forEach.call(header_cells, function(header_cell, i) {
      axes[i] = {
        format_options: JSON.parse(header_cell.getAttribute('data-format')),
        data: [header_cell.innerText],
      }
    });

    [].forEach.call(rows, function(row) {
      [].forEach.call(row.querySelectorAll('td'), function(cell, i) {
        axes[i].data.push(cell.getAttribute('data-raw'));
      });
    });

    var chart = c3.generate({
      data: {
        x: axes[0].data[0],
        xFormat: "%Y-%m-%dT%H:%M:%S+00:00",
        columns: axes.map(function(axis) { return axis.data; })
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

    table.parentNode.appendChild(chart.element);

  });

})(window.d3, window.c3, window.format);
