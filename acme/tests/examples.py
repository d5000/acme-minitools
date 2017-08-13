examples = { 
    "example1": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Object",
        "id": "http://www.test.example/object/1",
        "name": "A Simple, non-specific object"
    }""",

    "example2": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Link",
        "href": "http://example.org/abc",
        "hreflang": "en",
        "mediaType": "text/html",
        "name": "An example link"
    }""",

    "example3": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Activity",
        "summary": "Ngaio did something to a note",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Note",
            "name": "A Note"
        }
    }""",

    "example4": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Travel",
        "summary": "Ngaio went to work",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "target": {
            "type": "Place",
            "name": "Work"
        }
    }""",

    "example5": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's notes",
        "type": "Collection",
        "totalItems": 2,
        "items": [
            {
                "type": "Note",
                "name": "A Simple Note"
            },
            {
                "type": "Note",
                "name": "Another Simple Note"
            }
        ]
    }""",

    "example6": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's notes",
        "type": "OrderedCollection",
        "totalItems": 2,
        "orderedItems": [
            {
                "type": "Note",
                "name": "A Simple Note"
            },
            {
                "type": "Note",
                "name": "Another Simple Note"
            }
        ]
    }""",

    "example7": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Page 1 of Ngaio's notes",
        "type": "CollectionPage",
        "id": "http://example.org/foo?page=1",
        "partOf": "http://example.org/foo",
        "items": [
            {
                "type": "Note",
                "name": "A Simple Note"
            },
            {
                "type": "Note",
                "name": "Another Simple Note"
            }
        ]
    }""",

    "example8": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Page 1 of Ngaio's notes",
        "type": "OrderedCollectionPage",
        "id": "http://example.org/foo?page=1",
        "partOf": "http://example.org/foo",
        "orderedItems": [
            {
                "type": "Note",
                "name": "A Simple Note"
            },
            {
                "type": "Note",
                "name": "Another Simple Note"
            }
        ]
    }""",

    "example9": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio accepted an invitation to a party",
        "type": "Accept",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Invite",
            "actor": "https://bel-epa.com/~gjh",
            "object": {
                "type": "Event",
                "name": "Going-Away Party for Jim"
            }
        }
    }""",

    "example10": """{
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": "Ngaio accepted Joe into the club",
            "type": "Accept",
            "actor": {
                "type": "Person",
                "name": "Ngaio"
            },
            "object": {
                "type": "Person",
                "name": "Joe"
            },
            "target": {
                "type": "Group",
                "name": "The Club"
            }
        }""",

    "example11": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio tentatively accepted an invitation to a party",
        "type": "TentativeAccept",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Invite",
            "actor": "https://bel-epa.com/~gjh",
            "object": {
                "type": "Event",
                "name": "Going-Away Party for Jim"
            }
        }
    }""",

    "example12": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio added an object",
        "type": "Add",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/abc"
    }""",

    "example13": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio added a picture of her rabbit to her rabbit picture collection",
        "type": "Add",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Image",
            "name": "A picture of my rabbit",
            "url": "http://example.org/img/rabbit.png"
        },
        "origin": {
            "type": "Collection",
            "name": "Camera Roll"
        },
        "target": {
            "type": "Collection",
            "name": "My Rabbit Pictures"
        }
    }""",

    "example14": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio arrived at work",
        "type": "Arrive",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "location": {
            "type": "Place",
            "name": "Work"
        },
        "origin": {
            "type": "Place",
            "name": "Home"
        }
    }""",

    "example15": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio created a note",
        "type": "Create",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Note",
            "name": "A Simple Note",
            "content": "This is a simple note"
        }
    }""",

    "example16": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio deleted a note",
        "type": "Delete",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/notes/1",
        "origin": {
            "type": "Collection",
            "name": "Ngaio's Notes"
        }
    }""",

    "example17": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio followed Graham",
        "type": "Follow",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Person",
            "name": "Graham"
        }
    }""",

    "example18": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio ignored a note",
        "type": "Ignore",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/notes/1"
    }""",

    "example19": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio joined a group",
        "type": "Join",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Group",
            "name": "A Simple Group"
        }
    }""",

    "example20": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio left work",
        "type": "Leave",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Place",
            "name": "Work"
        }
    }""",

    "example21": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio left a group",
        "type": "Leave",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Group",
            "name": "A Simple Group"
        }
    }""",

    "example22": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio liked a note",
        "type": "Like",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/notes/1"
    }""",

    "example23": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered 50% off to Lewis",
        "type": "Offer",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "http://www.types.example/ProductOffer",
            "name": "50% Off!"
        },
        "target": {
            "type": "Person",
            "name": "Lewis"
        }
    }""",

    "example24": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio invited Graham and Lisa to a party",
        "type": "Invite",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Event",
            "name": "A Party"
        },
        "target": [
            {
                "type": "Person",
                "name": "Graham"
            },
            {
                "type": "Person",
                "name": "Lisa"
            }
        ]
    }""",

    "example25": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio rejected an invitation to a party",
        "type": "Reject",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Invite",
            "actor": "https://bel-epa.com/~gjh",
            "object": {
                "type": "Event",
                "name": "Going-Away Party for Jim"
            }
        }
    }""",

    "example26": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio tentatively rejected an invitation to a party",
        "type": "TentativeReject",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Invite",
            "actor": "https://bel-epa.com/~gjh",
            "object": {
                "type": "Event",
                "name": "Going-Away Party for Jim"
            }
        }
    }""",

    "example27": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio removed a note from her notes folder",
        "type": "Remove",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/notes/1",
        "target": {
            "type": "Collection",
            "name": "Notes Folder"
        }
    }""",

    "example28": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "The moderator removed Ngaio from a group",
        "type": "Remove",
        "actor": {
            "type": "http://example.org/Role",
            "name": "The Moderator"
        },
        "object": {
            "type": "Person",
            "name": "Ngaio"
        },
        "origin": {
            "type": "Group",
            "name": "A Simple Group"
        }
    }""",

    "example29": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio retracted her offer to Graham",
        "type": "Undo",
        "actor": "https://bel-epa.com/~ncm",
        "object": {
            "type": "Offer",
            "actor": "https://bel-epa.com/~ncm",
            "object": "http://example.org/posts/1",
            "target": "https://bel-epa.com/~gjh"
        }
    }""",

    "example30": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio updated her note",
        "type": "Update",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/notes/1"
    }""",

    "example31": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio read an article",
        "type": "View",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": {
            "type": "Article",
            "name": "What You Should Know About Activity Streams"
        }
    }""",

    "example32": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio listened to a piece of music",
        "type": "Listen",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/music.mp3"
    }""",

    "example33": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio read a blog post",
        "type": "Read",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/posts/1"
    }""",

    "example34": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio moved a post from List A to List B",
        "type": "Move",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/posts/1",
        "target": {
            "type": "Collection",
            "name": "List B"
        },
        "origin": {
            "type": "Collection",
            "name": "List A"
        }
    }""",

    "example35": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio went home from work",
        "type": "Travel",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "target": {
            "type": "Place",
            "name": "Home"
        },
        "origin": {
            "type": "Place",
            "name": "Work"
        }
    }""",

    "example36": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio announced that she had arrived at work",
        "type": "Announce",
        "actor": {
            "type": "Person",
            "id": "https://bel-epa.com/~ncm",
            "name": "Ngaio"
        },
        "object": {
            "type": "Arrive",
            "actor": "https://bel-epa.com/~ncm",
            "location": {
                "type": "Place",
                "name": "Work"
            }
        }
    }""",

    "example37": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio blocked Joe",
        "type": "Block",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://joe.example.org"
    }""",

    "example38": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio flagged an inappropriate note",
        "type": "Flag",
        "actor": "https://bel-epa.com/~ncm",
        "object": {
            "type": "Note",
            "content": "An inappropriate note"
        }
    }""",

    "example39": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio disliked a post",
        "type": "Dislike",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1"
    }""",

    "example40": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Question",
        "name": "What is the answer?",
        "oneOf": [
            {
                "type": "Note",
                "name": "Option A"
            },
            {
                "type": "Note",
                "name": "Option B"
            }
        ]
    }""",

    "example41": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Question",
        "name": "What is the answer?",
        "closed": "2016-05-10T00:00:00Z"
    }""",

    "example42": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Application",
        "name": "Exampletron 3000"
    }""",

    "example43": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Group",
        "name": "Big Beards of Austin"
    }""",

    "example44": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Organization",
        "name": "Example Co."
    }""",

    "example45": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Person",
        "name": "Ngaio Smith"
    }""",

    "example46": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Service",
        "name": "Acme Web Service"
    }""",

    "example47": """{
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
    }""",

    "example48": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Article",
        "name": "What a Crazy Day I Had",
        "content": "<div>... you will never believe ...</div>",
        "attributedTo": "https://bel-epa.com/~ncm"
    }""",

    "example49": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Document",
        "name": "4Q Sales Forecast",
        "url": "http://example.org/4q-sales-forecast.pdf"
    }""",

    "example50": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Audio",
        "name": "Interview With A Famous Technologist",
        "url": {
            "type": "Link",
            "href": "http://example.org/podcast.mp3",
            "mediaType": "audio/mp3"
        }
    }""",

    "example51": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Image",
        "name": "Rabbit Jumping on Wagon",
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
    }""",

    "example52": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Video",
        "name": "Puppy Plays With Ball",
        "url": "http://example.org/video.mkv",
        "duration": "PT2H"
    }""",

    "example53": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Note",
        "name": "A Word of Warning",
        "content": "Looks like it is going to rain today. Bring an umbrella!"
    }""",

    "example54": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Page",
        "name": "Omaha Weather Report",
        "url": "http://example.org/weather-in-omaha.html"
    }""",

    "example55": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Event",
        "name": "Going-Away Party for Jim",
        "startTime": "2014-12-31T23:00:00-08:00",
        "endTime": "2015-01-01T06:00:00-08:00"
    }""",

    "example56": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "Work"
    }""",

    "example57": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "Fresno Area",
        "latitude": 36.75,
        "longitude": 119.7667,
        "radius": 15,
        "units": "miles"
    }""",

    "example58": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Mention of Joe by Carrie in her note",
        "type": "Mention",
        "href": "http://example.org/joe",
        "name": "Joe"
    }""",

    "example59": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Profile",
        "summary": "Ngaio's Profile",
        "describes": {
            "type": "Person",
            "name": "Ngaio Smith"
        }
    }""",

    "example60": """{
        "type": "OrderedCollection",
        "totalItems": 3,
        "name": "Vacation photos 2016",
        "orderedItems": [
            {
                "type": "Image",
                "id": "http://image.example/1"
            },
            {
                "type": "Tombstone",
                "formerType": "Image",
                "id": "http://image.example/2",
                "deleted": "2016-03-17T00:00:00Z"
            },
            {
                "type": "Image",
                "id": "http://image.example/3"
            }
        ]
    }""",

    "example61": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "Foo",
        "id": "http://example.org/foo"
    }""",

    "example62": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A foo",
        "type": "http://example.org/Foo"
    }""",

    "example63": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered the Foo object",
        "type": "Offer",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/foo"
    }""",

    "example64": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered the Foo object",
        "type": "Offer",
        "actor": {
            "type": "Person",
            "id": "https://bel-epa.com/~ncm",
            "summary": "Ngaio"
        },
        "object": "http://example.org/foo"
    }""",

    "example65": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio and Joe offered the Foo object",
        "type": "Offer",
        "actor": [
            "http://joe.example.org",
            {
                "type": "Person",
                "id": "https://bel-epa.com/~ncm",
                "name": "Ngaio"
            }
        ],
        "object": "http://example.org/foo"
    }""",

    "example66": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Note",
        "name": "Have you seen my rabbit?",
        "attachment": [
            {
                "type": "Image",
                "content": "This is what he looks like.",
                "url": "http://example.org/rabbit.jpeg"
            }
        ]
    }""",

    "example67": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Image",
        "name": "My rabbit taking a nap",
        "url": "http://example.org/rabbit.jpeg",
        "attributedTo": [
            {
                "type": "Person",
                "name": "Ngaio"
            }
        ]
    }""",

    "example68": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Image",
        "name": "My rabbit taking a nap",
        "url": "http://example.org/rabbit.jpeg",
        "attributedTo": [
            "http://joe.example.org",
            {
                "type": "Person",
                "name": "Ngaio"
            }
        ]
    }""",

    "example69": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "Holiday announcement",
        "type": "Note",
        "content": "Thursday will be a company-wide holiday. Enjoy your day off!",
        "audience": {
            "type": "http://example.org/Organization",
            "name": "ExampleCo LLC"
        }
    }""",

    "example70": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered a post to Graham",
        "type": "Offer",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1",
        "target": "https://bel-epa.com/~gjh",
        "bcc": [ "http://joe.example.org" ]
    }""",

    "example71": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered a post to Graham",
        "type": "Offer",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1",
        "target": "https://bel-epa.com/~gjh",
        "bto": [ "http://joe.example.org" ]
    }""",

    "example72": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered a post to Graham",
        "type": "Offer",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1",
        "target": "https://bel-epa.com/~gjh",
        "cc": [ "http://joe.example.org" ]
    }""",

    "example73": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Activities in context 1",
        "type": "Collection",
        "items": [
            {
                "type": "Offer",
                "actor": "https://bel-epa.com/~ncm",
                "object": "http://example.org/posts/1",
                "target": "https://bel-epa.com/~gjh",
                "context": "http://example.org/contexts/1"
            },
            {
                "type": "Like",
                "actor": "http://joe.example.org",
                "object": "http://example.org/posts/2",
                "context": "http://example.org/contexts/1"
            }
        ]
    }""",

    "example74": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's blog posts",
        "type": "Collection",
        "totalItems": 3,
        "current": "http://example.org/collection",
        "items": [
            "http://example.org/posts/1",
            "http://example.org/posts/2",
            "http://example.org/posts/3"
        ]
    }""",

    "example75": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's blog posts",
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
    }""",

    "example76": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's blog posts",
        "type": "Collection",
        "totalItems": 3,
        "first": "http://example.org/collection?page=0"
    }""",

    "example77": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's blog posts",
        "type": "Collection",
        "totalItems": 3,
        "first": {
            "type": "Link",
            "summary": "First Page",
            "href": "http://example.org/collection?page=0"
        }
    }""",

    "example78": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "content": "This is all there is.",
        "generator": {
            "type": "Application",
            "name": "Exampletron 3000"
        }
    }""",

    "example79": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "content": "This is all there is.",
        "icon": {
            "type": "Image",
            "name": "Note icon",
            "url": "http://example.org/note.png",
            "width": 16,
            "height": 16
        }
    }""",

    "example80": """{
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
    }""",

    "example81": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "A simple note",
        "type": "Note",
        "content": "This is all there is.",
        "image": {
            "type": "Image",
            "name": "A Rabbit",
            "url": "http://example.org/rabbit.png"
        }
    }""",

    "example82": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "A simple note",
        "type": "Note",
        "content": "This is all there is.",
        "image": [
            {
                "type": "Image",
                "name": "Rabbit 1",
                "url": "http://example.org/rabbit1.png"
            },
            {
                "type": "Image",
                "name": "Rabbit 2",
                "url": "http://example.org/rabbit2.png"
            }
        ]
    }""",

    "example83": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "content": "This is all there is.",
        "inReplyTo": {
            "summary": "Previous note",
            "type": "Note",
            "content": "What else is there?"
        }
    }""",

    "example84": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "content": "This is all there is.",
        "inReplyTo": "http://example.org/posts/1"
    }""",

    "example85": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio listened to a piece of music on the Acme Music Service",
        "type": "Listen",
        "actor": {
            "type": "Person",
            "name": "Ngaio"
        },
        "object": "http://example.org/foo.mp3",
        "instrument": {
            "type": "Service",
            "name": "Acme Music Service"
        }
    }""",

    "example86": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A collection",
        "type": "Collection",
        "totalItems": 3,
        "last": "http://example.org/collection?page=1"
    }""",

    "example87": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A collection",
        "type": "Collection",
        "totalItems": 5,
        "last": {
            "type": "Link",
            "summary": "Last Page",
            "href": "http://example.org/collection?page=1"
        }
    }""",

    "example88": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Person",
        "name": "Ngaio",
        "location": {
            "name": "Over the Arabian Sea, east of Socotra Island Nature Sanctuary",
            "type": "Place",
            "longitude": 12.34,
            "latitude": 56.78,
            "altitude": 90,
            "units": "m"
        }
    }""",

    "example89": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's notes",
        "type": "Collection",
        "totalItems": 2,
        "items": [
            {
                "type": "Note",
                "name": "Reminder for Going-Away Party"
            },
            {
                "type": "Note",
                "name": "Meeting 2016-11-17"
            }
        ]
    }""",

    "example90": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's notes",
        "type": "OrderedCollection",
        "totalItems": 2,
        "orderedItems": [
            {
                "type": "Note",
                "name": "Meeting 2016-11-17"
            },
            {
                "type": "Note",
                "name": "Reminder for Going-Away Party"
            }
        ]
    }""",

    "example91": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Question",
        "name": "What is the answer?",
        "oneOf": [
            {
                "type": "Note",
                "name": "Option A"
            },
            {
                "type": "Note",
                "name": "Option B"
            }
        ]
    }""",

    "example92": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Question",
        "name": "What is the answer?",
        "anyOf": [
            {
                "type": "Note",
                "name": "Option A"
            },
            {
                "type": "Note",
                "name": "Option B"
            }
        ]
    }""",

    "example93": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Question",
        "name": "What is the answer?",
        "closed": "2016-05-10T00:00:00Z"
    }""",

    "example94": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio moved a post from List A to List B",
        "type": "Move",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1",
        "target": {
            "type": "Collection",
            "name": "List B"
        },
        "origin": {
            "type": "Collection",
            "name": "List A"
        }
    }""",

    "example95": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Page 2 of Ngaio's blog posts",
        "type": "CollectionPage",
        "next": "http://example.org/collection?page=2",
        "items": [
            "http://example.org/posts/1",
            "http://example.org/posts/2",
            "http://example.org/posts/3"
        ]
    }""",

    "example96": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Page 2 of Ngaio's blog posts",
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
    }""",

    "example97": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio liked a post",
        "type": "Like",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1"
    }""",

    "example98": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Like",
        "actor": "https://bel-epa.com/~ncm",
        "object": {
            "type": "Note",
            "content": "A simple note"
        }
    }""",

    "example99": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio liked a note",
        "type": "Like",
        "actor": "https://bel-epa.com/~ncm",
        "object": [
            "http://example.org/posts/1",
            {
                "type": "Note",
                "summary": "A simple note",
                "content": "That is a tree."
            }
        ]
    }""",

    "example100": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Page 1 of Ngaio's blog posts",
        "type": "CollectionPage",
        "prev": "http://example.org/collection?page=1",
        "items": [
            "http://example.org/posts/1",
            "http://example.org/posts/2",
            "http://example.org/posts/3"
        ]
    }""",

    "example101": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Page 1 of Ngaio's blog posts",
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
    }""",

    "example102": """{
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
    }""",

    "example103": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio checked that her flight was on time",
        "type": ["Activity", "http://www.verbs.example/Check"],
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/flights/1",
        "result": {
            "type": "http://www.types.example/flightstatus",
            "name": "On Time"
        }
    }""",

    "example104": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "id": "http://www.test.example/notes/1",
        "content": "I am fine.",
        "replies": {
            "type": "Collection",
            "totalItems": 1,
            "items": [
                {
                    "summary": "A response to the note",
                    "type": "Note",
                    "content": "I am glad to hear it.",
                    "inReplyTo": "http://www.test.example/notes/1"
                }
            ]
        }
    }""",

    "example105": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Image",
        "summary": "Picture of Ngaio",
        "url": "http://example.org/ngaio.jpg",
        "tag": [
            {
                "type": "Person",
                "id": "https://bel-epa.com/~ncm",
                "name": "Ngaio"
            }
        ]
    }""",

    "example106": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered the post to Graham",
        "type": "Offer",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1",
        "target": "https://bel-epa.com/~gjh"
    }""",

    "example107": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered the post to Graham",
        "type": "Offer",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1",
        "target": {
            "type": "Person",
            "name": "Graham"
        }
    }""",

    "example108": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio offered the post to Graham",
        "type": "Offer",
        "actor": "https://bel-epa.com/~ncm",
        "object": "http://example.org/posts/1",
        "target": "https://bel-epa.com/~gjh",
        "to": [ "http://joe.example.org" ]
    }""",

    "example109": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Document",
        "name": "4Q Sales Forecast",
        "url": "http://example.org/4q-sales-forecast.pdf"
    }""",

    "example110": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Document",
        "name": "4Q Sales Forecast",
        "url": {
            "type": "Link",
            "href": "http://example.org/4q-sales-forecast.pdf"
        }
    }""",

    "example111": """{
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
    }""",

    "example112": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "Liu Gu Lu Cun, Pingdu, Qingdao, Shandong, China",
        "type": "Place",
        "latitude": 36.75,
        "longitude": 119.7667,
        "accuracy": 94.5
    }""",

    "example113": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "Fresno Area",
        "altitude": 15.0,
        "latitude": 36.75,
        "longitude": 119.7667,
        "units": "miles"
    }""",

    "example114": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "content": "A <em>simple</em> note"
    }""",

    "example115": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "contentMap": {
            "en": "A <em>simple</em> note",
            "es": "Una nota <em>sencilla</em>",
            "zh-Hans": "一段<em>简单的</em>笔记"
        }
    }""",

    "example116": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "mediaType": "text/markdown",
        "content": "## A simple note\nA simple markdown `note`"
    }""",

    "example117": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Note",
        "name": "A simple note"
    }""",

    "example118": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Note",
        "nameMap": {
            "en": "A simple note",
            "es": "Una nota sencilla",
            "zh-Hans": "一段简单的笔记"
        }
    }""",

    "example119": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Video",
        "name": "Birds Flying",
        "url": "http://example.org/video.mkv",
        "duration": "PT2H"
    }""",

    "example120": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Link",
        "href": "http://example.org/image.png",
        "height": 100,
        "width": 100
    }""",

    "example121": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Link",
        "href": "http://example.org/abc",
        "mediaType": "text/html",
        "name": "Previous"
    }""",

    "example122": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Link",
        "href": "http://example.org/abc",
        "hreflang": "en",
        "mediaType": "text/html",
        "name": "Previous"
    }""",

    "example123": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Page 1 of Ngaio's notes",
        "type": "CollectionPage",
        "id": "http://example.org/collection?page=1",
        "partOf": "http://example.org/collection",
        "items": [
            {
                "type": "Note",
                "name": "Pizza Toppings to Try"
            },
            {
                "type": "Note",
                "name": "Thought about California"
            }
        ]
    }""",

    "example124": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "Fresno Area",
        "latitude": 36.75,
        "longitude": 119.7667,
        "radius": 15,
        "units": "miles"
    }""",

    "example125": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "Fresno Area",
        "latitude": 36.75,
        "longitude": 119.7667,
        "radius": 15,
        "units": "miles"
    }""",

    "example126": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Link",
        "href": "http://example.org/abc",
        "hreflang": "en",
        "mediaType": "text/html",
        "name": "Next"
    }""",

    "example127": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Event",
        "name": "Going-Away Party for Jim",
        "startTime": "2014-12-31T23:00:00-08:00",
        "endTime": "2015-01-01T06:00:00-08:00"
    }""",

    "example128": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "A simple note",
        "type": "Note",
        "content": "Fish swim.",
        "published": "2014-12-12T12:12:12Z"
    }""",

    "example129": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Event",
        "name": "Going-Away Party for Jim",
        "startTime": "2014-12-31T23:00:00-08:00",
        "endTime": "2015-01-01T06:00:00-08:00"
    }""",

    "example130": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "Fresno Area",
        "latitude": 36.75,
        "longitude": 119.7667,
        "radius": 15,
        "units": "miles"
    }""",

    "example131": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Link",
        "href": "http://example.org/abc",
        "hreflang": "en",
        "mediaType": "text/html",
        "name": "Preview",
        "rel": ["canonical", "preview"]
    }""",

    "example132": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Page 1 of Ngaio's notes",
        "type": "OrderedCollectionPage",
        "startIndex": 0,
        "orderedItems": [
            {
                "type": "Note",
                "name": "Density of Water"
            },
            {
                "type": "Note",
                "name": "Air Mattress Idea"
            }
        ]
    }""",

    "example133": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "Cane Sugar Processing",
        "type": "Note",
        "summary": "A simple <em>note</em>"
    }""",

    "example134": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "Cane Sugar Processing",
        "type": "Note",
        "summaryMap": {
            "en": "A simple <em>note</em>",
            "es": "Una <em>nota</em> sencilla",
            "zh-Hans": "一段<em>简单的</em>笔记"
        }
    }""",

    "example135": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's notes",
        "type": "Collection",
        "totalItems": 2,
        "items": [
            {
                "type": "Note",
                "name": "Which Staircase Should I Use"
            },
            {
                "type": "Note",
                "name": "Something to Remember"
            }
        ]
    }""",

    "example136": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "Fresno Area",
        "latitude": 36.75,
        "longitude": 119.7667,
        "radius": 15,
        "units": "miles"
    }""",

    "example137": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "Cranberry Sauce Idea",
        "type": "Note",
        "content": "Mush it up so it does not have the same shape as the can.",
        "updated": "2014-12-12T12:12:12Z"
    }""",

    "example138": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Link",
        "href": "http://example.org/image.png",
        "height": 100,
        "width": 100
    }""",

    "example139": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio is an acquaintance of Graham's",
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
    }""",

    "example140": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio is an acquaintance of Graham's",
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
    }""",

    "example141": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's profile",
        "type": "Profile",
        "describes": {
            "type": "Person",
            "name": "Ngaio"
        },
        "url": "https://bel-epa.com/~ncm"
    }""",

    "example142": """{
    "@context": "https://www.w3.org/ns/activitystreams",
    "summary": "This image has been deleted",
    "type": "Tombstone",
    "formerType": "Image",
    "url": "http://example.org/image/2"
    }""",

    "example143": """{
    "@context": "https://www.w3.org/ns/activitystreams",
    "summary": "This image has been deleted",
    "type": "Tombstone",
    "deleted": "2016-05-03T00:00:00Z"
    }""",

    "example144": """{
     "@context": "https://www.w3.org/ns/activitystreams",
     "summary": "Activities in Project XYZ",
     "type": "Collection",
     "items": [
         {
             "summary": "Ngaio created a note",
             "type": "Create",
             "id": "http://activities.example.com/1",
             "actor": "https://bel-epa.com/~ncm",
             "object": {
                "summary": "A note",
                 "type": "Note",
                 "id": "http://notes.example.com/1",
                 "content": "A note"
             },
             "context": {
                 "type": "http://example.org/Project",
                 "name": "Project XYZ"
             },
             "audience": {
                 "type": "Group",
                 "name": "Project XYZ Working Group"
             },
             "to": "https://bel-epa.com/~gjh"
         },
         {
             "summary": "Graham liked Ngaio's note",
             "type": "Like",
             "id": "http://activities.example.com/1",
             "actor": "https://bel-epa.com/~gjh",
             "object": "http://notes.example.com/1",
             "context": {
                 "type": "http://example.org/Project",
                 "name": "Project XYZ"
             },
             "audience": {
                 "type": "Group",
                 "name": "Project XYZ Working Group"
             },
             "to": "https://bel-epa.com/~ncm"
         }
     ]
    }""",

    "example145": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio's friends list",
        "type": "Collection",
        "items": [
            {
                "summary": "Ngaio is influenced by Joe",
                "type": "Relationship",
                "subject": {
                    "type": "Person",
                    "name": "Ngaio"
                },
                "relationship": "http://purl.org/vocab/relationship/influencedBy",
                "object": {
                    "type": "Person",
                    "name": "Joe"
                }
            },
            {
                "summary": "Ngaio is a friend of Jane",
                "type": "Relationship",
                "subject": {
                    "type": "Person",
                    "name": "Ngaio"
                },
                "relationship": "http://purl.org/vocab/relationship/friendOf",
                "object": {
                    "type": "Person",
                    "name": "Jane"
                }
            }
        ]
    }""",

    "example146": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio became a friend of Matt",
        "type": "Create",
        "actor": "https://bel-epa.com/~ncm",
        "object": {
            "type": "Relationship",
            "subject": "https://bel-epa.com/~ncm",
            "relationship": "http://purl.org/vocab/relationship/friendOf",
            "object": "http://matt.example.org",
            "startTime": "2015-04-21T12:34:56"
        }
    }""",

    "example147": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://example.org/connection-requests/123",
        "summary": "Ngaio requested to be a friend of Graham",
        "type": "Offer",
        "actor": "acct:ncm@bel-epa.com",
        "object": {
            "summary": "Ngaio and Graham's friendship",
            "id": "http://example.org/connections/123",
            "type": "Relationship",
            "subject": "acct:ncm@bel-epa.com",
            "relationship": "http://purl.org/vocab/relationship/friendOf",
            "object": "acct:gjh@bel-epa.com"
        },
        "target": "acct:gjh@bel-epa.com"
    }""",

    "example148": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "Ngaio and Graham's relationship history",
        "type": "Collection",
        "items": [
            {
                "summary": "Graham accepted Ngaio's friend request",
                "id": "http://example.org/activities/122",
                "type": "Accept",
                "actor": "acct:gjh@bel-epa.com",
                "object": "http://example.org/connection-requests/123",
                "inReplyTo": "http://example.org/connection-requests/123",
                "context": "http://example.org/connections/123",
                "result": [
                    "http://example.org/activities/123",
                    "http://example.org/activities/124",
                    "http://example.org/activities/125",
                    "http://example.org/activities/126"
                ]
            },
            {
                "summary": "Graham followed Ngaio",
                "id": "http://example.org/activities/123",
                "type": "Follow",
                "actor": "acct:gjh@bel-epa.com",
                "object": "acct:ncm@bel-epa.com",
                "context": "http://example.org/connections/123"
            },
            {
                "summary": "Ngaio followed Graham",
                "id": "http://example.org/activities/124",
                "type": "Follow",
                "actor": "acct:ncm@bel-epa.com",
                "object": "acct:gjh@bel-epa.com",
                "context": "http://example.org/connections/123"
            },
            {
                "summary": "Graham added Ngaio to his friends list",
                "id": "http://example.org/activities/125",
                "type": "Add",
                "actor": "acct:gjh@bel-epa.com",
                "object": "http://example.org/connections/123",
                "target": {
                    "type": "Collection",
                    "summary": "Graham's Connections"
                },
                "context": "http://example.org/connections/123"
            },
            {
                "summary": "Ngaio added Graham to her friends list",
                "id": "http://example.org/activities/126",
                "type": "Add",
                "actor": "acct:ncm@bel-epa.com",
                "object": "http://example.org/connections/123",
                "target": {
                    "type": "Collection",
                    "summary": "Ngaio's Connections"
                },
                "context": "http://example.org/connections/123"
            }
        ]
    }""",

    "example149": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "San Francisco, CA"
    }""",

    "example150": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Place",
        "name": "San Francisco, CA",
        "longitude": "122.4167",
        "latitude": "37.7833"
    }""",

    "example151": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "A question about robots",
        "id": "http://help.example.org/question/1",
        "type": "Question",
        "content": "I'd like to build a robot to feed my rabbit. Should I use Arduino or Raspberry Pi?"
    }""",

    "example152": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "id": "http://polls.example.org/question/1",
        "name": "A question about robots",
        "type": "Question",
         "content": "I'd like to build a robot to feed my rabbit. Which platform is best?",
         "oneOf": [
             {"name": "arduino"},
             {"name": "raspberry pi"}
         ]
     }""",

    "example153": """{
     "@context": "https://www.w3.org/ns/activitystreams",
     "attributedTo": "https://bel-epa.com/~ncm",
     "inReplyTo": "http://polls.example.org/question/1",
     "name": "arduino"
    }""",

    "example154": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "A question about robots",
        "id": "http://polls.example.org/question/1",
        "type": "Question",
         "content": "I'd like to build a robot to feed my rabbit. Which platform is best?",
         "oneOf": [
             {"name": "arduino"},
             {"name": "raspberry pi"}
         ],
         "replies": {
             "type": "Collection",
             "totalItems": 3,
             "items": [
                 {
                     "attributedTo": "https://bel-epa.com/~ncm",
                     "inReplyTo": "http://polls.example.org/question/1",
                     "name": "arduino"
                 },
                 {
                     "attributedTo": "http://joe.example.org",
                     "inReplyTo": "http://polls.example.org/question/1",
                     "name": "arduino"
                 },
                 {
                     "attributedTo": "https://bel-epa.com/~gjh",
                     "inReplyTo": "http://polls.example.org/question/1",
                     "name": "raspberry pi"
                 }
             ]
         },
         "result": {
             "type": "Note",
             "content": "Users are favoriting &quot;arduino&quot; by a 33% margin."
         }
     }""",

    "example155": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "summary": "History of Graham's note",
        "type": "Collection",
        "items": [
            {
                "summary": "Ngaio liked Graham's note",
                "type": "Like",
                "actor": "https://bel-epa.com/~ncm",
                "id": "http://activities.example.com/1",
                "published": "2015-11-12T12:34:56Z",
                "object": {
                    "summary": "Graham's note",
                    "type": "Note",
                    "id": "http://notes.example.com/1",
                    "attributedTo": "https://bel-epa.com/~gjh",
                    "content": "My note"
                }
            },
            {
                "summary": "Ngaio disliked Graham's note",
                "type": "Dislike",
                "actor": "https://bel-epa.com/~ncm",
                "id": "http://activities.example.com/2",
                "published": "2015-12-11T21:43:56Z",
                "object": {
                    "summary": "Graham's note",
                    "type": "Note",
                    "id": "http://notes.example.com/1",
                    "attributedTo": "https://bel-epa.com/~gjh",
                    "content": "My note"
                }
            }
        ]
     }""",

    "example156": """{
     "@context": "https://www.w3.org/ns/activitystreams",
     "summary": "History of Graham's note",
     "type": "Collection",
     "items": [
         {
             "summary": "Ngaio liked Graham's note",
             "type": "Like",
             "id": "http://activities.example.com/1",
             "actor": "https://bel-epa.com/~ncm",
             "published": "2015-11-12T12:34:56Z",
             "object": {
                 "summary": "Graham's note",
                 "type": "Note",
                 "id": "http://notes.example.com/1",
                 "attributedTo": "https://bel-epa.com/~gjh",
                 "content": "My note"
             }
         },
         {
             "summary": "Ngaio no longer likes Graham's note",
             "type": "Undo",
             "id": "http://activities.example.com/2",
             "actor": "https://bel-epa.com/~ncm",
             "published": "2015-12-11T21:43:56Z",
             "object": "http://activities.example.com/1"
         }
     ]
    }""",

    "example157": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "A thank-you note",
        "type": "Note",
        "content": "Thank you <a href='https://bel-epa.com/~ncm'>@ngaio</a> for all your hard work! <a href='http://example.org/tags/givingthanks'>#givingthanks</a>",
        "to": {
            "name": "Ngaio",
            "type": "Person",
            "id": "https://bel-epa.com/~ncm"
        },
        "tag": {
            "id": "http://example.org/tags/givingthanks",
            "name": "#givingthanks"
        }
    }""",

    "example158": """{
        "@context": "https://www.w3.org/ns/activitystreams",
        "name": "A thank-you note",
        "type": "Note",
        "content": "Thank you @ngaio for all your hard work! #givingthanks",
        "tag": [
            {
                "type": "Mention",
                "href": "http://example.org/people/ngaio",
                "name": "@ngaio"
            },
            {
                "id": "http://example.org/tags/givingthanks",
                "name": "#givingthanks"
            }
        ]
    }""",

    "example159": """{
            "@context": "https://www.w3.org/ns/activitystreams",
            "summary": "Ngaio moved the sales figures from Folder A to Folder B",
            "type": "Move",
            "actor": "https://bel-epa.com/~ncm",
            "object": {
                "type": "Document",
                "name": "sales figures"
            },
            "origin": {
                "type": "Collection",
                "name": "Folder A"
            },
            "target": {
                "type": "Collection",
                "name": "Folder B"
            }
        }"""
}
