// Takes a size in KB in returns a human readable string
function humanizeSize(size_kb) {
	if(size_kb > 1024) {
		return Math.round(size_kb / 1024) + " MB";
	} else {
		return size_kb + " KB";
	}
}

// Generate action buttons
function generateActions(index) {
	return '<td>' +
				'<button type="button" data-id="' + index + '"class="add-to-jenkins btn btn-primary">' + 
					'<span class="glyphicon glyphicon-save"></span>' + 
					'Add to Jenkins' +
				'</button>' +
			'</td>'
}

// Generates a table row for one repository entry in the result table
function generateRow(entry, index) {
	var now = moment.utc();
	var lastUpdate = moment.utc(entry.last_update);
	var daysBetween = now.diff(lastUpdate, 'days');

	return '<tr>' + 
				'<td>' +
					// Owner
					'<a title="Owner" class="tip" href="' + entry.owner_url + '">' +
						entry.owner +
					'</a>' +
					// Slash seperator
					' / ' +
					// Repo name
					'<a title="Repository" class="tip repo-title" href="' + entry.url + '">' +
						entry.name +
					'</a>' +
					// Star count
					'<span title="Star count" class="tip label ' + starClassifier(entry.stars) + '">' +
						'<span class="glyphicon glyphicon-star"></span>' +
						entry.stars +
					'</span>' +
					// Fork count
					'<span title="Fork count" class="tip label ' + forkClassifier(entry.forks) + '">' +
						'<span class="glyphicon glyphicon-random"></span>' +
						entry.forks +
					'</span>' +
					// Langauge
					'<span title="Primary language" class="tip label ' + langClassifier(entry.language) + '">' +
						'<span class="glyphicon glyphicon-wrench"></span>' +
						entry.language +
					'</span>' +
					// Size
					'<span title="Repository size" class="tip label ' + sizeClassifier(entry.size_kb) + '">' +
						'<span class="glyphicon glyphicon-floppy-disk"></span>' +
						humanizeSize(entry.size_kb) +
					'</span>' +
					// Last updated
					'<span title="Last updated" class="tip label ' + dateClassifier(daysBetween) + '">' +
						'<span class="glyphicon glyphicon-calendar"></span>' +
						'updated ' + lastUpdate.fromNow() +
					'</span>' +
				'</td>' +
				generateActions(index);
			'</tr>'
}