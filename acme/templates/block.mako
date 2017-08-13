## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .attr {color: rgb(200, 200, 200);}
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  .icon {display: inline !important;}
  </style>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui small header">
        <i class="yellow cube icon"></i> Block ${oitems.get('height')}
      </div>
      <div class="ui divided list">
        <div class="item">primechain: <span class="date">${oitems.get('primechain')}</span></div>
        <div class="item">difficulty: <span class="val">${oitems.get('difficulty')}</span></div>
        <div class="item">time: <span class="time" title="${oitems.get('time')+'.000Z'}">${oitems.get('time')}</span>&nbsp;&nbsp;<span class="attr">(${oitems.get('time').replace('T', ' ')})</span></div>
        <div class="item"><i class="yellow cube icon"></i> hash: <span class="val">${oitems.get('hash')}</span></div>
        %if oitems.get('previousblockhash', False):
          <div class="item"><i class="yellow cube icon"></i> previousblockhash: <span class="val">${oitems.get('previousblockhash')}</span></div>
        %endif
        %if oitems.get('nextblockhash', False):
          <div class="item"><i class="yellow cube icon"></i> nextblockhash: <span class="val">${oitems.get('nextblockhash')}</span></div>
        %endif
        <div class="item">headerhash: <span class="val">${oitems.get('headerhash')}</span></div>
        <div class="item">merkleroot: <span class="val">${oitems.get('merkleroot')}</span></div>
        %for txid in oitems.get('txids'):
         <div class="item"><i class="yellow money icon"></i> transaction: <a href="${request.route_url('transaction', net=net, arg=txid)}">${txid}</a></div>
        %endfor
        <div class="item"><div class="ui divider"></div></div>
        <div class="item">
          <a class="item" href="${request.route_url('block', net=net, arg=oitems.get('nextblockhash'))|n}"><button class="ui right floated ${'disabled' if oitems['height'] >= coin['binfo']['blocks'] else ''} mini primary button" style="margin-right:12em">Next block</button></a>
          <a class="item" href="${request.route_url('block', net=net, arg=oitems.get('previousblockhash'))}"><button class="ui left floated ${'disabled' if oitems['height'] == 0 else ''} mini primary button" style="margin-left:12em">Previous block</button></a>
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
</%def>
