var cont = 0;
var price_without_dot = 0;
var price_without_coma = 0;
var posStart = 0;
var posEnd = 0;


$(document).ready(function(){
    
	//Click in photo to replace for above
	
	if(parseInt($(".js_numbers").find("span").html()) == 1){
	$(".ip_mapleft .inferior_left img").on("click", function(){
    	
    	$(".image2").find("img").attr("src", $(this).attr("src"));
    	
    	cont = -1;
    
    
    });
	
	//When change a photo the page up
	
    $('.ip_mapleft .inferior_left img').click(function(){
        $("html, .superior_left").animate({ scrollTop: 0 }, 600);
        return false;
    });
    
    //Photo next button
    
	$(".ip_mapleft .buttonnext  img").on("click", function(){
	    	var parte1 = $(".image2").find("img").eq(0);
	    	var parte2 = $(".inferior_left").find("img").eq(cont);
	    	
	    	if (cont == $(".inferior_left").find("img").length){
	    		cont = 0;
	    		parte2 = $(".inferior_left").find("img").eq(cont);
	    		parte1.attr("src", parte2.attr("src"));
	    	}else{
	    		cont += 1;
	    		parte2 = $(".inferior_left").find("img").eq(cont);
	    		parte1.attr("src", parte2.attr("src"));
	    	}
	    });
	    
	//Photo back photo
	
	$(".ip_mapleft .buttonback  img").on("click", function(){
			var parte1 = $(".image2").find("img").eq(0);
			var parte2 = $(".inferior_left").find("img").eq(cont);
			
			if (cont == 0){
				cont = $(".inferior_left").find("img").length
				parte2 = $(".inferior_left").find("img").eq(cont);
				parte1.attr("src", parte2.attr("src"));
				
			}else{
				cont -= 1;
				parte2 = $(".inferior_left").find("img").eq(cont);
				parte1.attr("src", parte2.attr("src"));
			}
		});

	//Hide all div except gallery
	
	$(".gallery_panel").on("click", function(){
    	
    	$(".current").find("#contact").attr("class", "hidden");
    	$(".current").find("#calculate").attr("class", "hidden");
//    	$(".current").find("#maps").attr("class", "hidden");
    	$(".current").find("#share").attr("class", "hidden");
    	$(".current").find("#gallery").attr("class", "show");
    });

	//Hide all div except contact
	
	$(".req_panel").on("click", function(){
    	
    	$(".current").find("#contact").attr("class", "show");
    	$(".current").find("#calculate").attr("class", "hidden");
//    	$(".current").find("#maps").attr("class", "hidden");
    	$(".current").find("#share").attr("class", "hidden");
    	$(".current").find("#gallery").attr("class", "hidden");
    });
	
	//Hide all div except calculator
    
	$(".calc_panel").on("click", function(){
	    	
		$(".current").find("#contact").attr("class", "hidden");
    	$(".current").find("#calculate").attr("class", "show");
//    	$(".current").find("#maps").attr("class", "hidden");
    	$(".current").find("#share").attr("class", "hidden");
    	$(".current").find("#gallery").attr("class", "hidden");
	});
	
	//Hide all div except map
	
//	$(".map_panel").on("click", function(){
//	    	
//		$(".current").find("#contact").attr("class", "hidden");
//    	$(".current").find("#calculate").attr("class", "hidden");
//    	$(".current").find("#maps").attr("class", "show");
//    	$(".current").find("#share").attr("class", "hidden");
//    	$(".current").find("#gallery").attr("class", "hidden");
//	});
	
	//Hide all div except share
	
	$(".share_panel").on("click", function(){
	    	
		$(".current").find("#contact").attr("class", "hidden");
    	$(".current").find("#calculate").attr("class", "hidden");
//    	$(".current").find("#maps").attr("class", "hidden");
    	$(".current").find("#share").attr("class", "show");
    	$(".current").find("#gallery").attr("class", "hidden");
	});
	
	//Check if the calculartor number are float and fix them
	
	var precio;
	
	if($(".ip_mapright").find("span").eq(3).attr("id") == "2"){
		precio = $(".ip_mapright").find("span").eq(1).html();
		
		price_without_dot = precio.replace('.' , '');
    	price_without_coma = price_without_dot.replace(/,/ , '.');
		
		$(".current #calculate").find("input").eq(0).attr("value", price_without_coma);
		
	}
	if($(".ip_mapright").find("span").eq(6).attr("id") == "2"){
		precio = $(".ip_mapright").find("span").eq(4).html();
		
		price_without_dot = precio.replace('.' , '');
    	price_without_coma = price_without_dot.replace(/,/ , '.');
		
		$(".current #calculate").find("input").eq(0).attr("value", price_without_coma);
	}
	
	$(".current #calculate").find("input").eq(2).attr("value", $(".current #payment_info").find("span").eq(0).html());
	
	$(".current #calculate").find("input").eq(3).attr("value", $(".current #payment_info").find("span").eq(1).html());
	
	var interes = $(".current #calculate").find("input").eq(2).val();
	
	$(".current #calculate").find("input").eq(2).attr("value", interes.replace(/,/ , '.'));
    
	//Calculator operations
	
	$(".current #calc").on("click", function(){
    	
    	var precio2 = $(".current #calculate").find("input").eq(0).val();
    	var interes = $(".current #calculate").find("input").eq(2).val();
    	var plazos = $(".current #calculate").find("input").eq(3).val();
    	var signal = $(".current #calculate").find("input").eq(1).val();
    	
    	if((precio2 == '0') || (precio2 == '')){
    		alert("Introduce un precio valido.");
    	}else{
    		if ((interes == '0') || (interes == '')){
    			alert("Introduce un interés valido.");
    		}else{
    			if (precio2.includes(",")){
    				alert("Introduce un punto en lugar de una coma.");
    			}else{
    				if ((plazos == '0') || (plazos == '')){
        				alert("Introduce un número de plazos valido.");
        			}else{
        				if((signal == '0') || (signal == '')){
        					$(".current #calculate").find("input").eq(5).attr("value", price_without_coma);
        				}else{
        					if (interes.includes(",")){
        						alert("Introduce un punto en lugar de una coma.");
        					}else{
        						$(".current #calculate").find("input").eq(5).attr("value", (parseFloat(price_without_coma) - parseFloat(signal)));
        					}
        				}
        			}
    			}
    		}
    	}
    	var meses = (parseFloat(plazos) * 12);
    	
    	$(".current #calculate").find("input").eq(6).attr("value", meses);
    	
    	var interes12 = ((parseFloat(interes) / 12)/100);
    	
    	var cuota = (parseFloat($(".current #calculate").find("input").eq(5).val()) / ((1 - Math.pow((1 + interes12), (-1 * meses))) / interes12));
    	
    	$(".current #calculate").find("input").eq(7).attr("value", cuota.toFixed(2));
    	    	
    });
	
	//Check if the top is new
	
	var max = $(".superior_left .new").find("span").eq(1).html();
	var fecha = $(".superior_left .new").find("span").eq(0).html();
	
	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1;

	var yyyy = today.getFullYear();
	if(dd<10){
	    dd='0'+dd;
	} 
	if(mm<10){
	    mm='0'+mm;
	} 
	var result = dd+'/'+mm+'/'+yyyy;
	
	var aFecha1 = fecha.split('/'); 
	var aFecha2 = result.split('/'); 
	var fFecha1 = Date.UTC(aFecha1[2],aFecha1[1]-1,aFecha1[0]); 
	var fFecha2 = Date.UTC(aFecha2[2],aFecha2[1]-1,aFecha2[0]); 
	var dif = fFecha2 - fFecha1;
	var dias = Math.floor(dif / (1000 * 60 * 60 * 24)); 
	
	if (dias <= parseInt(max)){
		$(".superior_left .new").find("img").attr("class", "show");
	}
	
	//Gallery slider for smartphones
	
	$('.image2').bind('touchstart',function(e){
		var touch = e.originalEvent.touches[0];
		var elm = $(this).offset();
		var x = touch.pageX - elm.left;
		var y = touch.pageY - elm.top;
		
		posStart = x;

	});
	$('.image2').bind('touchend',function(e){
		var touch = e.originalEvent.changedTouches[0];
		var elm = $(this).offset();
		var x = touch.pageX - elm.left;
		var y = touch.pageY - elm.top;
		
		posEnd = x;
		
		var operation = posEnd - posStart
		
		if (operation > 0){
			var parte1 = $(".image2").find("img").eq(0);
			var parte2 = $(".inferior_left").find("img").eq(cont);
			
			if (cont == 0){
				cont = $(".inferior_left").find("img").length
				parte2 = $(".inferior_left").find("img").eq(cont);
				parte1.attr("src", parte2.attr("src"));
				
			}else{
				cont -= 1;
				parte2 = $(".inferior_left").find("img").eq(cont);
				parte1.attr("src", parte2.attr("src"));
				
			}
		}
		if (operation < 0){
			var parte1 = $(".image2").find("img").eq(0);
	    	var parte2 = $(".inferior_left").find("img").eq(cont);
	    	
	    	if (cont == $(".inferior_left").find("img").length){
	    		cont = 0;
	    		parte2 = $(".inferior_left").find("img").eq(cont);
	    		parte1.attr("src", parte2.attr("src"));
	    	}else{
	    		cont += 1;
	    		parte2 = $(".inferior_left").find("img").eq(cont);
	    		parte1.attr("src", parte2.attr("src"));
	    	}
		}
	});
	
	//Energy efficiency color
	
	var letter = $(".energy_type").find("span").html();
	
	if (letter == 'A'){
		$(".energy_type").attr("style", "background-image: url('/website_real_estate/static/img/images/a.png'); background-repeat: no-repeat; background-size: contain;")
	}
	if (letter == 'B'){
		$(".energy_type").attr("style", "background-image: url('/website_real_estate/static/img/images/b.png'); background-repeat: no-repeat; background-size: contain;")
	}
	if (letter == 'C'){
		$(".energy_type").attr("style", "background-image: url('/website_real_estate/static/img/images/c.png'); background-repeat: no-repeat; background-size: contain;")
	}
	if (letter == 'D'){
		$(".energy_type").attr("style", "background-image: url('/website_real_estate/static/img/images/d.png'); background-repeat: no-repeat; background-size: contain;")
	}
	if (letter == 'E'){
		$(".energy_type").attr("style", "background-image: url('/website_real_estate/static/img/images/e.png'); background-repeat: no-repeat; background-size: contain;")
	}
	if (letter == 'F'){
		$(".energy_type").attr("style", "background-image: url('/website_real_estate/static/img/images/f.png'); background-repeat: no-repeat; background-size: contain;")
	}
	if (letter == 'G'){
		$(".energy_type").attr("style", "background-image: url('/website_real_estate/static/img/images/g.png'); background-repeat: no-repeat; background-size: contain;")
	}
	
	
	
	
	
	
	}
});



