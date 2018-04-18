var map;
var markers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 48.9, lng: 2.3 },
        zoom: 11,
//      mapTypeId: google.maps.MapTypeId.SATELLITE
        mapTypeId: google.maps.MapTypeId.TERRAIN
    });
}

// ---------------------- 
// ---------------------- Markers

function loadMarkers() {
    deleteMarkers()
    $.getJSON( 'http://localhost/gps/data.json', function(data) {
        $.each( data, function(i, marker) {
            console.log(marker.utc + ' - ' + marker.latitude + ' - ' +  marker.longitude + ' - ' + marker.signal_quality + ' - ' + marker.signal_strength )
           
            
            if ( marker.signal_quality <= $('#signal_quality').val() || marker.signal_strength <= $('#signal_strength').val() ) {
                icon_url = 'http://maps.google.com/mapfiles/ms/micons/red.png'
            } else {
                icon_url = 'http://maps.google.com/mapfiles/ms/micons/yellow.png'
            }
            
            var contentString = '<div id="content">'+
                '<div id="siteNotice">'+
                '</div>'+
                '<h1 id="firstHeading" class="firstHeading">Signal '+ marker.signal_quality +'/'+ marker.signal_strength +'</h1>'+
                '<div id="bodyContent">'+
                '<p>'+
                'time: ' + marker.utc +'<br/>'+
                'latitude: '+ marker.latitude +'<br/>'+
                'longitude: '+ marker.longitude +'<br/>'+
                '<hr/>'+
                'speed: '+ marker.speed + 'm/s ( ' + (marker.speed * 3.6).toFixed(2) + 'km/h)<br />'+
                
                'clim: ' + marker.clim +'<br/>'+
                'altitude: ' + marker.altitude +'<br/>'+
                '<hr/>'+
                'signal_quality: ' + marker.signal_quality +'<br/>'+
                'signal_strength: ' + marker.signal_strength +'<br/>'+
                
                '</p>'+
                '</div>'+
                '</div>';
            
            var infowindow = new google.maps.InfoWindow({
                content: contentString
            });
            
            var marker = new google.maps.Marker({
                position: {lat: marker.latitude, lng: marker.longitude},
                map: map,
                icon: icon_url,
                opacity: 0.5
            })
            
            markers.push(marker);
            
            marker.addListener('click', function() {
                infowindow.open(map, marker);
            });
        });
    });
    
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

// Removes the markers from the map, but keeps them in the array.
function hideMarkers() {
  setMapOnAll(null);
}

// Shows any markers currently in the array.
function showMarkers() {
  setMapOnAll(map);
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
  hideMarkers();
  markers = [];
}


$(function(){

//     var map;
//     var markers = [];
    
})