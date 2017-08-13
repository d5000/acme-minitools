/*
function updateResults(dict) {
	$("result").innerHTML = dict["result"];
	document.forms[0].reset();
}

function sparql(form) {
	qs = formData2QueryString(form);
	document.getElementById('result').innerHTML = "<p>Retrieving and processing ...</p>";
	var deferred = loadJSONDoc('/resources/sparql/?' + qs);
	deferred.addCallback(updateResults);
}


function popup(x) {
    x.style['opacity'] = 0.90;
    x.style['stroke-width'] = 1.6;
}

function popdown(x) {
    x.style['opacity'] = 0.45;
    x.style['stroke-width'] = 0.35;
}

function rollover(x) {
    x.style['fill-opacity'] = 0.90;
}

function rollout(x) {
    x.style['fill-opacity'] = 0.45;
}

function respond(x) {
    document.location.href="/ukparl/constituency/"+x.id;
}
*/

// namespace
window.semantic = {
  handler: {}
};

// Allow for console.log to not break IE
if (typeof window.console == "undefined" || typeof window.console.log == "undefined") {
  window.console = {
    log  : function() {},
    info : function(){},
    warn : function(){}
  };
}
if(typeof window.console.group == 'undefined' || typeof window.console.groupEnd == 'undefined' || typeof window.console.groupCollapsed == 'undefined') {
  window.console.group = function(){};
  window.console.groupEnd = function(){};
  window.console.groupCollapsed = function(){};
}
if(typeof window.console.markTimeline == 'undefined') {
  window.console.markTimeline = function(){};
}
window.console.clear = function(){};

// ready event
semantic.ready = function() {
/*
  var
    handler = {};

    $ui               = $('.ui').not('.hover, .down'),
    $menu             = $('#menu'),
    $hideMenu         = $('#menu .hide.item'),
    $menuPopup        = $('.ui.main.menu .popup.item'),
    $menuDropdown     = $('.ui.main.menu .dropdown'),
    $pageTabMenu      = $('body > .tab.segment .tabular.menu'),
    $pageTabs         = $('body > .tab.segment .menu .item'),
    $helpPopup        = $('.header .help.icon'),
    $sidebarButton    = $('.attached.launch.button');




  handler = {
    menu: {
      mouseenter: function() {
        $(this)
          .stop()
          .animate({
            width: '155px'
          }, 300, function() {
            $(this).find('.text').show();
          })
        ;
      },
      mouseleave: function(event) {
        $(this).find('.text').hide();
        $(this)
          .stop()
          .animate({
            width: '70px'
          }, 300);
      }
    }
  };

  $('.ui.dropdown')
    .dropdown({
      on: 'hover'
    })
  ;

  $menuDropdown
    .dropdown({
      on         : 'hover',
      action     : 'nothing'
    })
  ;

  $sidebarButton
    .on('mouseenter', handler.menu.mouseenter)
    .on('mouseleave', handler.menu.mouseleave)
  ;
  $menu
    .sidebar('attach events', '.launch.button, .launch.item')
    .sidebar('attach events', $hideMenu, 'hide')
  ;

  $menu
    .sidebar({
      transition       : 'uncover',
      mobileTransition : 'uncover'
    })
  ;
  $('.launch.button, .view-ui, .launch.item')
    .on('click', function(event) {
      $menu.sidebar('toggle');
      event.preventDefault();
    })
  ;

  $('.panels.menu .item')
    .tab()
  ;
*/
};

semantic.home = {};

// ready event
semantic.home.ready = function() {

  var
    $header        = $('#hero'),
    $ui            = $header.find('h1 b'),

    handler
  ;

  handler = {
    endAnimation: function() {
      $header
        .addClass('stopped')
      ;
    },
  };

  $('.logo.shape')
    .shape({
      duration: 400
    })
  ;

  if($(window).width() > 600) {
    $('body')
      .visibility({
        offset: -1,
        once: false,
        continuous: false,
        onTopPassed: function() {
          requestAnimationFrame(function() {
            $('.following .additional.item')
              .transition('scale in', 750)
            ;
          });
        }
      })
    ;
  }

  $('.email.stripe form')
    .form({
      email: {
        identifier : 'email',
        rules: [
          {
            type   : 'empty',
            prompt : 'Please enter an e-mail'
          },
          {
            type   : 'email',
            prompt : 'Please enter a valid e-mail address'
          }
        ]
      }
    })
  ;

  // demos
  $('.checkbox')
    .checkbox()
  ;
  $('.accordion')
    .accordion()
  ;
  $('.dimmer')
    .dimmer({
      on: 'hover'
    })
  ;
  $('.ui.dropdown')
    .dropdown()
  ;

  $('.ui.sidebar')
    .sidebar('setting', 'transition', 'overlay')
  ;

};

