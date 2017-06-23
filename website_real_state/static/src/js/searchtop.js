$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 2){
		$("select").change(function(){
		    if (($(this).children(":selected").val() == "sale") || ($(this).children(":selected").val() == "transfer")){
	    		$(".attributes_searchbar").find("div").eq(4).attr("class", "show salepricefrom col-md-2");
	    		$(".attributes_searchbar").find("div").eq(5).attr("class", "show salepriceto col-md-2");
	    		$(".attributes_searchbar").find("div").eq(6).attr("class", "hidden rentpricefrom col-md-2");
	    		$(".attributes_searchbar").find("div").eq(7).attr("class", "hidden rentpriceto col-md-2");
	    	}
	    	else if ($(this).children(":selected").val() == "rent"){
	    		$(".attributes_searchbar").find("div").eq(4).attr("class", "hidden salepricefrom col-md-2");
	    		$(".attributes_searchbar").find("div").eq(5).attr("class", "hidden salepriceto col-md-2");
	    		$(".attributes_searchbar").find("div").eq(6).attr("class", "show rentpricefrom col-md-2");
	    		$(".attributes_searchbar").find("div").eq(7).attr("class", "show rentpriceto col-md-2");
	    	}
	    	else if (($(this).children(":selected").val() == "sale_rent") || ($(this).children(":selected").val() == "rent_sale_option")){
	    		$(".attributes_searchbar").find("div").eq(4).attr("class", "show salepricefrom col-md-2");
	    		$(".attributes_searchbar").find("div").eq(5).attr("class", "show salepriceto col-md-2");
	    		$(".attributes_searchbar").find("div").eq(6).attr("class", "show rentpricefrom col-md-2");
	    		$(".attributes_searchbar").find("div").eq(7).attr("class", "show rentpriceto col-md-2");
	    	}
	    	else {
	    		$(".attributes_searchbar").find("div").eq(4).attr("class", "hidden salepricefrom col-md-2");
	    		$(".attributes_searchbar").find("div").eq(5).attr("class", "hidden salepriceto col-md-2");
	    		$(".attributes_searchbar").find("div").eq(6).attr("class", "hidden rentpricefrom col-md-2");
	    		$(".attributes_searchbar").find("div").eq(7).attr("class", "hidden rentpriceto col-md-2");
	    	}
		});

		}
});





$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 3){
		
		var wordtocut =  "";
		var number = 0;
		
		for (i = 0; i < 6; i++) {
			wordtocut =  $(".top_description").find("#internet_description1").eq(i).html();
			
			if (wordtocut.length > 150){
				$(".top_description").find("#internet_description1").eq(i).html(wordtocut.substring(0, 151) + "...");
				
			}
			
			
		}
		
		}
});


//a partir de aqui es el mapa


