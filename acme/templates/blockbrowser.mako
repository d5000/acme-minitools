## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>

  ## <script src="http://ajax.googleapis.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
  ## <script>
  ##     window.jQuery || document.write('<script src="js/jquery-2.0.3.min.js"><\/script>')
  ## </script>

  <script type="text/javascript" src="/js/lodlive/jquery-ui-1.9.2.min.js"></script>
  <link rel="stylesheet" href="/js/lodlive/jquery.fancybox/jquery.fancybox.css" type="text/css" media="all" />
  <link rel="stylesheet" href="/css/lodlive/lodlive.core.css" type="text/css" media="all" />
  <link rel="stylesheet" href="/css/lodlive/lodlive.profile.css" type="text/css" media="all" />
  <link rel="stylesheet" href="/css/lodlive/lodlive.app.css" type="text/css" media="all" />

  <script type="text/javascript" src="/js/lodlive/jquery.fancybox/jquery.fancybox.pack.js"></script>
  <script type="text/javascript" src="/js/lodlive/jquery.slimScroll.min.js"></script>
  <script type="text/javascript" src="/js/lodlive/jquery.json-2.3.min.js"></script>
  <script type="text/javascript" src="/js/lodlive/jquery.jsonp-2.4.0.min.js"></script>
  <script type="text/javascript" src="/js/lodlive/jquery.jstorage.js"></script>
  <script type="text/javascript" src="/js/lodlive/jquery.jcanvas.js"></script>
  <script type="text/javascript" src="/js/lodlive/jquery.doTimeout.js"></script>
  <script type="text/javascript" src="http://maps.google.com/maps/api/js"></script>
  <script type="text/javascript" src="/js/lodlive/jquery.gmap3.js"></script>
  <script type="text/javascript" src="/js/lodlive/jquery.ThreeDots.min.js"></script>

  <script type="text/javascript" src="/js/lodlive/lodlive.profile.js"></script>
  <script type="text/javascript" src="/js/lodlive/lodlive.core.js"></script>
  <script type="text/javascript" src="/js/lodlive/lodlive.lang.js"></script>
  <script type="text/javascript" src="/js/lodlive/lodlive.utils.js"></script>
  <script type="text/javascript" src="/js/lodlive/lodlive.custom-lines.js"></script>
  <script type="text/javascript" src="/js/lodlive/lodlive.app.js"></script>
  <script type="text/javascript">
      $.jStorage.set('selectedLanguage', 'en')
  </script>
</%def>

<%def name="body()">

  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui small header">
        <i class="yellow cube icon"></i> Block Graph
      </div>
      <div id="bgraph" style="height:350px" class="ui inverted segment dark">
        <div id="startPanel">
          <div id="boxes">
              <div id="firstLineBoxes"></div>
          </div>
        </div>
      </div>
        <!--
        <div class="help hd">
            <div>
                <h2>HELP</h2>
                <p>
                    <a href="http://www.youtube.com/embed/BQ9Ckh2ov-c?rel=0" class="sprite videoHelp"></a>
                </p>
                <p>
                    Here you can follow the direct and inverse connections provided by the resource by moving freely from one "circle" to the others.
                </p>
                <p>
                    Every new pop-open resource will guide the user to those relating to it, automatically connecting the new "circle" to the ones they have already opened.
                </p>
                <p>
                    Every time an owl:sameAs property is reached throughout the course of navigation, LodLive will connect to the related endpoint, enabling the user to move to the new available resources within the same navigation environment.
                </p>
            </div>
        </div>
        <div class="legenda hd">
            <div>
                <h2>SYMBOL LEGEND</h2>
                <ul class="optionsList legend">
                    <li>
                        <span class="spriteLegenda"></span>tools
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>view additional information
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>close circle
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>focus on circle
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>open resource URI
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>expand all visible relations
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>direct relation
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>group of direct relations
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>inverse relation
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>group of inverse relations
                    </li>
                    <li>
                        <span class="spriteLegenda"></span>owl:sameAs relation
                    </li>
                </ul>
            </div>
        </div>
        -->
      </div>
</%def>
