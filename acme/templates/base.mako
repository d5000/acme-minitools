# -*- coding: utf-8 -*-
<!DOCTYPE html>
<%namespace name="rubric" file="acme:templates/rubric.mako" import="*"/>
<%namespace name="nav" file="acme:templates/nav.mako" import="*"/>
<%namespace name="footer" file="acme:templates/footer.mako" import="*"/>
<html dir="ltr" lang="en-gb">
  <head>
    ${rubric.body()|n}
    ${self.header()|n}
  </head>
  <body ontouchstart="">
    <noscript>
      <div class="noscript">
      Your browser settings show that JavaScript is disabled. (Good call, we too browse with javascript disabled). If you enable it for this site, you’ll get the full benefit of the user-oriented enhancements: nice fonts, drop-down menus, active tabs and the like. We recommend that you turn on Javascript and then refresh this page. <a href="http://www.enable-javascript.com/" target="_blank">How do I turn on Javascript?</a>
      </div>
    </noscript>

    <!-- Page Contents -->
    <div class="pusher">
      <div class="ui container">
      ${nav.body()|n}

      ${next.body()|n}
      ${footer.body()|n}
      % if context.get('extra_js', UNDEFINED) is not UNDEFINED:
        ${context['extra_js']|n}
      % endif
      </div>
    </div>
  </body>
</html>