(function(){
    'use strict';
     if(parseInt($(".js_numbers").find("span").html()) == 2){
    	 var website = openerp.website;
    	    website.add_template_file('/website_real_state/static/xml/tops_data.xml');
    	    website.openerp_website = {};

    	    // GARDENIA MAP 
    	    website.snippet.animationRegistry.s_partner_google_map = website.snippet.Animation.extend({
    	        selector : "section.s_top_google_map",

    	        start : function() {
    	            var self = this;
    	            if (typeof google === 'object' && typeof google.maps === 'object') {
    	                self.redraw();
    	            }
    	        },
    	    
    	        redraw: function () {
    	            var self = this;


    	            // Default options, will be overwritten by the user
    	            var myOptions = {
    	                zoom:12,
    	                mapTypeId: google.maps.MapTypeId.ROADMAP,
    	                panControl: false,
    	                zoomControl: true,
    	                mapTypeControl: false,
    	                streetViewControl: false,
    	                scrollwheel:false,
    	                mapTypeControlOptions: {
    	                  mapTypeIds: [google.maps.MapTypeId.ROADMAP, 'map_style']
    	                }
    	            };


    	            //Define a default map's colors set
    	            var std = [];
    	            var stdMap = new google.maps.StyledMapType(std, {name: "Std Map"});

    	            //Render Map
    	            var mapC    = self.$target.find('.map_container'),
    	                map     = new google.maps.Map(mapC.get(0), myOptions);

    	            

    	            // partner array
    	            var locationArray = [];
    	            var locationNameArray = [];
    	            var locationInfoArray = [];
    	            var longmax=-180;
    	            var longmin=180;
    	            var latmax=-90;
    	            var latmin=90;
    	            var latcenter=0;
    	            var longcenter=0;

    	            var topidsfromview=$(".invisible_tops_ids").find("span").html();
    	            var topidswithoutsymbol1 = topidsfromview.replace('[' , '')
    	            var topidswithoutsymbol2 = topidswithoutsymbol1.replace(']' , '')
    	            
    	            var topids = topidswithoutsymbol2.split(',')
    	            
    	            
    	            openerp.jsonRpc('/realstate/maptops','call', {"topsids":topids}).then(function(data) {
    	                          var obj=$.parseJSON(data);
    	                          $.each(obj, function(id, top) {
    	                              if(((top.latitude != '0') && (top.latitude !='') && ((top.longitude != '0') && (top.longitude !='')))){
    	                            	  
    	                            	  if (parseFloat(top.latitude)>latmax){latmax=parseFloat(top.latitude);}
        	                              if (parseFloat(top.latitude)<latmin){latmin=parseFloat(top.latitude);}
        	                              if (parseFloat(top.longitude)>longmax){longmax=parseFloat(top.longitude);}
        	                              if (parseFloat(top.longitude)<longmin){longmin=parseFloat(top.longitude);}
        	                              locationArray.push(new google.maps.LatLng(parseFloat(top.latitude),parseFloat(top.longitude)));
        	                              locationNameArray.push(top.name);
        	                              locationInfoArray.push(openerp.qweb.render("tops_data_map.top_data",{'top':top}));
    	                              }
    	                          });

    	              if(self.$target.attr('data-pin-style') == "flat") {
    	                var is_internetExplorer11 = navigator.userAgent.toLowerCase().indexOf('trident') > -1;
    	                var marker_url = (is_internetExplorer11) ? '/snippet_partner_google_map/static/src/img/marker.png' : '/snippet_partner_google_map/static/src/img/marker.svg';

    	                var coord;
    	                 for (coord in locationArray) {
    	                     var marker=new google.maps.Marker({
    	                     position: locationArray[coord],
    	                     map: map,
    	                     animation: google.maps.Animation.DROP,
    	                     icon: marker_url,
    	                     title: locationNameArray[coord],
    	                    });

    	                    self.addInfoWindow(map,marker, locationInfoArray[coord]);

    	                 }



    	                }
    	                else {
    	                    var coord;
    	                    for (coord in locationArray) {
    	                        var marker=new google.maps.Marker({
    	                        position: locationArray[coord],
    	                        map: map,
    	                        animation: google.maps.Animation.DROP,
    	                        title: locationNameArray[coord],
    	                        });

    	                     self.addInfoWindow(map,marker, locationInfoArray[coord]);

    	                    }
    	                }


    	            longcenter=longmin+((longmax-longmin)/2);
    	            latcenter=latmin+((latmax-latmin)/2);
    	            //Update GPS position
    	            //var p   =  this.$target.attr('data-map-gps').substring(1).slice(0, -1).split(',');
    	            var gps =  new google.maps.LatLng( latcenter,longcenter );
    	            map.setCenter(gps);



    	            //Update Map on screen resize
    	            google.maps.event.addDomListener(window, 'resize', function() {
    	                map.setCenter(gps);
    	            });

    	            google.maps.event.addDomListener(map, 'resize', function() {
    	                map.setCenter(gps);
    	            });


    	            });




    	            //Update Map Type
    	            map.setMapTypeId(google.maps.MapTypeId[self.$target.attr('data-map-type')]);

    	            //Update Map Zoom
    	            map.setZoom(parseInt(self.$target.attr('data-map-zoom')));

    	            //Update Map Color (execute only if a map color palette is not defined)
    	            if(self.$target.attr('data-map-color') != ""){
    	                self.update_map_color(map);
    	            }

    	            var input = (document.getElementById('pac-input'));

    	            var autocomplete = new google.maps.places.Autocomplete(input);
    	            autocomplete.bindTo('bounds', map);


    	            google.maps.event.addListener(autocomplete, 'place_changed', function() {
    	                var place = autocomplete.getPlace();
    	                if (!place.geometry) {
    	                    window.alert("Autocomplete's returned place contains no geometry");
    	                    return;
    	                }

    	                // If the place has a geometry, then present it on a map.
    	                if (place.geometry.viewport) {
    	                    map.fitBounds(place.geometry.viewport);
    	                } else {
    	                    map.setCenter(place.geometry.location);
    	                    map.setZoom(17);  // Why 17? Because it looks good.
    	                }
    	            });


    	        },

    	        addInfoWindow:function (map,marker, message) {

    	            var infoWindow = new google.maps.InfoWindow({
    	                content: message
    	            });

    	            google.maps.event.addListener(marker, 'click', function () {
    	                infoWindow.open(map, marker);
    	            });
    	        },


    	        update_map_color: function(map){
    	            var self = this;
    	            var mapColor = eval("self." + self.$target.attr('data-map-color'));
    	            
    	            var thisMap = new google.maps.StyledMapType(mapColor, {name: "TEST"});
    	            map.mapTypes.set('map_style', thisMap);
    	            map.setMapTypeId('map_style');
    	            
    	        }


    	    });
		
		}
    
})();


$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 3){
		
		
		$("#more_featured").on("click", function(){
			
			$(".listfeatured1").attr("class", "hidden container listfeatured1");
			$(".listfeatured2").attr("class", "show container listfeatured2");
			
		});
		
		var url = window.location.href;
		
		if (url.includes("page")){
			$(".listfeatured1").attr("class", "hidden container listfeatured1");
			$(".listfeatured2").attr("class", "show container listfeatured2");
		}
		
		if (url.includes("2")){
			$(".pagination").find("a").eq(0).attr("href", "1");
		}
		
		
		$(".pagination").find("li").eq(1).on("click", function(){
			
			$(".pagination").find("a").eq(1).attr("href", "1");
			
		});
		
		
		
		}
});


$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 3){
		
		var wordtocut =  "";
		var number = 0;
		
		for (i = 0; i < 9; i++) {
			wordtocut =  $(".top_description1").find("#internet_description2").eq(i).html();
			if (wordtocut.length > 150){
				$(".top_description1").find("#internet_description2").eq(i).html(wordtocut.substring(0, 151) + "...");
				
			}
			
			
		}
		
		}
});



























