## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .ui.feed>.event>.content .date,
  .ui.feed>.event>.content .summary,
  .ui.feed>.event>.content .extra.text {color: #ccc;}
  </style>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui header">Test Area</div>
      <div class="ui inverted segment">

        <div class="ui feed">
          <div class="event">
            <div class="label">
              <img src="/img/logo.png">
            </div>
            <div class="content">
              <div class="date">
                when
              </div>
              <div class="summary">
                 <a>actor</a> action 
              </div>
              <div class="extra text">
                extra text
              </div>
            </div>
          </div>
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

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Article",
  "name": "What a Crazy Day I Had",
  "content": "<div>... you will never believe ...</div>",
  "attributedTo": "http://sally.example.org"
}

attachment
attributedTo
audience
content
name
endTime
generator
icon 1:1 image
image
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Image",
  "name": "Cat Jumping on Wagon",
  "url": [
    {
      "type": "Link",
      "href": "http://example.org/image.jpeg",
      "mediaType": "image/jpeg"
    },
    {
      "type": "Link",
      "href": "http://example.org/image.png",
      "mediaType": "image/png"
    }
  ]
}
inReplyTo
location
preview
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Video",
  "name": "Cool New Movie",
  "duration": "PT2H30M",
  "preview": {
    "type": "Video",
    "name": "Trailer",
    "duration": "PT1M",
    "url": {
      "href": "http://example.org/trailer.mkv",
      "mediaType": "video/mkv"
    }
  }
}
published xsd:dateTime
replies
startTime
summary
tag
updated
url
to
bto
cc
bcc
"mediaType": "text/markdown" # defaulting to text/html
duration

=================================================

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "GJ's blog posts",
  "type": "Collection",
  "totalItems": 3,
  "current": {
    "type": "Link",
    "summary": "Most Recent Items",
    "href": "http://example.org/collection"
  },
  "items": [
    "http://example.org/posts/1",
    "http://example.org/posts/2",
    "http://example.org/posts/3"
  ]
}


{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "Page 1 of Sally's blog posts",
  "type": "CollectionPage",
  "prev": {
    "type": "Link",
    "name": "Previous Page",
    "href": "http://example.org/collection?page=1"
  },
  "items": [
    "http://example.org/posts/1",
    "http://example.org/posts/2",
    "http://example.org/posts/3"
  ]
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "Page 2 of Sally's blog posts",
  "type": "CollectionPage",
  "next": {
    "type": "Link",
    "name": "Next Page",
    "href": "http://example.org/collection?page=2"
  },
  "items": [
    "http://example.org/posts/1",
    "http://example.org/posts/2",
    "http://example.org/posts/3"
  ]
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "A simple note",
  "type": "Note",
  "content": "A simple note",
  "icon": [
    {
      "type": "Image",
      "summary": "Note (16x16)",
      "url": "http://example.org/note1.png",
      "width": 16,
      "height": 16
    },
    {
      "type": "Image",
      "summary": "Note (32x32)",
      "url": "http://example.org/note2.png",
      "width": 32,
      "height": 32
    }
  ]
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Document",
  "name": "4Q Sales Forecast",
  "url": [
    {
      "type": "Link",
      "href": "http://example.org/4q-sales-forecast.pdf",
      "mediaType": "application/pdf"
    },
    {
      "type": "Link",
      "href": "http://example.org/4q-sales-forecast.html",
      "mediaType": "text/html"
    }
  ]
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Person",
  "id": "http://purl.org/net/bel-epa/ccy#Sj9oBMXyJgxM7GZ5CpUtf3mixFEhk4ern9",
  "name": "Graham Higgins"
  "url": "https://bel-epa.com/~gjh/foaf#me",
  "summary": "VGk8kUebNK62fJi7f3Z2mcUG575tDvzNf1PPHWWbE2QvcFgaToQs",
}


{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Image",
  "summary": "Picture of Ngaio",
  "url": "https://bel-epa.com/~/ncm/image.jpg",
  "tag": [
    {
      "type": "Person",
      "id": "https://bel-epa.com/~ncm",
      "name": "Ngaio"
    }
  ]
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "Ngaio's profile",
  "type": "Profile",
  "describes": {
    "type": "Person",
    "name": "Ngaio"
  },
  "url": "https://bel-epa.com/~ncm"
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "Ngaio is an acquaintance of Graham",
  "type": "Relationship",
  "subject": {
    "type": "Person",
    "name": "Ngaio"
  },
  "relationship": "http://purl.org/vocab/relationship/acquaintanceOf",
  "object": {
    "type": "Person",
    "name": "Graham"
  }
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Profile",
  "summary": "Ngaio's Profile",
  "describes": {
    "type": "Person",
    "name": "Ngaio Macfarlane"
  }
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Article",
  "name": "What a Crazy Day I Had",
  "mediaType": "text/markdown",
  "content": "<div>... you will never believe ...</div>",
  "icon": [
    {
      "type": "Image",
      "summary": "Note (16x16)",
      "url": "http://example.org/note1.png",
      "width": 16,
      "height": 16
    },
    {
      "type": "Image",
      "summary": "Note (32x32)",
      "url": "http://example.org/note2.png",
      "width": 32,
      "height": 32
    }
  ]
  "image": [
    {
      "type": "Image",
      "name": "Cat 1",
      "url": "http://example.org/cat1.png"
    }
  ],
  "attributedTo": "http://sally.example.org"
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Organization",
  "name": "Example Co."
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Group",
  "name": "Big Beards of Austin"
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "Page 2 of Sally's blog posts",
  "type": "CollectionPage",
  "next": {
    "type": "Link",
    "name": "Next Page",
    "href": "http://example.org/collection?page=2"
  },
  "items": [
    "http://example.org/posts/1",
    "http://example.org/posts/2",
    "http://example.org/posts/3"
  ]
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Image",
  "summary": "Picture of Sally",
  "url": "http://example.org/sally.jpg",
  "tag": [
    {
      "type": "Person",
      "id": "http://sally.example.org",
      "name": "Sally"
    }
  ]
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "summary": "A simple note",
  "type": "Note",
  "mediaType": "text/markdown",
  "content": "## A simple note\nA simple markdown `note`"
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Link",
  "href": "http://example.org/image.png",
  "height": 100,
  "width": 100
}

{
  "@context": "https://www.w3.org/ns/activitystreams",
  "type": "Link",
  "href": "http://example.org/abc",
  "mediaType": "text/html",
  "name": "Previous"
}
