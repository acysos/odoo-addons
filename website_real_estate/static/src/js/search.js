$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 2){

		//Add fields to search depending of the option selected
		$("select").change(function(){
		    if (($(this).children(":selected").val() == "sale") || ($(this).children(":selected").val() == "transfer")){
	    		$(".attributes_searchbar .salepricefrom").attr("class", "show salepricefrom col-md-2");
	    		$(".attributes_searchbar .salepriceto").attr("class", "show salepriceto col-md-2");
	    		$(".attributes_searchbar .rentpricefrom").attr("class", "hidden rentpricefrom col-md-2");
	    		$(".attributes_searchbar .rentpriceto").attr("class", "hidden rentpriceto col-md-2");
	    		$(".search-advanced .salepricefrom").attr("class", "show salepricefrom");
	    		$(".search-advanced .salepriceto").attr("class", "show salepriceto");
	    		$(".search-advanced .rentpricefrom").attr("class", "hidden rentpricefrom");
	    		$(".search-advanced .rentpriceto").attr("class", "hidden rentpriceto");
	    		document.getElementById("rpf").value = 'Rent price from';
	    		document.getElementById("adv_rpf").value = 'Rent price from';
	    		document.getElementById("rpt").value = 'Rent price to';
	    		document.getElementById("adv_rpt").value = 'Rent price to';
	    	}
	    	else if ($(this).children(":selected").val() == "rent"){
	    		$(".attributes_searchbar .salepricefrom").attr("class", "hidden salepricefrom col-md-2");
	    		$(".attributes_searchbar .salepriceto").attr("class", "hidden salepriceto col-md-2");
	    		$(".attributes_searchbar .rentpricefrom").attr("class", "show rentpricefrom col-md-2");
	    		$(".attributes_searchbar .rentpriceto").attr("class", "show rentpriceto col-md-2");
	    		$(".search-advanced .salepricefrom").attr("class", "hidden salepricefrom");
	    		$(".search-advanced .salepriceto").attr("class", "hidden salepriceto");
	    		$(".search-advanced .rentpricefrom").attr("class", "show rentpricefrom");
	    		$(".search-advanced .rentpriceto").attr("class", "show rentpriceto");
	    		document.getElementById("spf").value = 'Sale price from';
	    		document.getElementById("adv_spf").value = 'Sale price from';
	    		document.getElementById("spt").value = 'Sale price to';
	    		document.getElementById("adv_spt").value = 'Sale price to';
	    	}
	    	else if (($(this).children(":selected").val() == "sale_rent") || ($(this).children(":selected").val() == "rent_sale_option")){
	    		$(".attributes_searchbar .salepricefrom").attr("class", "show salepricefrom col-md-2");
	    		$(".attributes_searchbar .salepriceto").attr("class", "show salepriceto col-md-2");
	    		$(".attributes_searchbar .rentpricefrom").attr("class", "show rentpricefrom col-md-2");
	    		$(".attributes_searchbar .rentpriceto").attr("class", "show rentpriceto col-md-2");
	    		$(".search-advanced .salepricefrom").attr("class", "show salepricefrom");
	    		$(".search-advanced .salepriceto").attr("class", "show salepriceto");
	    		$(".search-advanced .rentpricefrom").attr("class", "show rentpricefrom");
	    		$(".search-advanced .rentpriceto").attr("class", "show rentpriceto");
	    	}
	    	else if ($(this).children(":selected").val() == "operation"){
	    		$(".attributes_searchbar .salepricefrom").attr("class", "hidden salepricefrom col-md-2");
	    		$(".attributes_searchbar .salepriceto").attr("class", "hidden salepriceto col-md-2");
	    		$(".attributes_searchbar .rentpricefrom").attr("class", "hidden rentpricefrom col-md-2");
	    		$(".attributes_searchbar .rentpriceto").attr("class", "hidden rentpriceto col-md-2");
	    		$(".search-advanced .salepricefrom").attr("class", "hidden salepricefrom");
	    		$(".search-advanced .salepriceto").attr("class", "hidden salepriceto");
	    		$(".search-advanced .rentpricefrom").attr("class", "hidden rentpricefrom");
	    		$(".search-advanced .rentpriceto").attr("class", "hidden rentpriceto");
	    		document.getElementById("spf").value = 'Sale price from';
	    		document.getElementById("adv_spf").value = 'Sale price from';
	    		document.getElementById("spt").value = 'Sale price to';
	    		document.getElementById("adv_spt").value = 'Sale price to';
	    		document.getElementById("rpf").value = 'Rent price from';
	    		document.getElementById("adv_rpf").value = 'Rent price from';
	    		document.getElementById("rpt").value = 'Rent price to';
	    		document.getElementById("adv_rpt").value = 'Rent price to';
	    	}
		    
			if (($(this).children(":selected").val() == "flat") || ($(this).children(":selected").val() == "chalet") || ($(this).children(":selected").val() == "house")){
				$(".search-advanced .rooms").attr("class", "show rooms");
			} else {
				var selected = document.getElementById("categories").value;
				if (selected == 'flat' || selected == 'chalet' || selected == 'house') {
					$(".search-advanced .rooms").attr("class", "show rooms");
				} else {
					$(".search-advanced .rooms").attr("class", "hidden rooms");
				}

				document.getElementById("default-bed").checked = 'checked';
				document.getElementById("default-bath").checked = 'checked';
			}
			
			if (($(this).children(":selected").val() == "unlimited") || 
					($(this).children(":selected").val() == "flat") || 
					($(this).children(":selected").val() == "shop") ||
					($(this).children(":selected").val() == "premise") ||
					($(this).children(":selected").val() == "chalet") ||
					($(this).children(":selected").val() == "house") ||
					($(this).children(":selected").val() == "office") ||
					($(this).children(":selected").val() == "premise-office") ||
					($(this).children(":selected").val() == "industrial_unit") ||
					($(this).children(":selected").val() == "hotel_industry") ||
					($(this).children(":selected").val() == "parking") ||
					($(this).children(":selected").val() == "box_room") ||
					($(this).children(":selected").val() == "land"))
			{
				$(".search-advanced .flat-top-type").attr("class", "hidden flat-top-type");
				$(".search-advanced .shop-top-type").attr("class", "hidden shop-top-type");
				$(".search-advanced .premise-top-type").attr("class", "hidden premise-top-type");
				$(".search-advanced .chalet-top-type").attr("class", "hidden chalet-top-type");
				$(".search-advanced .house-top-type").attr("class", "hidden house-top-type");
				$(".search-advanced .office-top-type").attr("class", "hidden office-top-type");
				$(".search-advanced .premise-office-top-type").attr("class", "hidden premise-office-top-type");
				$(".search-advanced .industrial_unit-top-type").attr("class", "hidden industrial_unit-top-type");
				$(".search-advanced .hotel_industry-top-type").attr("class", "hidden hotel_industry-top-type");
				$(".search-advanced .parking-top-type").attr("class", "hidden parking-top-type");
				$(".search-advanced .box_room-top-type").attr("class", "hidden box_room-top-type");
				$(".search-advanced .land-top-type").attr("class", "hidden land-top-type");
				if (($(this).children(":selected").val() == "flat")) {
					$(".search-advanced .flat-top-type").attr("class", "show flat-top-type");
				}
				if (($(this).children(":selected").val() == "shop")) {
					$(".search-advanced .shop-top-type").attr("class", "show shop-top-type");
				}
				if (($(this).children(":selected").val() == "premise")) {
					$(".search-advanced .premise-top-type").attr("class", "show premise-top-type");
				}
				if (($(this).children(":selected").val() == "chalet")) {
					$(".search-advanced .chalet-top-type").attr("class", "show chalet-top-type");
				}
				if (($(this).children(":selected").val() == "house")) {
					$(".search-advanced .house-top-type").attr("class", "show house-top-type");
				}
				if (($(this).children(":selected").val() == "office")) {
					$(".search-advanced .office-top-type").attr("class", "show office-top-type");
				}
				if (($(this).children(":selected").val() == "premise-office")) {
					$(".search-advanced .premise-office-top-type").attr("class", "show premise-office-top-type");
				}
				if (($(this).children(":selected").val() == "industrial_unit")) {
					$(".search-advanced .industrial_unit-top-type").attr("class", "show industrial_unit-top-type");
				}
				if (($(this).children(":selected").val() == "hotel_industry")) {
					$(".search-advanced .hotel_industry-top-type").attr("class", "show hotel_industry-top-type");
				}
				if (($(this).children(":selected").val() == "parking")) {
					$(".search-advanced .parking-top-type").attr("class", "show parking-top-type");
				}
				if (($(this).children(":selected").val() == "box_room")) {
					$(".search-advanced .box_room-top-type").attr("class", "show box_room-top-type");
				}
				if (($(this).children(":selected").val() == "land")) {
					$(".search-advanced .land-top-type").attr("class", "show land-top-type");
				}
				document.getElementById("default-subtype").checked = 'checked';
			}
			
		});

		//Hide the map in small screens and make responsive the search
		
		if ($(window).width() < 768){
			$(".ocultbutton").attr("class", "show ocultbutton");
			$(".attributes_searchbar").attr("class", "attributes_searchbar row hidden");
			$("#occultlistmap").find("div").attr("class", "hidden");
		}
		
		$("#searchclick").on("click", function(){
	    	
			$(".ocultbutton").attr("class", "hidden ocultbutton");
			$(".attributes_searchbar").attr("class", "attributes_searchbar row show");
			
	    });
		
		$("#spf").on('change', function() {
			document.getElementById("adv_spf").value = this.value;
		});
		$("#adv_spf").on('change', function() {
			document.getElementById("spf").value = this.value;
		});

		$("#spt").on('change', function() {
			document.getElementById("adv_spt").value = this.value;
		});
		$("#adv_spt").on('change', function() {
			document.getElementById("spt").value = this.value;
		});

		$("#rpf").on('change', function() {
			document.getElementById("adv_rpf").value = this.value;
		});
		$("#adv_rpf").on('change', function() {
			document.getElementById("rpf").value = this.value;
		});
		
		$("#rpt").on('change', function() {
			document.getElementById("adv_rpt").value = this.value;
		});
		$("#adv_rpt").on('change', function() {
			document.getElementById("rpt").value = this.value;
		});

		$("#af").on('change', function() {
			document.getElementById("adv_af").value = this.value;
		});
		$("#adv_af").on('change', function() {
			document.getElementById("af").value = this.value;
		});

		$("#at").on('change', function() {
			document.getElementById("adv_at").value = this.value;
		});
		$("#adv_at").on('change', function() {
			document.getElementById("at").value = this.value;
		});

	}
});


