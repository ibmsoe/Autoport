rivets.formatters.size = function(value) {
	if(value > 1024) {
		return Math.round(value / 1024) + " MB";
	} else {
		return value + " KB";
	}
}

rivets.formatters.date = function(value) {
	return moment.utc(value).fromNow();
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

	return '<tr id="row-' + index + '">' + 
				'<td>' +
					// Owner
					'<a title="Owner" class="tip" rv-href="entry.owner_url" rv-text="entry.owner"></a>' +
					// Slash seperator
					' / ' +
					// Repo name
					'<a title="Repository" class="tip repo-title" rv-href="entry.url" rv-text="entry.name"></a>' +
					// Star count
					'<span title="Star count" class="tip label" rv-coding="entry.coding.stars">' +
						'<span class="glyphicon glyphicon-star"></span>' +
						'{ entry.stars }' +
					'</span>' +
					// Fork count
					'<span title="Fork count" class="tip label" rv-coding="entry.coding.forks">' +
						'<span class="glyphicon glyphicon-random"></span>' +
						'{ entry.forks }' +
					'</span>' +
					// Langauge
					'<span title="Primary language" class="tip label" rv-coding="entry.coding.language">' +
						'<span class="glyphicon glyphicon-wrench"></span>' +
						'{ entry.language }' +
					'</span>' +
					// Size
					'<span title="Repository size" class="tip label" rv-coding="entry.coding.size">' +
						'<span class="glyphicon glyphicon-floppy-disk"></span>' +
						'{ entry.size_kb | size }' +
					'</span>' +
					// Last updated
					'<span title="Last updated" class="tip label" rv-coding="entry.coding.date">' +
						'<span class="glyphicon glyphicon-calendar"></span>' +
						'updated { entry.last_update | date }' +
					'</span>' +
				'</td>' +
				'<td>' +
				'<button type="button" data-id="' + index + '"class="add-to-jenkins btn btn-primary">' + 
					'<span class="glyphicon glyphicon-save"></span>' + 
					'Add to Jenkins' +
				'</button>' +
			'</td>'
			'</tr>'
}