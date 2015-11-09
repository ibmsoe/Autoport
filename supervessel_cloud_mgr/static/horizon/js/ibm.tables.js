/**
 * Licensed Materials - Property of IBM
 *
 * (c) Copyright IBM Corp. 2014 All Rights Reserved
 *
 * US Government Users Restricted Rights - Use, duplication or
 * disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
 */

/**
 * Process table headers.
 * @param $table The jQuery list of DataTables to process.
 */
function processHeaders($table) {
  if($table.length === 0) {
    return;
  }
  
  // If the column headers do not have the inner div used by the tablesorter,
  // then append an inner div of our own.
  $table.find('thead th:not(.table_header):not(:has(div.tablesorter-header-inner))').each(function() {
    var content = $(this).html();
    $(this).empty().append('<div class="header-inner">' + content + '</div>');
  });
  
  // Add the column divider div to all column headers
  $table.find('thead th:not(.table_header)').prepend('<div class="header-divider"><div></div></div>');
  
  // If there are no table actions then add a class to the table_actions
  // div so we can style it appropriately.
  $table.each(function() {
    var $actions = $(this).find('thead div.table_actions');
    if($actions.find('> *').length === 0) {
      $actions.addClass('no-actions');
    }
  });
}

/**
 * Process table headers after a delay. This is to make sure that all other
 * javascript table processing is done.
 * @param $table The jQuery list of DataTables to process.
 */
function processHeadersDelayed($table) {
  setTimeout(function() {
    processHeaders($table);
  }, 1);
}

horizon.addInitFunction(function() {
  processHeadersDelayed($('div.table_wrapper table.datatable'));
});
horizon.modals.addModalInitFunction(function(modal) {
  processHeadersDelayed($(modal).find('div.table_wrapper table.datatable'));
});
horizon.tabs.addTabLoadFunction(function($tab) {
  processHeadersDelayed($tab.find('div.table_wrapper table.datatable'));
});
