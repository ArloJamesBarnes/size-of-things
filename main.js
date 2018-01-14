var container;
var ships;
var min_size_px = 50;
var m_per_px = 10;
var zoomSlowFactor = 100
$(function() {
  container = $('.stuff')
  $.getJSON("ships.json").done(function(data) {
    ships = data;
    initialize_ships();
  })

  // Figure out px/mm

  $(window).on('mousewheel', function(evt) {
    evt.preventDefault();
    console.log(evt.deltaY);
    m_per_px *= Math.pow(10, evt.deltaY/zoomSlowFactor);
    resize();
  })
})

function initialize_ships() {
  resize();
}

function resize() {
  $.each(ships, function(idx, ship) {
    var info = ship.info
    if(!info.Length) {
      console.log("Error: No length for " + info.Name)
      return
    }
    var px_width = info.Length/m_per_px
    if(px_width > min_size_px) {
      if(!ship.elm) {
        ship.elm = $('<img class="thing"></img>').get(0)
        ship.elm.src = ship.path + '/' + ship.filename
        container.append(ship.elm)
      }
      var ratio = px_width/ship.elm.naturalWidth
      ship.elm.width = px_width
      ship.elm.height = ship.elm.naturalHeight*ratio
    } else {
      if(ship.elm) {
        container.get(0).removeChild(ship.elm);
        ship.elm = false;
      }
    }
  })
  $('.m_per_px').text(Math.round(m_per_px));
}
