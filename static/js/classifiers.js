var GOOD = 1;
var NEUTRAL = 2;
var BAD = 3;
var UNCERTAIN = 4;

rivets.binders.coding = function(el, value) {
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
	}
	$(el).addClass(classToAdd);
}

// Classifier generator for color coding
function makeSimpleClassifier(higherIsBetter, warnCount, okCount)
{
	var classifier;
	if(higherIsBetter) {
		classifier = function(count) {
			if(count > okCount) {
				return GOOD;
			} else if(count > warnCount) {
				return NEUTRAL;
			} else {
				return BAD;
			}
		}
	} else {
		classifier = function(count) {
			if(count < okCount) {
				return GOOD;
			} else if(count < warnCount) {
				return NEUTRAL;
			} else {
				return BAD;
			}
		}
	}
	return classifier;
}

// Classifier instance functions
var starClassifier = makeSimpleClassifier(true, 500, 1000);
var forkClassifier = makeSimpleClassifier(true, 150, 400);
var sizeClassifier = makeSimpleClassifier(false, 500000, 200000);
var dateClassifier = makeSimpleClassifier(false, 60, 30);

// Language classifier
function langClassifier(language) {
	switch (language) {
		case "C":
		case "C++":
		case "Objective-C":
			return BAD;
		case "Shell":
		case "Java":
		case "C#":
		case "Scala":
		case "Go":
			return NEUTRAL;
		case "JavaScript":
		case "Ruby":
		case "PHP":
		case "Python":
		case "Dart":
		case "Lua":
			return GOOD;
		default:
			return UNCERTAIN;
	}
}