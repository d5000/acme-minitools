## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="False"/>
<%def name="header()">
  <title>ACME - SLIM</title>
  <style type="text/css">
    .valcol {color:rgb(96, 234, 96); font-style: normal;}
    .muted {color: rgba(255, 255, 255, 0.6);}
    .sotto {font-weight:normal; font-style:italic; font-size:80%;}
    .val {color: rgb(255, 230, 30);}
    .coinlogo {float: left; vertical-align:middle; margin-right:0.6em; height:1.3em; width:1.3em}
    /* td {color: rgba(232, 219, 166, 0.81);} */
    .smry.ui.inverted.table tbody tr td {font-style: italic; color: rgba(255, 255, 255, 0.74);} 
    .neg {color: rgba(255, 0, 0, 0.91);}
    .pos {color: rgba(96, 234, 96, 0.8);}
    .opos {color: rgba(255, 230, 30, 0.8);}
    .ui-datepicker-calendar {display: none;}
  </style>
  <style>
    body {/*font: 10px sans-serif;*/}
    text {fill: #ccc;}
    text.symbol {fill: #BBBBBB;}
    path {
        fill: none;
        stroke-width: 1;
    }
    path.candle {
        stroke: #fff;
    }
    path.candle.body {
        stroke-width: 0;
    }
    path.candle.up {
        fill: #00AA00;
        stroke: #00AA00;
    }
    path.candle.down {
        fill: #FF0000;
        stroke: #FF0000;
    }
    .close.annotation.up path {
        fill: #00AA00;
    }
    path.volume {
        fill: #DDDDDD;
    }
    .indicator-plot path.line {
        fill: none;
        stroke-width: 1;
    }
    /*
    .ma-0 path.line {
        stroke: #1f77b4;
    }
    .ma-1 path.line {
        stroke: #aec7e8;
    }
    .ma-2 path.line {
        stroke: #ff7f0e;
    }
    */
    button {/*position:absolute; right:110px; top:25px;*/}
    /*
    path.macd {
        stroke: #0000AA;
    }
    */
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
    /*
    path.rsi {
        stroke: #fff;
    }
    */
    path.overbought, path.oversold {
        stroke: #FF9999;
        stroke-dasharray: 5, 5;
    }
    path.middle, path.zero {
        stroke: #BBBBBB;
        stroke-dasharray: 5, 5;
    }
    .analysis path, .analysis circle {
        stroke: blue;
        stroke-width: 0.8;
    }
    .trendline circle {
        stroke-width: 0;
        display: none;
    }
    .mouseover .trendline path {
        stroke-width: 1.2;
    }
    .mouseover .trendline circle {
        stroke-width: 1;
        display: inline;
    }
    .dragging .trendline path, .dragging .trendline circle {
        stroke: darkblue;
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
    /*
    .supstance path {
        stroke-dasharray: 2, 2;
    }
    .supstances .interaction path {
        pointer-events: all;
        cursor: ns-resize;
    }
    .mouseover .supstance path {
        stroke-width: 1.5;
    }
    .dragging .supstance path {
        stroke: darkblue;
    }
    */
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
    /*
    .tradearrow path.tradearrow {
        stroke: none;
    }
    .tradearrow path.buy {
        fill: #0000FF;
    }
    .tradearrow path.sell {
        fill: #9900FF;
    }
    .tradearrow path.highlight {
        fill: none;
        stroke-width: 2;
    }
    .tradearrow path.highlight.buy {
        stroke: #0000FF;
    }
    .tradearrow path.highlight.sell {
        stroke: #9900FF;
    }
    */
    .axis path,
    .axis line {
      fill: none;
      stroke: #ddd;
      shape-rendering: crispEdges;
    }
  </style>
  <script src="/js/sgvizler.js" type="text/javascript"></script>
  <script src="/js/d3.min.js" type="text/javascript"></script>
  <script src="/js/techan.js" type="text/javascript"></script>
</%def>

<%def name="body()">

  <table class="smry ui inverted table">
    <tbody>
      <tr>
        <td><span class="attr">${timestamp.strftime("%c")|n}</span></td>
        <td>last mint: <span class="valcol">${str((now-coin.get('lastblocktime')).seconds)|n}s</span> ago,&nbsp;&nbsp;pow/pob: <span class="valcol">${curpowdiff|n}</span>,&nbsp;&nbsp;pos: <span class="valcol">${curposdiff|n}</span></td>
        <td>supply: <span class="valcol">${"{:.0f}".format(float(coin['binfo']['moneysupply']) - float(netburnedcoins))}</span>&nbsp;&nbsp;(mint: <span class="valcol">${"{:.0f}".format(float(coin['binfo']['moneysupply']))}</span>&nbsp;-&nbsp;burn: <span class="valcol">${"{:.0f}".format(float(netburnedcoins))}</span>)</td>
        <td>nethash: <span class="valcol">${"{:.2f}".format(curhashrate * 1000)|n}</span> mh/s,&nbsp;&nbsp;nodes: <span class="valcol">${coin['binfo']['connections']}</span>
            </div>
        </td>
      </tr>
    </tbody>
  </table>

  <table class="ui inverted table">
    <thead>
      <tr>
        <th>Block</th>
        <th>Hash</th>
        <th>Diff</th>
        <th>Minted</th>
        <th>Time (UTC)</th>
        <th>interval</th>
        <th>Tx# &middot; Value out</th>
      </tr>
    </thead>
    <tbody>
    %for bnum, bhash, bdiff, prooftype, bblock, btime, binterval, txc, vout in blocks[:6]:
    <tr class="illu">
      <td><i class="yellow cube icon"></i> ${bnum}</td>
      <td><a href="${request.route_url('block', net=net, arg=bhash)}">${bhash[:16]} ...</a></td>
      <td>${"{:.6f}".format(bdiff)|n}</td>
      <td>${dict(burn='<i class="red fire icon"></i>',stake='<i class="blue laptop icon"></i>',work='<i class="green desktop icon"></i>').get(prooftype.split(' ')[0][9:], '<i class="yellow help circle outline icon"></i>')|n}</td>
      <td><span class="time" title="${btime}">${btime}</span>&nbsp;&nbsp;(<span class="muted sotto">${btime}</span>)</td>
      <td>
      %if binterval < 0:
        <span class="neg"><time>${"{:<+.0f}".format(binterval)|n}</time></span>
      %elif binterval > 450:
        <span class="opos"><time>${"{:<+.0f}".format(binterval)|n}</time></span>
      %else:
        <span class="pos"><time>${"{:<+.0f}".format(binterval)|n}</time></span>
      %endif
      </td>
      ## <td>${txc} &middot; <span class="val">${"{:.2f}".format(vout)|n}</span></td>
      <td>${txc} <i class="yellow money icon"></i> <span class="val">${"{:.2f}".format(vout)|n}</span></td>
    </tr>
    %endfor
    </tbody>
  </table>

  <div class="ui container">
  ${difflag|n}
  </div>
</%def>
