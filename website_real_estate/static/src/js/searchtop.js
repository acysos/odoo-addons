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
$(document).ready(function(){
    if(parseInt($(".js_numbers").find("span").html()) == 2){
    	
     }
    
});



$(document).ready(function(){
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
         
         for (i = 0; i < totaltops; i++) {
        	 if (topids[beginimage] == 'False'){
        		 markers2.push([topids[i], topids[aux],"<div class=\"everyTop1\"><div class=\"col-md-12 description_right1\"><div class=\"right3\"><p>"+ topids[beginzone] + "-" + topids[beginaddress] + "<br/>M2: " + topids[beginm2] + "<br/>N° Ref:"+ topids[beginreference] + "<br/><a href=\"/realestate/top/"+ topids[beginid] +"\">Más detalles</a></p></div></div></div>" ]);
        	 }
        	 else{
        		 markers2.push([topids[i], topids[aux],"<div class=\"everyTop1\"><div class=\"col-md-6 image_left1\"><div class=\"left3\"><div class=\"imageP1 col-md-12\"><a href=\"/realestate/top/"+ topids[beginid] +"\"><img style=\"width:100%;height:100%;\" class=\"img-responsive\" src=\"http://127.0.0.1:12069/website/image/base_multi_image.image/" + topids[beginimage] + "/file_db_store\" /></a></div></div></div><div class=\"col-md-6 description_right1\"><div class=\"right3\"><p>"+ topids[beginzone] + "-" + topids[beginaddress] + "<br/>M2: " + topids[beginm2] + "<br/>N° Ref:"+ topids[beginreference] + "<br/><a href=\"/realestate/top/"+ topids[beginid] +"\">Más detalles</a></p></div></div></div>"]);
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



























