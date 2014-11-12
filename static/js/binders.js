// Rivets.js binders
// rv-classification binder
rivets.binders.classification = function(el, value) {
	// Classification constants
	var GOOD = 1;
	var NEUTRAL = 2;
	var BAD = 3;
	var UNCERTAIN = 4;

	var classToAdd;
	switch(value) {
		case GOOD:
			classToAdd = "label-success";
			break;
		case NEUTRAL:
			classToAdd = "label-warning";
			break;
		case BAD:
			classToAdd = "label-danger";
			break;
		default:
			classToAdd = "label-default";
            break;
	}
	$(el).removeClass("label-success label-warning label-danger label-default");
	$(el).addClass(classToAdd);
};

