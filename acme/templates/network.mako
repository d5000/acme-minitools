## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <script src="https://d3js.org/d3-time.v1.min.js"></script>
  <script src="/js/d3.v4.min.js"></script>
  <script src="/js/techan.js"></script>
  <style type="text/css">
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  text {fill: #ccc;}
  text.symbol {fill: #BBBBBB;}
  path {
      fill: none;
      stroke-width: 1;
  }
  .indicator-plot path.line {
      fill: none;
      stroke-width: 1;
  }
  path.signal {
      stroke: #FF9999;
  }
  path.zero {
      stroke: #BBBBBB;
      stroke-dasharray: 0;
      stroke-opacity: 0.5;
  }
  path.difference {
      fill: #BBBBBB;
      opacity: 0.5;
  }
  .interaction path, .interaction circle {
      pointer-events: all;
  }
  .interaction .body {
      cursor: move;
  }
  .trendlines .interaction .start, .trendlines .interaction .end {
      cursor: nwse-resize;
  }
  .crosshair {
      cursor: crosshair;
  }
  .crosshair path.wire {
      stroke: #DDDDDD;
      stroke-dasharray: 1, 1;
  }
  .crosshair .axisannotation path {
      fill: #DDDDDD;
  }
  .axis path,
  .axis line {
    fill: none;
    stroke: #ddd;
    shape-rendering: crispEdges;
  }
  </style>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui header">Mean block emission time (target 90 seconds)</div>
      <div class="ui inverted segment">
        ${chart|n}
      </div>
      <div class="ui mini item"><i>(Taken from <a href="https://pepprseed.github.io/svgdatashapes/pages/e4.html" title="SVGDataShapes Github repository">https://pepprseed.github.io/svgdatashapes/</a>)</i>
      </div>
    </div>

    <div class="ui inverted segment dark">
      <div class="ui header">Daily emissions, launch (2014-06-28) to date</div>
      <div class="ui inverted segment">
        <div class="ui container">
          <svg id="plot" width="960" height="350"></svg>
        </div>
      </div>
    </div>

    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed JSON API response</div>
      <div class="content">
        ${dump|n}
      </div>
    </div>
  </div>

  <script>
    var svg = d3.select("#plot"),
        margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = +svg.attr("width") - margin.left - margin.right,
        height = +svg.attr("height") - margin.top - margin.bottom,
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var parseTime = d3.timeParse("%Y-%m-%d");

    var x = d3.scaleTime()
        .rangeRound([0, width]);

    var y = d3.scaleLinear()
        .rangeRound([height, 0]);

    var line = d3.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.blocks); });

    d3.tsv("/css/emissions.tsv", function(d) {
      d.date = parseTime(d.Date);
      d.blocks = parseInt(d.Blocks, 10);
      return d;
    }, function(error, data) {
      if (error) throw error;

      x.domain(d3.extent(data, function(d) { return d.date; }));
      y.domain(d3.extent(data, function(d) { return d.blocks; }));

      g.append("g")
          .attr("transform", "translate(0," + height + ")")
          .call(d3.axisBottom(x))
        .select(".domain")
          .remove();

      g.append("g")
          .call(d3.axisLeft(y))
        .append("text")
          .attr("fill", "#000")
          // .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", "0.71em")
          .attr("text-anchor", "end")
          .text("Blocks");

      g.append("path")
          .datum(data)
          .attr("fill", "none")
          .attr("stroke", "steelblue")
          .attr("stroke-linejoin", "round")
          .attr("stroke-linecap", "round")
          .attr("stroke-width", 0.01)
          .attr("d", line);
    });
  </script>


</%def>
