$(document).ready(function() {
    $('.src').addClass("pre-scrollable");

    $('#content').addClass("container-fluid");

    $('h1.title').wrapAll('<div class="row-fluid"/>');
    $('h1.title').wrapAll('<div class="page-header"/>');

    $('#table-of-contents').remove();
    $('#postamble').remove();

    $('.org-dl').addClass('dl-horizontal');
    $('.OPEN').addClass('label label-info');
    $('.IDEA').addClass('label label-info');
    $('.TEST').addClass('label label-important');
    $('.ASSIGNED').addClass('label label-warning');
    $('.DONE').addClass('label label-success');

    $('.tag').addClass('text-right text-info');

    $('.outline-2').wrapAll('<div id="main" class="row-fluid"/>');
    $('.outline-2').wrapAll('<div class="span9"/>');

    $('#main').prepend('<div id="toc"/>');
    $('#toc').wrapAll('<div class="span3"/>');
    $('#toc').tocify({
	context: "#main",
	selectors: "h2,h3",
    });

    $('#toc').affix();

});
