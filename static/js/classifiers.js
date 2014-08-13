// Classifier generator for color coding
function makeSimpleClassifier(higherIsBetter, warnCount, okCount)
{
	var classifier;
	if(higherIsBetter) {
		classifier = function(count) {
			if(count > okCount) {
				return "label-success";
			} else if(count > warnCount) {
				return "label-warning";
			} else {
				return "label-danger";
			}
		}
	} else {
		classifier = function(count) {
			if(count < okCount) {
				return "label-success";
			} else if(count < warnCount) {
				return "label-warning";
			} else {
				return "label-danger";
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
			return "label-danger"
		case "Shell":
		case "Java":
		case "C#":
		case "Scala":
		case "Go":
			return "label-warning"
		case "JavaScript":
		case "Ruby":
		case "PHP":
		case "Python":
		case "Dart":
		case "Lua":
			return "label-success"
		default:
			return 'label-default'
	}
}