## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .attr {color: rgb(200, 200, 200);}
  .amt {/*color: rgba(30, 112, 191, 0.9);*/color: rgba(96, 234, 96, 0.8); font-weight:bold; font-size:120%;}
  .pyqrline, .val {color: rgb(255, 230, 30);}
  .input, .date, .time {color: rgba(96, 234, 96, 0.8);}
  .output {color: #f12500;}
  .sotto {font-weight:normal; font-style:italic; font-size:80%;}
  .ui.card .meta>a:not(.ui), .ui.cards>.card .meta>a:not(.ui) {color:#4183c4;}
  .ui.card .meta>a:hover(.ui):hover, .ui.cards>.card .meta>a:not(.ui):hover {color:rgb(200, 200, 200);;}
  .card {background: transparent!important; color:rgb(200, 200, 200);}
  .ui.header.small .icon {display:inline!important;}
  </style>
  <script type="text/javascript" src="/js/sgvizler.js"></script>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">

      <div class="ui header">Transaction <span class="val">${"{hd}......{tl}".format(hd=txattrs['txid'][:18], tl=txattrs['txid'][-6:])}</span></div>
      <div class="ui items">
        <div class="item">
          <div class="ui small header">
            included in block: 
            <a href="${request.route_url('block', net=net, arg=txattrs['blockhash'])|n}" title="Go to block ${txattrs['height']}"
              >${txattrs['height']}</a>,
              minted 
              <span class="date">${txattrs['date']}</span>
              (<span class="attr sotto" title="${txattrs['date']}">${txattrs['date']}</span>),
              <span class="val">${txattrs['confirmations']}</span> confirmations.
          </div>
        </div>
      </div>

      <div class="ui small header">Inputs</div>
      <div class="ui grid">

        %for i, tx in enumerate(inputs):

          %if tx.get('coinbase'):
          <div class="four wide column">
            <div class="ui inverted segment">
              <span class="attr" style="font-style:italic">Coinbase minting</span><br/>
              <span class="val">${txattrs['confirmations']}</span>confirmations
              <br/>
              <span class="date"><i class="yellow wizard icon"></i> ${tx['coinbase'][:24]}...</span>
              <div class="ui divider"></div>
            </div>
          </div>

          %else:

          <div class="four wide column">
            <div class="ui inverted segment">
              %if tx.get('amount') is not None:
              <p>
                <i class="large icons" style="opacity:0.6"><i class="large yellow thin circle icon"></i> <i class="green key icon"></i></i> Pay-to-Pubkey
                <br/>
                <i class="yellow wizard icon"></i> <a href="${request.route_url('transaction', net=net, arg=tx['txid'])}" title="Details for ${tx['txid']}">${tx['txid'][:24]}...</a>
              </p>
              
              <p>
                <span class="attr">
                  <span class="amt">${tx.get('amount')}</span> ${coin['symbol']}
                  (<span class="val">${tx.get('confirmations', '000000')} confirmations)</span>
                </span>
              </p>

              %else:
              <p>
                <i class="large icons" style="opacity:0.6"><i class="large yellow thin circle icon"></i> <i class="green wizard icon"></i></i> Coinbase coin
                <br/>
                <i class="yellow wizard icon"></i> <a href="${request.route_url('transaction', net=net, arg=tx['txid'])}" title="Details for ${tx['txid']}">${tx['txid'][:24]}...</a>
              </p>
              
              <p>
                <span class="attr">
                  <span class="amt">?????</span>  ${coin['symbol']}
                  (<span class="val">????????? confirmations</span>)
                </span>
              </p>
              %endif
            </div>
          </div>

          %endif

        %endfor
      </div>

      <div class="ui divider"></div>

      <div class="ui inverted segment">
        <div class="ui small header">Outputs</div>
        <div class="ui cards">

          %for i, tx in enumerate(outputs):

          <div class="ui card">
            <div class="content">
              <img class="right floated tiny ui image" src="${tx['qrcode']|n}" title="${tx['address']}" />
              <div class="ui small header">
                <i class="yellow ${'hashtag' if 'pubkeyhash' in tx['scriptPubKey'].get('type','pubkey') else 'key'} icon" style="display:inline!important"></i> Pay-to-${tx['scriptPubKey'].get('type','pubkey').capitalize()}<br/><br/>
              <span class="output">${tx['value']}</span>
              <span class="attr"> ${coin['symbol']}</span>
              </div>
              <div class="meta">
                <span class="attr" style="font-size:88%"><a href="${request.route_url('address', net=net, arg=tx['address'])}" title="Browse transactions for address ${tx['address']}">${tx['address']}</a>
              </div>
              <div class="description">
                <div class="ui divider"></div>

                %for l in tx['scriptPubKeynice']['asm']:

                  <p><span class="val">${l}</span></p>

                %endfor

                </div>
              </div>
            </div>

          %endfor

        </div>
      </div>
    </div>
    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed JSON response</div>
      <div class="content">
        ${dump|n}
      </div>
    </div>
  </div>

</%def>

