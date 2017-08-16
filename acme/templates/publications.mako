## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .val {color: rgb(255, 230, 30);}
  .txt {color: rgba(255, 255, 255, 0.7);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  </style>
</%def>

<%def name="body()">
  <div class="ui container" style="margin:4.6em">
    <div class="ui inverted segment dark">
      <div class="ui header">Publications</div>
      <table class="ui inverted celled striped table">
        <thead>
          <tr>
            <th>Inscribed</th>
            <th>Inscription</th>
            <th>Transaction</th>
            <th>Block</th>
          </tr>
        </thead>

        <tbody>
        %for pub in pubs:
          <tr>
            <td>
              <span class="date" title="${pub[2]['time'][:-4].replace(' ', 'T')+'Z'|n}">
                ${pub[2]["time"]|n}
              </span>
            </td>
            <td class="aligned">
              <i class="yellow ticket icon"></i>
              <span class="txt">
              % if pub[0].startswith('magnet'):
                ${'<a href="{}">{}</a>'.format(pub[0], pub[0])|n}
              % else: 
                ${pub[0]}
              %endif
              </span>
            </td>
            <td>
              <i class="yellow money icon"></i>
              <a href="${request.route_url('transaction', net=net, arg=pub[3])}">
                ${pub[3][5:20]}...
              </a>
            </td>
            <td>
              <i class="yellow cube icon"></i>
              <a href="${request.route_url('block', net=net, arg=pub[1])}">${pub[2]["height"]}</a>
            </td>
          </tr>
        %endfor
        </tbody>
      </table>
    </div>
    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed SPARQL response</div>
      <div class="content">
        <div class="ui inverted segment dark"><pre>${dump|n}</pre></div>
      </div>
    </div>
  </div>
</%def>