// Maps
$(window).load(function(){
    if(parseInt($(".js_numbers").find("span").html()) == 1){
    	
	     var long = $("#maps").find("span").eq(0).html();
	     var latit = $("#maps").find("span").eq(1).html();
	     var map = new L.Map('map');   
	        
	 	 L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	       attribution: '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
	       maxZoom: 18
	     }).addTo(map);
	     map.attributionControl.setPrefix(''); // Don't show the 'Powered by Leaflet' text.
	
	     var centeroflocations = new L.LatLng(parseFloat(long),parseFloat(latit)); 
	     map.setView(centeroflocations, 13);
	    
	     // Define an array. This could be done in a seperate js file.
	     // This tidy formatted section could even be generated by a server-side script
	     // or fetched seperately as a jsonp request.
	     var markerLocation = new L.LatLng(parseFloat(long), parseFloat(latit));
	     var marker = new L.Marker(markerLocation);
	     map.addLayer(marker);
	     
	     //si la pantalla es pequeña oculta el mapa y pone un enlace en su lugar
	     if ($(window).width() < 768){
	    	 var toPrecision = zoomPrecision(15);
			 lat = toPrecision(long);
			 lon = toPrecision(latit);
			 $("#maps").find("a").attr("class", "show urltomaps");
			 $("#maps").find("a").attr("href", " http://osm.org/go/" + makeShortCode(lat, lon, 15) + "==?m");
			 $("#maps-div").find("div").attr("class", "hidden");
		 }
	     
	     //coloca el banner pending en funcion del campo website_acta
	     var n = $( ".pending" ).find('span').length;	
		 for (i = 0; i < n; i++) {
			if (($( ".pending" ).find('span').eq(i).html() == 'Pendiente de Venta') || ($( ".pending" ).find('span').eq(i).html() == 'Pendiente de Alquilar')){
				$(".pending").find("img").eq(i).attr("class", "show");
			}
		 }
     
     }
    
});

