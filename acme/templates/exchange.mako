## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <link rel="stylesheet" href="/css/techansite.css" type="text/css" />
  <script src="/js/d3.v4.min.js" type="text/javascript"></script>
  <script src="/js/techan.js" type="text/javascript"></script>
  <script src="/js/dependencies.js" type="text/javascript"></script>
  <script src="/js/techansite.js" type="text/javascript"></script>
  <style type="text/css">
  </style>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui container chartcontainer">
      <div id="bigChart"></div>
      <div class="text-center">
          <a href="https://github.com/andredumas/techan.js/blob/gh-pages/src/js/index.js">Chart Source</a>
      </div>
    </div>

  <script>
      (function(window, d3, techanSite) {
          d3.select('div#bigChart').call(techanSite.bigchart);
          window.onresize = function() {
              d3.select('div#bigChart').call(techanSite.bigchart.resize);
          };
      })(window, d3, techanSite);
  </script>
</%def>
