var cont = 0;


$(document).ready(function(){
    
	if(parseInt($(".js_numbers").find("span").html()) == 1){
	$(".ip_mapleft .inferior_left img").on("click", function(){
    	
    	$(".image2").find("img").attr("src", $(this).attr("src"));
    	
    	cont = -1;
    
    
    });
    $('.ip_mapleft .inferior_left img').click(function(){
        $("html, .superior_left").animate({ scrollTop: 0 }, 600);
        return false;
    });

	}
    
});


$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 1){
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
	}
    
});


$(document).ready(function(){
	
	if(parseInt($(".js_numbers").find("span").html()) == 1){
	$(".inferior_right .req_panel span").on("click", function(){
    	
    	$(".current").find("#contact").attr("class", "show");
    	$(".current").find("#calculate").attr("class", "hidden");
    	$(".current").find("#maps").attr("class", "hidden");
    	$(".current").find("#share").attr("class", "hidden");
    });
    
	$(".inferior_right .calc_panel span").on("click", function(){
	    	
		$(".current").find("#contact").attr("class", "hidden");
    	$(".current").find("#calculate").attr("class", "show");
    	$(".current").find("#maps").attr("class", "hidden");
    	$(".current").find("#share").attr("class", "hidden");
	});
	$(".inferior_right .map_panel span").on("click", function(){
	    	
		$(".current").find("#contact").attr("class", "hidden");
    	$(".current").find("#calculate").attr("class", "hidden");
    	$(".current").find("#maps").attr("class", "show");
    	$(".current").find("#share").attr("class", "hidden");
	});
	
	$(".inferior_right .share_panel span").on("click", function(){
	    	
		$(".current").find("#contact").attr("class", "hidden");
    	$(".current").find("#calculate").attr("class", "hidden");
    	$(".current").find("#maps").attr("class", "hidden");
    	$(".current").find("#share").attr("class", "show");
	});
	}
    
});




var price_without_dot;
var price_without_coma;




$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 1){
	var precio;
	
  
	if($(".ip_mapright").find("span").eq(2).attr("id") == "2"){
		precio = $(".ip_mapright").find("span").eq(1).html();
		
		price_without_dot = precio.replace('.' , '');
    	price_without_coma = price_without_dot.replace(/,/ , '.');
		
		$(".current #calculate").find("input").eq(0).attr("value", price_without_coma);
		
	}
	if($(".ip_mapright").find("span").eq(4).attr("id") == "2"){
		precio = $(".ip_mapright").find("span").eq(3).html();
		
		price_without_dot = precio.replace('.' , '');
    	price_without_coma = price_without_dot.replace(/,/ , '.');
		
		$(".current #calculate").find("input").eq(0).attr("value", price_without_coma);
	}
	
	$(".current #calculate").find("input").eq(2).attr("value", $(".current #payment_info").find("span").eq(0).html());
	
	$(".current #calculate").find("input").eq(3).attr("value", $(".current #payment_info").find("span").eq(1).html());
	
	var interes = $(".current #calculate").find("input").eq(2).val();
	
	$(".current #calculate").find("input").eq(2).attr("value", interes.replace(/,/ , '.'));
	
	}
    
});


$(document).ready(function(){
	
	if(parseInt($(".js_numbers").find("span").html()) == 1){
    $(".current #calc").on("click", function(){
    	
    	var precio = $(".current #calculate").find("input").eq(0).val();
    	var interes = $(".current #calculate").find("input").eq(2).val();
    	var plazos = $(".current #calculate").find("input").eq(3).val();
    	var signal = $(".current #calculate").find("input").eq(1).val();
    	
    	
    	
    	if((precio == '0') || (precio == '')){
    		alert("Introduce un precio valido.");
    	}else{
    		if ((interes == '0') || (interes == '')){
    			alert("Introduce un interés valido.");
    		}else{
    			if (precio.includes(",")){
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
	}
    
});


$(document).ready(function(){
	if(parseInt($(".js_numbers").find("span").html()) == 1){
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
	
	}
    
});

var posStart = 0;
var posEnd = 0;


$(function() {
	
	if(parseInt($(".js_numbers").find("span").html()) == 1){
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
	}
    
});



$(document).ready(function(){
    
	if(parseInt($(".js_numbers").find("span").html()) == 1){
		var letter = $(".energy_type").find("span").html();
		
		if (letter == 'A'){
			$(".energy_type").attr("style", "background-image: url('/website_real_state/static/img/images/a.png'); background-repeat: no-repeat; background-size: contain;")
		}
		if (letter == 'B'){
			$(".energy_type").attr("style", "background-image: url('/website_real_state/static/img/images/b.png'); background-repeat: no-repeat; background-size: contain;")
		}
		if (letter == 'C'){
			$(".energy_type").attr("style", "background-image: url('/website_real_state/static/img/images/c.png'); background-repeat: no-repeat; background-size: contain;")
		}
		if (letter == 'D'){
			$(".energy_type").attr("style", "background-image: url('/website_real_state/static/img/images/d.png'); background-repeat: no-repeat; background-size: contain;")
		}
		if (letter == 'E'){
			$(".energy_type").attr("style", "background-image: url('/website_real_state/static/img/images/e.png'); background-repeat: no-repeat; background-size: contain;")
		}
		if (letter == 'F'){
			$(".energy_type").attr("style", "background-image: url('/website_real_state/static/img/images/f.png'); background-repeat: no-repeat; background-size: contain;")
		}
		if (letter == 'G'){
			$(".energy_type").attr("style", "background-image: url('/website_real_state/static/img/images/g.png'); background-repeat: no-repeat; background-size: contain;")
		}
	}
    
});




















