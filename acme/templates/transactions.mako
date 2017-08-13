## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .card {background-color: transparent !important;}
  .attr {color: rgb(200, 200, 200);}
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  </style>
  <script type="text/javascript" src="/js/sgvizler.js"></script>
</%def>

<%def name="body()">
  <div class="ui container" style="margin:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui header">Transactions recorded in the last 30 minutes</div>
      <div class="ui inverted cards">
        %for tx in txs:
          <div class="card">
            <div class="content">
              <img style="height:1.6em;width:1.6em" class="right floated mini ui image" src="/img/coin${'_testnet' if coin['binfo']['testnet'] else ''}.png">
              <div class="header">
              Block: ${tx[1]}
                ## <a href="${request.route_url('transaction', arg=tx[0])}" title="Browse transaction details">${tx[0][:20]}...</a>
              </div>
              <div class="meta">
                <span title="${tx[2]}" class="val">${tx[2]}</span>
              </div>
              <div class="description">
                <span class="attr">at <span class="date">${tx[2]}</span></span>
              </div>
            </div>
            <div class="content">
            %for txd in tx[0]:
              <span><span class="date">${txd['confirmations']}</span>&nbsp;<a href="${request.route_url('transaction', net=net, arg=txd['txid'])}" title="Browse transaction details">${txd['txid'][:12]}...</a>&nbsp;<span class="val">${txd['vout'][-1]['value']}</span>&nbsp;<span class="date">${txd['vout'][-1]['scriptPubKey']['type']}</span></span>
            %endfor
            </div>
          </div>            
        %endfor
      </div>
    </div>
    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed JSON</div>
      <div class="content">
        ${dump|n}
      </div>
    </div>
</%def>
