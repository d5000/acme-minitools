## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  </style>
</%def>

<%def name="body()">
  <div class="ui container">
    <div class="ui inverted segment dark">
      <div id="myForm"></div>
    </div>
    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed JSON API response</div>
      <div class="content">
        <div class="ui inverted segment dark"><pre>${dump|n}</pre></div>
      </div>
    </div>
  </div>
</%def>
