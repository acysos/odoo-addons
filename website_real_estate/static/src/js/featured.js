$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 3){
		
		//Sirve para ver mas inmuebles destacados
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

$(window).load(function() {
	if(parseInt($(".js_numbers").find("span").html()) == 3){
		//Muestra el banner pending
		
		var n = $( ".pending" ).length;
		
		for (i = 0; i < n; i++) {
			if (($( ".pending" ).eq(i).find('span').html() == 'Pendiente de Venta') || ($( ".pending" ).eq(i).find('span').html() == 'Pendiente de Alquilar')){
				$(".pending").find("img").eq(i).attr("class", "show");
			}
		}	
	}
});


$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 3){
		
		/*Sirve para acortar la descripción de los inmuebles si tiene mas de
		  150 caracteres. */
		var wordtocut1 =  "";
		var wordtocut2 =  "";
		var number = 0;
		
		for (i = 0; i < 9; i++) {
			wordtocut2 =  $(".top_description1").find("#internet_description2").eq(i).html();
			if (wordtocut2.length > 150){
				$(".top_description1").find("#internet_description2").eq(i).html(wordtocut2.substring(0, 151) + "...");
				
			}
			if (i <= 6){
				wordtocut1 =  $(".top_description").find("#internet_description1").eq(i).html();
				if (wordtocut1.length > 150){
					$(".top_description").find("#internet_description1").eq(i).html(wordtocut1.substring(0, 151) + "...");
					
				}
			}
		}
		
	}
});























