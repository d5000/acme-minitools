<%inherit file="acme:templates/base.mako"/>
<%page cached="False"/>
<%def name="header()">
  <title>ACME - ${coin['symbol']}</title>
  <style type="text/css">
  </style>
</%def>

<%def name="body()">

<div class="ui two column grid container" style="margin-top:4.6em"> 
  <div class="row">
    <div class="column">
      <span class="ui small header">${coin['name']} Mainnet</span>
    </div>
    <div class="column">
      <span class="ui small header">${coin['name']} Testnet</span>
    </div>
  </div>
  <div class="row">
    <div class="column">
      <a href="${request.route_url('index', net='main')}" class="ui medium image">
        <img class="ui medium circular image" src="/img/coin.png">
      </a>
    </div>
    <div class="column">
      <a href="${request.route_url('index', net='test')}" class="ui medium image">
        <img class="ui medium circular image" src="/img/coin_testnet.png">
      </a>
    </div>
  </div>
</div>
</%def>
