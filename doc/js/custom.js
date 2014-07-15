$(document).ready(function() {
    $('.src').addClass("pre-scrollable");

    $('#content').addClass("container").attr("role", "main");
    var title = $("h1.title").text();

    $('h1.title').wrapAll('<div id="nb" class="navbar navbar-inverse navbar-fixed-top" role="navigation"/>');
    $('h1.title').wrapAll('<div class="container"/>');
    $('h1.title').wrapAll('<div class="navbar-header"/>');
    $("h1.title").replaceWith('<a class="navbar-brand" href="#">' + $("h1.title").text() + "</a>");

    $('#table-of-contents h2').remove();

    var navtoc = $('#text-table-of-contents').clone();
    var toc = $('#text-table-of-contents').clone();

    navtoc.appendTo("#nb .container");
    navtoc.addClass("collapse navbar-collapse");
    navtoc.find("ul").addClass("nav navbar-nav");
    navtoc.find("ul > li > ul").remove();

    toc.attr("id", "content-toc");
    toc.prependTo("#content");

    $('#content').prepend('<div class="page-header"><h1>' + title + '</h1></div>');

    $('#table-of-contents').remove();

    $('#nb').prependTo("body");

    $('#postamble').remove();

    $('.org-dl').addClass('dl-horizontal');

    $('h2').addClass('page-header');

    $('.TODO').addClass('label label-info');
    $('.OPEN').addClass('label label-info');
    $('.IDEA').addClass('label label-info');
    $('.TEST').addClass('label label-important');
    $('.ASSIGNED').addClass('label label-warning');
    $('.DONE').addClass('label label-success');

    $('.tag').addClass('muted');

    $('table').addClass('table');
    $('img').addClass('img-responsive');



    // https://gist.github.com/ivos/4055810
    if($(document).width()>979){  // Required if "viewport" content is "width=device-width, initial-scale=1.0": navbar is not fixed on lower widths.

	var hash = window.location.hash;

	// Code below fixes the issue if you land directly onto a page section (http://domain/page.html#section1)

	if(hash!=""){
	    $(document).scrollTop(($(hash).offset().top) - $(".navbar-fixed-top").height());
	}

	// Here's the fix, if any <a> element points to a page section an offset function is called

	var locationHref = window.location.protocol + '//' + window.location.host + $(window.location).attr('pathname');
	var anchorsList = $('a').get();

	for(i=0;i<anchorsList.length;i++){
	    var hash = anchorsList[i].href.replace(locationHref,'');
	    if (hash[0] == "#" && hash != "#"){
		var originalOnClick = anchorsList[i].onclick; // Retain your pre-defined onClick functions
		setNewOnClick(originalOnClick,hash);
	    }
	}
    }

    function setNewOnClick(originalOnClick,hash){
	anchorsList[i].onclick=function(){
	    $(originalOnClick);
	    $(document).scrollTop(($(hash).offset().top) - $(".navbar-fixed-top").height());
	    return false;
	};
    }
});
