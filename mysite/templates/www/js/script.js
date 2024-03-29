/* Author: 

*/

$('a.inline-pop').fancybox();

$('a.iframe-pop').fancybox({
    'type': 'iframe',
});

$('#add-feed-form').submit(function() {
    $.fancybox.close();
    return false;
});

$('a.iframe-story-pop').click(function () {

    $.fancybox.showActivity();

    if (document.body && document.body.offsetWidth) {
        winW = document.body.offsetWidth;
        winH = document.body.offsetHeight;
    }

    if (document.compatMode=='CSS1Compat' &&
        document.documentElement &&
        document.documentElement.offsetWidth ) {
        winW = document.documentElement.offsetWidth;
        winH = document.documentElement.offsetHeight;
    }

    if (window.innerWidth && window.innerHeight) {
        winW = window.innerWidth;
        winH = window.innerHeight;
    }

    $.fancybox({
    'type': 'iframe',
    'href': this.href,
    'width': winW,
    'height': winH,
    });

    return false;

});

$('a.account-menu').click(function(){
    
    var account_hidden_div=document.getElementById('account-hidden-div');
    var account=document.getElementById('account');

	$(account_hidden_div).slideToggle('fast', function() {});

    return false;

});


$('a.close-pop').click(function(){
	$.fancybox.close();
	});

$('a.category').click(function() {
	$(this).next('ul').slideToggle('slow', function() {
  });
});

$("a.category").click(function () {

     $(this).toggleClass("open");
     var name = $(this)[0].getAttribute("name");
     var cookie_name = name.replace(/\s/g, "");

     /* console.log(cookie_name); */

     if ($.cookie(cookie_name) == "open") {
        $.cookie(name, "close", {path: '/'}); 
     } else {
        $.cookie(name, "open", {path: '/'}); 
     }
});

