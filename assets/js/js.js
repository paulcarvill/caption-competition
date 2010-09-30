// TODO: add permalink to each caption

var paginator = {
	
	init : function(){
		this.captionList = $('#captionlist');
		this.captionListInner = $('#captionListInner');
		this.removeClassesForStyling();
		this.addClassesToStylePaginatedCaptions();

		this.currentCaption = 1;
		this.totalCaptions = this.getTotalNumberOfCaptions();
		
		if(this.totalCaptions > 1){
			this.addNavigationControls();
		}
		var span = $('#more a span');
		this.comp = span.attr('id');
		this.page = span.text();
		$('#more').remove();
		
		this.showPagination = false;
		if(this.pagination()) {
			this.showPagination = true;
		}
	},
	
	removeClassesForStyling : function(){
		this.captionListInner.attr('id', '');
	},
	
	addClassesToStylePaginatedCaptions : function(){
		this.captionList.addClass('captionList');
		this.captionListInner.addClass('captionListInner');
	},
	
	getTotalNumberOfCaptions : function(){
		return this.captionListInner.children().length;
	},
	
	pagination : function(){
		var pagination = $('#more');
		return pagination.length;
	},
	
	addNavigationControls : function(){
		this.next = $('<p id="next">Next</p>').click(this.getNextPage);
		this.counter = $('<p id="counter">'+this.currentCaption+' of '+this.totalCaptions+'</p>');
		this.captionList.after(this.next).after(this.counter);
	},
	
	addBackButton : function(){
		this.back = $('<p id="back">Back</p>').click(this.getPreviousPage);
		this.counter.css('margin-left', '0');
		this.captionList.after(this.next).after(this.counter).after(this.back);
	},
	
	updateBackButton : function(){
		if(paginator.currentCaption > 1){
			if(!this.back){
				this.addBackButton();
			}
			else {
				paginator.back.css('visibility', 'visible');
			}
		}
		else {
			paginator.back.css('visibility', 'hidden');
		}
	},
	
	updateNextButton : function(){
		if(paginator.currentCaption == paginator.totalCaptions){
			paginator.next.hide();
		}
		else {
			paginator.next.show();
		}
	},
	
	updateMoreLink : function(){
		if(paginator.moreLink) {
			paginator.moreLink.is(':visible') ? paginator.moreLink.hide() : paginator.moreLink.show();
		}
	},
	
	updateCounter : function(){
		paginator.counter.html('<p>'+paginator.currentCaption+' of '+paginator.totalCaptions+'</p>');
	},
	
	getNextPage : function(){
		if(paginator.currentCaption < paginator.totalCaptions) {
			paginator.currentCaption++;
			paginator.updateBackButton();
			paginator.updateNextButton();
			paginator.updateCounter();
			paginator.animateUp();	
		}
		paginator.updateMoreLink();
		if(paginator.showPagination && paginator.currentCaption == paginator.totalCaptions){
			paginator.showMoreLink()
		}
	},
	
	getPreviousPage : function(){
		if(paginator.currentCaption > 1) {
			paginator.currentCaption--;
			paginator.updateBackButton();
			paginator.updateNextButton();
			paginator.updateCounter();
			paginator.animateDown();	
		}
		paginator.updateMoreLink();
	},
	
	animateUp : function(){
		paginator.captionListInner.animate({
			'left' : "-=437px"
		});	
	},
	
	animateDown : function(){
		paginator.captionListInner.animate({
			'left' : "+=437px"
		})
	},
	
	showMoreLink : function(){
		if($('#more').length == 0){
			paginator.moreLink = $('<p id="more">load more...</p>');
			paginator.moreLink.click(paginator.getMoreCaptions);
			paginator.counter.after(paginator.moreLink);
		}
	},
	
	getMoreCaptions : function(){
		$.getJSON('/competitions/'+paginator.comp+'/page/'+paginator.page+'/json', paginator.callback, 'json');
	},
	
	callback : function(response){
		if(response[1] == false){
			paginator.showPagination = false;
		}
		paginator.moreLink.remove();
		$(response[0]).each(function(){
			paginator.captionListInner.append('<li><p>'+this.text+'</p><p></p><p>'+this.author+'</p></li>')
		})
		paginator.setTotalCaptions(paginator.totalCaptions + response[0].length);
		paginator.incrementCurrentCaption();
		paginator.updateCounter();
		paginator.setPaginatorWidth();
		paginator.animateUp();
		paginator.updateNextButton();
	},
	
	setPaginatorWidth : function(){
		paginator.captionListInner.css( { 'width' : 437*paginator.totalCaptions+'px' } );
	},
	
	setTotalCaptions : function(newTotal){
		paginator.totalCaptions = newTotal;
	},
	
	incrementCurrentCaption : function(){
		paginator.currentCaption++;
	}
	
}


$(function(){
	paginator.init()
});