/*
// attach ready event
$(document)
  .ready(semantic.home.ready)
;
*/

function addLoadEvent(func) {
    var oldonload = window.onload;
    if (typeof window.onload != 'function') {
        window.onload = func;
    } else {
        window.onload = function() {
            oldonload();
            func();
        }
    }
}

function addResizeEvent(func) {
    var oldonresize = window.onresize;
    if (typeof window.onresize != 'function') {
        window.onresize = func;
    } else {
        window.onresize = function() {
            oldonresize();
            func();
        }
    }
}

/* To re-plot when tab is re-selected
$('a[href="#anchor"]').on('shown', function(e) {
            if (plotX._drawCount === 0) {
                plotX.replot();
            }
});
*/

/**
 * Create an <svg> element and draw a pie chart into it.
 * Arguments:
 *   data: an array of numbers to chart, one for each wedge of the pie.
 *   width,height: the size of the SVG graphic, in pixels
 *   cx, cy, r: the center and radius of the pie
 *   colors: an array of HTML color strings, one for each wedge
 *   labels: an array of labels to appear in the legend, one for each wedge
 *   lx, ly: the upper-left corner of the chart legend
 * Returns: 
 *    An <svg> element that holds the pie chart.
 *    The caller must insert the returned element into the document.
 */
function pieChart(data, width, height, cx, cy, r, colors, labels, lx, ly) {
    // This is the XML namespace for svg elements
    var svgns = "http://www.w3.org/2000/svg";    // Create the <svg> element, and specify pixel size and user coordinates
    var chart = document.createElementNS(svgns, "svg:svg");
    chart.setAttribute("width", width);
    chart.setAttribute("height", height);
    chart.setAttribute("viewBox", "0 0 " + width + " " + height);

    // Add up the data values so we know how big the pie is
    var total = 0;
    for(var i = 0; i < data.length; i++) total += data[i];
    
    // Now figure out how big each slice of pie is. Angles in radians.
    var angles = []
    for(var i = 0; i < data.length; i++) angles[i] = data[i]/total*Math.PI*2;

    // Loop through each slice of pie.
    startangle = 0;
    for(var i = 0; i < data.length; i++) {
        // This is where the wedge ends
        var endangle = startangle + angles[i];

        // Compute the two points where our wedge intersects the circle
        // These formulas are chosen so that an angle of 0 is at 12 o'clock
        // and positive angles increase clockwise.
        var x1 = cx + r * Math.sin(startangle);
        var y1 = cy - r * Math.cos(startangle);
        var x2 = cx + r * Math.sin(endangle);
        var y2 = cy - r * Math.cos(endangle);
        
        // This is a flag for angles larger than than a half circle
        // It is required by the SVG arc drawing component
        var big = 0;
        if (endangle - startangle > Math.PI) big = 1;
        
        // We describe a wedge with an <svg:path> element
        // Notice that we create this with createElementNS()
        var path = document.createElementNS(svgns, "path");
        
        // This string holds the path details
        var d = "M " + cx + "," + cy +  // Start at circle center
            " L " + x1 + "," + y1 +     // Draw line to (x1,y1)
            " A " + r + "," + r +       // Draw an arc of radius r
            " 0 " + big + " 1 " +       // Arc details...
            x2 + "," + y2 +             // Arc goes to to (x2,y2)
            " Z";                       // Close path back to (cx,cy)

        // Now set attributes on the <svg:path> element
        path.setAttribute("d", d);              // Set this path 
        path.setAttribute("fill", colors[i]);   // Set wedge color
        path.setAttribute("stroke", "black");   // Outline wedge in black
        path.setAttribute("stroke-width", "2"); // 2 units thick
        chart.appendChild(path);                // Add wedge to chart

        // The next wedge begins where this one ends
        startangle = endangle;
    }

    return chart;
}

// attach ready event
$(document)
  .ready(semantic.ready)
;

// addLoadEvent(startbox);
