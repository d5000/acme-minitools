## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  </style>
  <script>
  /**
   * Author: Mark Wallace
   *
   * This function asynchronously issues a SPARQL query to a
   * SPARQL endpoint, and invokes the callback function with the JSON 
   * Format [1] results.
   *
   * Refs:
   * [1] http://www.w3.org/TR/sparql11-results-json/
   */
  function sparqlQueryJson(queryStr, endpoint, callback, isDebug) {
    var querypart = "query=" + escape(queryStr);
  
    // Get our HTTP request object.
    var xmlhttp = null;
    if(window.XMLHttpRequest) {
      xmlhttp = new XMLHttpRequest();
   } else if(window.ActiveXObject) {
     // Code for older versions of IE, like IE6 and before.
     xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
   } else {
     alert('Perhaps your browser does not support XMLHttpRequests?');
   }
  
   // Set up a POST with JSON result format.
   xmlhttp.open('POST', endpoint, true); // GET can have caching probs, so POST
   xmlhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
   xmlhttp.setRequestHeader("Accept", "application/sparql-results+json");
  
   // Set up callback to get the response asynchronously.
   xmlhttp.onreadystatechange = function() {
     if(xmlhttp.readyState == 4) {
       if(xmlhttp.status == 200) {
         // Do something with the results
         // if(isDebug) alert(xmlhttp.responseText);
         callback(xmlhttp.responseText);
       } else {
         // Some kind of error occurred.
         alert("Sparql query error: " + xmlhttp.status + " "
             + xmlhttp.responseText);
       }
     }
   };
   // Send the query to the endpoint.
   xmlhttp.send(querypart);
  
   // Done; now just wait for the callback to be called.
  };
  </script>
  <script>
    var results = ''
    var endpoint = '${endpoint}/${dataset}/sparql';
    var query = 'PREFIX ccy: <http://purl.org/net/bel-epa/ccy#> \
SELECT ?flags \
WHERE { \
  ?block ccy:height ?height . \
  ?block ccy:flags ?flags \
} ORDER BY DESC(?height) LIMIT 120' ;

    // Define a callback function to receive the SPARQL JSON result.
    function myCallback(str) {
      document.getElementById("content").innerHTML = str;
      // Convert result to JSON
      var jsonObj = eval('(' + str + ')');

      // Build up a table of results.
      var cld = {'proof-of-work': 'green', 'proof-of-stake': 'blue', 'proof-of-burn': 'red'};
      var result = ' <div class="ui inverted segment">' ;
      for(var i = 0; i<  jsonObj.results.bindings.length; i++) {
        result += '<i class="' + cld[jsonObj.results.bindings[i].flags.value] + ' circle icon" style="margin:0;padding:0;"></i>';
      } 
      result += '</div>' ;
      document.getElementById("results").innerHTML = result;
   }
   // Make the query.
   sparqlQueryJson(query, endpoint, myCallback, true);
  </script>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui header">Proof-of-work / proof-of-stake / proof-of-burn frequencies, last 120 blocks (3 hrs)</divs>
      <div id="results">
        <img src="/img/loading.gif" title="Loading ..." />
      </div>
      <div class="ui inverted accordion">
        <div class="title"><i class="dropdown icon"></i>Unprocessed SPARQL response</div>
        <div class="content">
          
        </div>
      </div>
    </div>

</%def>
