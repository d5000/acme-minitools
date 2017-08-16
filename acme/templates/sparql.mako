## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <link href="/css/qonsole/bootstrap.css" rel="stylesheet" />
  <link href="/css/qonsole/font-awesome.css" rel="stylesheet" />
  <link href="/css/qonsole/codemirror.css" rel="stylesheet" />
  <link href="/css/qonsole/jquery.dataTables.css" rel="stylesheet" />
  <link href="/css/qonsole/qonsole.css" rel="stylesheet" />
  <script type="text/javascript" src="/js/qonsole/qonsole.js"></script>
  <script type="text/javascript" src="/js/qonsole/remote-sparql-service.js"></script>
  <script type="text/javascript" src="/js/qonsole/bootstrap.js"></script>
  <script type="text/javascript" src="/js/qonsole/spin.js"></script>
  <script type="text/javascript" src="/js/qonsole/jquery.spin.js"></script>

  <style type="text/css">
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  </style>
  <script type="text/javascript">
    // configuration
    var qonfig = {
      endpoints: {
        "default": "http://purl.org/net/bel-epa/ccy#",
      },
      prefixes: {
        "ccy":       "http://purl.org/net/bel-epa/ccy#",
        "rdf":      "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs":     "http://www.w3.org/2000/01/rdf-schema#",
        "owl":      "http://www.w3.org/2002/07/owl#",
        "xsd":      "http://www.w3.org/2001/XMLSchema#"
      },
      queries: [
        { "name": "Height of blockchain",
          "query": "select ?height\nwhere {\n" +
                   "  ?block ccy:height ?height}\n" +
                   "} order by desc(?height) limit 1"
        },
        { "name": "all OWL classes",
          "query": "select ?class ?label ?description\nwhere {\n" +
                   "  ?class a owl:Class.\n" +
                   "  optional { ?class rdfs:label ?label}\n" +
                   "  optional { ?class rdfs:comment ?description}\n}"
        },
        {
          'name': 'Example with embedded comments',
          'query': '# comment 1\n@prefix foo: <http://fubar.com/foo>.\n@prefix bar: <http://fubar.com/bar>.\n#comment 2\nselect * {}'
        }
      ],
      allowQueriesFromURL: true
    };
  </script>
</%def>

<%def name="body()">
  <div class="ui container">
    <div class="ui inverted segment dark">

      <div class="container qonsole">
        <div class="col-md-12 well">
          <h2 class="">Example queries</h2>
          <span class="form-inline">
            <select class="form-control" id="examples"></select>
          </span>
        </div>

        <div class="col-md-12 well vertical">
          <h2 class="">Prefixes</h2>
          <ul class="list-inline prefixes">
            <li class="keep">
              <a data-toggle="modal" href="#prefixEditor" class="btn" title="Add a SPARQL prefix">
                <i class="fa fa-plus-circle"></i>
              </a>
            </li>
          </ul>
        </div>

        <div class="col-md-12 well">
          <div class="query-edit">
            <div id="query-edit-cm" class=""></div>
          </div>
          <div class="query-chrome">
            <form class="form-inline" role="form">
              <div class="form-group">
                <label for="endpoints">SPARQL endpoint:</label>
                  <select class="form-control" id="endpoints">
                  </select>
                </div>
              <div class="form-group">
                <input type="hidden" class="form-control" id="sparqlEndpoint" />
              </div>
              <div class="form-group">
                <label for="format">Results format:</label>
                <select class="form-control" name="format">
                  <option value="tsv">table</option>
                  <option value="text">plain text</option>
                  <option value="json">JSON</option>
                  <option value="xml">XML</option>
                </select>
              </div>
              <div class="form-group">
                <a href="#" class="btn btn-success run-query form-control">perform query</a>
              </div>

            </form>
          </div>
        </div>


      <div class="ui inverted accordion">
        <div class="title"><i class="dropdown icon"></i>Unprocessed JSON API response</div>
        <div class="content">
          ${dump|n}
        </div>
      </div>
    </div>
  </div>
  <script type="text/javascript">
    $.qonsole.init(qonfig);
  </script>
</%def>