$(window).load(function() {
	if(parseInt($(".js_numbers").find("span").html()) == 2){
		//Show banner pending
		
		var n = $( ".pending" ).length;
		
		for (i = 0; i < n; i++) {
			if (($( ".pending" ).eq(i).find('span').html() == 'Pendiente de Venta') || ($( ".pending" ).eq(i).find('span').html() == 'Pendiente de Alquilar')){
				$(".pending").find("img").eq(i).attr("class", "show");
			}
		}	
	}
});





//Map
$(window).load(function(){
     if(parseInt($(".js_numbers").find("span").html()) == 2){
    	 
    	 var topidsfromview=$(".invisible_tops_ids").find("span").html();
     	 while (topidsfromview.indexOf('[') != -1)
     		topidsfromview = topidsfromview.replace('[' , '');
     	 while (topidsfromview.indexOf(']') != -1)
     		topidsfromview = topidsfromview.replace(']' , '');
     	 while (topidsfromview.indexOf("u'") != -1)
     		topidsfromview = topidsfromview.replace("u'" , "");
     	 while (topidsfromview.indexOf("'") != -1)
     		topidsfromview = topidsfromview.replace("'" , "");
         var topids = topidsfromview.split(', ')
          
         var totaltops = topids.length / 8;
         var markers2 = [];
         
         var aux = totaltops;
         
         var sumlat = 0;
         var sumlong = 0;
         
         var beginid = totaltops * 2;
         var beginimage = totaltops * 3;
         var beginzone = totaltops * 4;
         var beginaddress = totaltops * 5;
         var beginm2 = totaltops * 6;
         var beginreference = totaltops * 7;
         
         var url_image = $(".url_param_proof").html();
         
         
         for (i = 0; i < totaltops; i++) {
        	 
        	 if (topids[beginaddress].includes('xf1')){
        		 topids[beginaddress] = topids[beginaddress].replace(/\\/g, '');
        		 topids[beginaddress] = topids[beginaddress].replace('xf1', 'ñ')
        	 }
        	 
        	 if (topids[beginaddress].includes('xe1')){
        		 topids[beginaddress] = topids[beginaddress].replace(/\\/g, '');
        		 topids[beginaddress] = topids[beginaddress].replace('xe1', 'á')
        	 }
        	 
        	 if (topids[beginaddress].includes('xe9')){
        		 topids[beginaddress] = topids[beginaddress].replace(/\\/g, '');
        		 topids[beginaddress] = topids[beginaddress].replace('xe9', 'é')
        	 }
        	 
        	 if (topids[beginaddress].includes('xed')){
        		 topids[beginaddress] = topids[beginaddress].replace(/\\/g, '');
        		 topids[beginaddress] = topids[beginaddress].replace('xed', 'í')
        	 }
        	 
        	 if (topids[beginaddress].includes('xf3')){
        		 topids[beginaddress] = topids[beginaddress].replace(/\\/g, '');
        		 topids[beginaddress] = topids[beginaddress].replace('xf3', 'ó')
        	 }
        	 
        	 if (topids[beginaddress].includes('xfa')){
        		 topids[beginaddress] = topids[beginaddress].replace(/\\/g, '');
        		 topids[beginaddress] = topids[beginaddress].replace('xfa', 'ú')
        	 }
        	 
        	 if (topids[beginaddress].includes('xfc')){
        		 topids[beginaddress] = topids[beginaddress].replace(/\\/g, '');
        		 topids[beginaddress] = topids[beginaddress].replace('xfc', 'ü')
        	 }
        	 
        	 if (topids[beginzone].includes('xd1')){
        		 topids[beginzone] = topids[beginzone].replace(/\\/g, '');
        		 topids[beginzone] = topids[beginzone].replace('xd1', 'Ñ')
        	 }
        	 
        	 if (topids[beginzone].includes('xc1')){
        		 topids[beginzone] = topids[beginzone].replace(/\\/g, '');
        		 topids[beginzone] = topids[beginzone].replace('xc1', 'Á')
        	 }
        	 
        	 if (topids[beginzone].includes('xc9')){
        		 topids[beginzone] = topids[beginzone].replace(/\\/g, '');
        		 topids[beginzone] = topids[beginzone].replace('xc9', 'É')
        	 }
        	 
        	 if (topids[beginzone].includes('xcd')){
        		 topids[beginzone] = topids[beginzone].replace(/\\/g, '');
        		 topids[beginzone] = topids[beginzone].replace('xcd', 'Í')
        	 }
        	 
        	 if (topids[beginzone].includes('xd3')){
        		 topids[beginzone] = topids[beginzone].replace(/\\/g, '');
        		 topids[beginzone] = topids[beginzone].replace('xd3', 'Ó')
        	 }
        	 
        	 if (topids[beginzone].includes('xda')){
        		 topids[beginzone] = topids[beginzone].replace(/\\/g, '');
        		 topids[beginzone] = topids[beginzone].replace('xda', 'Ú')
        	 }
        	 
        	 if (topids[beginzone].includes('xdc')){
        		 topids[beginzone] = topids[beginzone].replace(/\\/g, '');
        		 topids[beginzone] = topids[beginzone].replace('xdc', 'Ü')
        	 }
        	 
        	 
        	 if (topids[beginimage] == 'False'){
        		 markers2.push([topids[i], topids[aux],"<div class=\"everyTop1\"><div class=\"col-md-12 col-sm-12 description_right1\"><div class=\"right3\"><p>"+ topids[beginzone] + "-" + topids[beginaddress] + "<br/>M2: " + topids[beginm2] + "<br/>N° Ref:"+ topids[beginreference] + "<br/><a href=\"/realestate/top/"+ topids[beginid] +"\">Más detalles</a></p></div></div></div>" ]);
        		 
        	 }
        	 else{
        		 var url_image = $(".url_param_proof").html();
        		 markers2.push([topids[i], topids[aux],"<div class=\"everyTop1\"><div class=\"col-md-6 col-sm-6 image_left1\"><div class=\"left3\"><div class=\"imageP1 col-md-12  col-sm-12\"><a href=\"/realestate/top/"+ topids[beginid] +"\"><img style=\"width:100%;height:100%;\" class=\"img-responsive\" src=\"" + url_image + "/website/image/base_multi_image.image/" + topids[beginimage] + "/file_db_store\" /></a></div></div></div><div class=\"col-md-6  col-sm-6 description_right1\"><div class=\"right3\"><p>"+ topids[beginzone] + "-" + topids[beginaddress] + "<br/>M2: " + topids[beginm2] + "<br/>N° Ref:"+ topids[beginreference] + "<br/><a href=\"/realestate/top/"+ topids[beginid] +"\">Más detalles</a></p></div></div></div>"]);
        		 
        	 }
        	 
        	 sumlat += parseFloat(topids[i]);
        	 sumlong += parseFloat(topids[aux]);
        	 
        	 beginzone +=1;
        	 beginaddress +=1;
        	 beginm2 +=1;
        	 beginid +=1;
        	 beginimage +=1;
        	 beginreference +=1;
        	 aux += 1;
        	}
         
         
         
    	 var map = new L.Map('map'); 
    	 
    	 
         
      	 L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
            maxZoom: 18
         }).addTo(map);
         map.attributionControl.setPrefix(''); // Don't show the 'Powered by Leaflet' text.

         var centeroflocations = new L.LatLng(sumlat/totaltops,sumlong/totaltops); 
         map.setView(centeroflocations, 13);
         
         // Define an array. This could be done in a seperate js file.
         // This tidy formatted section could even be generated by a server-side script
         // or fetched seperately as a jsonp request.
         var markers = [
            [ parseFloat(markers2[0][1]), parseFloat(markers2[0][0]), markers2[0][2] ],
            [ -0.119623, 51.503308, "London Eye" ],
            [ -0.1279688, 51.5077286, "Nelson's Column<br><a href=\"https://en.wikipedia.org/wiki/Nelson's_Column\">wp</a>" ] 
         ];
         
         
         //Loop through the markers array
         for (var i=0; i<markers2.length; i++) {
            
            var lon = markers2[i][1];
            var lat = markers2[i][0];
            var popupText = markers2[i][2];
            
            var markerLocation = new L.LatLng(lat, lon);
            var marker = new L.Marker(markerLocation);
            map.addLayer(marker);
     
            marker.bindPopup(popupText);
         
         }
         
		}
    
});




























