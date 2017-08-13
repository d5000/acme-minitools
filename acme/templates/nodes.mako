## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .attr {color: rgb(200, 200, 200);}
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  .active { fill: blue !important;}
  .hoverinfo {background-color: #222 !important; color: #ffe61e;}
  svg {width: 100%;height: 100%;}
  path.slice{stroke-width:2px;}
  polyline{opacity: .3; stroke: rgba(255,255,255,0.7); stroke-width: 2px; fill: none;}
  g.labels text {fill: rgba(255,255,255,0.7);}
  /*.datamaps-key dt, .datamaps-key dd {float: none !important;}
  .datamaps-key {right: -50px; top: 0;}*/
  </style>
  <script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.5.3/d3.min.js"></script>
  <script src="//cdnjs.cloudflare.com/ajax/libs/topojson/1.6.9/topojson.min.js"></script>
  ## <script src="/js/d3.v3.min.js"></script>
  <script src="/js/datamaps.world.hires.js"></script>
  <script src="http://techanjs.org/techan.min.js"></script>
</%def>

<%def name="body()">
  <div class="ui container" style="margin:4.6em">
    <div class="ui inverted segment dark">
      <div class="ui header">Geoip-derived locations of hosted peers</div>
      <div id="container" style="position: relative; width: 900px; height: 600px;"></div>
      <div class="ui inverted segment dark">
        <style type="text/css">.ui.basic.yellow.label {background-color: transparent !important; border-color: rgba(255, 230, 30, 0.4) !important;}</style>
        % for k, v in freqcnt.items():
        <div>
          <div class="ui tiny header"><tt>${k}</tt>
            <i class="${k.lower()} flag"></i>
            <div class="ui basic yellow mini label">
              <span style="margin-right:${str(v * 10)}px; color:rgba(255,255,255,0.7)">${v}</span>
            </div>
          </div>
        <div>
        % endfor
      </div>
    </div>
    <div class="ui inverted segment dark">
      <div class="ui cards">
        %for node in nodes:
        <div class="ui black card" style="background: transparent;">
          <div class="content">
            <div class="ui small header"><span class="category">${node['geoloc']['country_name']|n}: ${node['addr'].split(':')[0]|n}<span class="right floated time"><i class="${node['geoloc']['country_code'].lower()|n} flag"></i></span>
              </span></div>
            <div class="meta">
              <span class="right floated time"><span class="attr">inbound:</span> ${node['inbound']}</span>
              <span class="left floated time"><span class="attr">banscore:</span> ${node['banscore']}</span>
            </div>
            <div class="description" >
              %for attr in ["conntime", "lastrecv", "lastsend"]:
                <div class="ui item"><span class="attr">${attr|n}</span> - <span class="date"><time title="${str(node[attr])|n}">${str(node[attr])|n}</time></span></div>
              %endfor
              <div class="ui item"><span class="attr">subver:</span> - <span class="val">${node['subver'].split('/')[1] if '/' in node['subver'] else node['subver']}</span></div>
            </div>
          </div>
          <div class="extra content">
            <div class="right floated author">
              v${node['version']}
            </div>
            <div class="left floated author">
              Service level: ${node['services']} 
            </div>
          </div>
        </div>
        %endfor
      </div>
    </div>
    <div class="ui inverted segment dark">
      <div class="ui header">Client versions: total of <span class="val">${sum(v['value'] for v in versions)}</span> clients, <span class="val">${len(versions)}</span> different versions.</div>
      <div id="donut"></div>
    </div>

    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed JSON API response</div>
      <div class="content">
        <div class="ui inverted segment dark"><pre>${dump|n}</pre></div>        
      </div>
    </div>
  </div>
  <script>
      // example data from server
      var series = ${cchosts|n};
      // Datamaps expect data in format:
      // { "USA": { "fillColor": "#42a844", numberOfWhatever: 75},
      //   "FRA": { "fillColor": "#8dc386", numberOfWhatever: 43 } }
      var dataset = {};
      // We need to colorize every country based on "numberOfWhatever"
      // colors should be uniq for every value.
      // For this purpose we create palette(using min/max series-value)
      var onlyValues = series.map(function(obj){ return obj[1]; });
      var minValue = Math.min.apply(null, onlyValues),
              maxValue = Math.max.apply(null, onlyValues);
      // create color palette function
      // color can be whatever you wish
      var paletteScale = d3.scale.linear()
              .domain([minValue,maxValue])
              .range(["#ffd942","#ffcc00"]); // blue color
      // fill dataset in appropriate format
      series.forEach(function(item){ //
          // item example value ["USA", 70]
          var iso = item[0], value = item[1];
          dataset[iso] = { numberOfThings: value, fillColor: paletteScale(value) };
      });
      // render map
      new Datamap({
          element: document.getElementById('container'),
          projection: 'mercator', // big world map
          // countries don't listed in dataset will be painted with this color
          fills: { defaultFill: '#222' },
          data: dataset,
          geographyConfig: {
              borderColor: '#DEDEDE',
              highlightBorderWidth: 2,
              // don't change color on mouse hover
              highlightFillColor: function(geo) {
                  return geo['fillColor'] || '#222';
              },
              // only change border
              highlightBorderColor: '#B7B7B7',
              // show desired information in tooltip
              popupTemplate: function(geo, data) {
                  // don't show tooltip if country don't present in dataset
                  if (!data) { return ; }
                  // tooltip content
                  return ['<div class="hoverinfo">',
                      '<strong>', geo.properties.name, '</strong>',
                      '<br>Count: <strong>', data.numberOfThings, '</strong>',
                      '</div>'].join('');
              }
          }
      });
  </script>
  <script>
    var width = 960,
        height = 450,
      radius = Math.min(width, height) / 2;

    var pie = d3.layout.pie()
      .sort(null)
      .value(function(d) {
        return d.value;
      });

    var arc = d3.svg.arc()
      .outerRadius(radius * 0.8)
      .innerRadius(radius * 0.4);

    var outerArc = d3.svg.arc()
      .innerRadius(radius * 0.9)
      .outerRadius(radius * 0.9);

    var svg = d3.select("#donut")
      .append("svg")
        .attr("width", width)
        .attr("height", height)
      .append("g")

    svg.append("g")
      .attr("class", "slices");
    svg.append("g")
      .attr("class", "labels");
    svg.append("g")
      .attr("class", "lines");

    svg.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var key = function(d){ return d.data.label; };

    var color = d3.scale.ordinal()
      .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

    function Data (){
      return ${str(versions)|n};
    };

    function render(data) {

      /* ------- PIE SLICES -------*/
      var slice = svg.select(".slices").selectAll("path.slice")
        .data(pie(data), key);

      slice.enter()
        .insert("path")
        .style("fill", function(d) { return color(d.data.label); })
        .attr("class", "slice");

      slice   
        .transition().duration(1000)
        .attrTween("d", function(d) {
          this._current = this._current || d;
          var interpolate = d3.interpolate(this._current, d);
          this._current = interpolate(0);
          return function(t) {
            return arc(interpolate(t));
          };
        })

      slice.exit()
        .remove();

      /* ------- TEXT LABELS -------*/

      var text = svg.select(".labels").selectAll("text")
        .data(pie(data), key);

      text.enter()
        .append("text")
        .attr("dy", ".35em")
        .text(function(d) {
          return d.data.label + ' (' + d.data.value + ')';
        });
      
      function midAngle(d){
        return d.startAngle + (d.endAngle - d.startAngle)/2;
      }

      text.transition().duration(1000)
        .attrTween("transform", function(d) {
          this._current = this._current || d;
          var interpolate = d3.interpolate(this._current, d);
          this._current = interpolate(0);
          return function(t) {
            var d2 = interpolate(t);
            var pos = outerArc.centroid(d2);
            pos[0] = radius * (midAngle(d2) < Math.PI ? 1 : -1);
            return "translate("+ pos +")";
          };
        })
        // .styleTween("fill", "#fff")
        .styleTween("text-anchor", function(d){
          this._current = this._current || d;
          var interpolate = d3.interpolate(this._current, d);
          this._current = interpolate(0);
          return function(t) {
            var d2 = interpolate(t);
            return midAngle(d2) < Math.PI ? "start":"end";
          };
        });

      text.exit()
        .remove();

      /* ------- SLICE TO TEXT POLYLINES -------*/

      var polyline = svg.select(".lines").selectAll("polyline")
        .data(pie(data), key);
      
      polyline.enter()
        .append("polyline");

      polyline.transition().duration(1000)
        .attrTween("points", function(d){
          this._current = this._current || d;
          var interpolate = d3.interpolate(this._current, d);
          this._current = interpolate(0);
          return function(t) {
            var d2 = interpolate(t);
            var pos = outerArc.centroid(d2);
            pos[0] = radius * 0.95 * (midAngle(d2) < Math.PI ? 1 : -1);
            return [arc.centroid(d2), outerArc.centroid(d2), pos];
          };      
        });
      
      polyline.exit()
        .remove();
    };

    render(Data());

  </script>


</%def>