function zoomPrecision(zoom) {
    var decimals = Math.pow(10, Math.floor(zoom/3));
    return function(x) {
         return Math.round(x * decimals) / decimals;
    };
}
function interlace(x, y) {
    x = (x | (x << 8)) & 0x00ff00ff;
    x = (x | (x << 4)) & 0x0f0f0f0f;
    x = (x | (x << 2)) & 0x33333333;
    x = (x | (x << 1)) & 0x55555555;

    y = (y | (y << 8)) & 0x00ff00ff;
    y = (y | (y << 4)) & 0x0f0f0f0f;
    y = (y | (y << 2)) & 0x33333333;
    y = (y | (y << 1)) & 0x55555555;

    return (x << 1) | y;
}

/*
 * Called to create a short code for the short link.
 */
function makeShortCode(lat, lon, zoom) {
    char_array = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_~";
    var x = Math.round((lon + 180.0) * ((1 << 30) / 90.0));
    var y = Math.round((lat +  90.0) * ((1 << 30) / 45.0));
    // JavaScript only has to keep 32 bits of bitwise operators, so this has to be
    // done in two parts. each of the parts c1/c2 has 30 bits of the total in it
    // and drops the last 4 bits of the full 64 bit Morton code.
    var str = "";
    var c1 = interlace(x >>> 17, y >>> 17), c2 = interlace((x >>> 2) & 0x7fff, (y >>> 2) & 0x7fff);
    for (var i = 0; i < Math.ceil((zoom + 8) / 3.0) && i < 5; ++i) {
        digit = (c1 >> (24 - 6 * i)) & 0x3f;
        str += char_array.charAt(digit);
    }
    for (var i = 5; i < Math.ceil((zoom + 8) / 3.0); ++i) {
        digit = (c2 >> (24 - 6 * (i - 5))) & 0x3f;
        str += char_array.charAt(digit);
    }
    for (var i = 0; i < ((zoom + 8) % 3); ++i) {
        str += "-";
    }
    return str;
}




