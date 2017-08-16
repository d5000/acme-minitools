## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .valcol {color:rgb(96, 234, 96); font-style: normal;}
  .coinlogo {float: left; vertical-align:middle; margin-right:0.6em; height:1.3em; width:1.3em}
  .attr {color: rgb(200, 200, 200);}
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  .sotto {font-weight:normal; font-style:italic; font-size:80%;}
  /* td {color: rgba(232, 219, 166, 0.81);} */
  .smry.ui.inverted.table tbody tr td {font-style: italic; color: rgba(255, 255, 255, 0.74);} 
  .neg {color: rgba(255, 0, 0, 0.91);}
  .pos {color: rgba(96, 234, 96, 0.8);}
  .opos {color: rgba(255, 230, 30, 0.8);}
  .ui-datepicker-calendar {display: none;}
  </style>
</%def>

<%def name="body()">

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
    %for bnum, bhash, bdiff, prooftype, bblock, btime, binterval, txc, vout in blocks:
    <tr class="illu">
      <td><i class="yellow cube icon"></i> ${bnum}</td>
      <td><a href="${request.route_url('block', net=net, arg=bhash)}">${bhash[:16]|n} ...</a></td>
      <td>${"{:.6f}".format(bdiff)|n}</td>
      <td>${dict(burn='<i class="red fire icon"></i>',stake='<i class="blue laptop icon"></i>',work='<i class="green desktop icon"></i>').get(prooftype.split(' ')[0][9:], '<i class="yellow help circle outline"></i>')|n}</td>
      <td><span class="date time" title="${btime}">${btime}</span>&nbsp;&nbsp;(<span class="sotto muted">${btime}</span>)</td>
      <td>
      %if binterval < 0:
        <span class="neg"><time>${"{:<+.0f}".format(binterval)|n}</time></span>
      %elif binterval > 450:
        <span class="opos"><time>${"{:<+.0f}".format(binterval)|n}</time></span>
      %else:
        <span class="pos"><time>${"{:<+.0f}".format(binterval)|n}</time></span>
      %endif
      </td>
      <td>${txc} <i class="yellow money icon"></i> <span class="val">${"{:.2f}".format(vout)|n}</span></td>
    </tr>
    %endfor
    </tbody>
  </table>
  <div class="ui list">
  ${pag|n}
  </div>
</%def>
