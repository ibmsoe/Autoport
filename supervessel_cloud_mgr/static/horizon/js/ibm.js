/**
 * Licensed Materials - Property of IBM
 *
 * (c) Copyright IBM Corp. 2014 All Rights Reserved
 *
 * US Government Users Restricted Rights - Use, duplication or
 * disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
 */

// Load the configuration strategy template from a local file
// TODO: Using our own way to get the 'csrftoken' cookie until this bug is
// fixed upstream. Otherwise configuration strategy template loading by URL is
// broken. When fixed we will use horizon.cookies.get('csrftoken').
// https://bugs.launchpad.net/horizon/+bug/1358911
function getCookie(key) {
  cookies = document.cookie.split(';');
  for(var i = 0; i < cookies.length; i++) {
    cookie = cookies[i].trim().split('=');
    if(cookie[0] == key) {
      return cookie[1];
    }
  }
  return null;
}

function loadTemplateFromFile($node) {
  removeError('#id_template_url');
  removeError('#id_template_file');
  file = $('#id_template_file').get(0).files[0];
  if(!file) return;
  var reader = new FileReader();
  reader.onload = function(evt) {
    templateCheck(evt.target.result, $node, '#id_template_file');
  };
  reader.readAsText(file);
}

// Load the configuration strategy template from a URL
function loadTemplateFromUrl($node) {
  removeError('#id_template_url');
  removeError('#id_template_file');
  $.ajax({
    url: '/admin/images/load_template/',
    dataType: 'JSON',
    type: 'POST',
    data: {
      template_url: $('#id_template_url').val(),
      // TODO: Using getCookie() until the bug upstream is fixed. See comments
      // on getCookie() function above.
      csrfmiddlewaretoken: getCookie('csrftoken')
    },
    cache: false
  }).done(function(response) {
    if(!response.error) {
      templateCheck(response.data, $node, '#id_template_url');
    }
    else {
      showError('#id_template_url', response.error);
    }
  }).fail(function(xhr) {
    showError('#id_template_url', gettext('There was a problem communicating with the server. Make sure the URL is correct and try again.'));
  });
}

// Remove the error from the given field
function removeError(fieldId) {
  $group = $(fieldId).closest('.form-group');
  $group.find('.help-block').remove();
  $group.removeClass('has-error');
}

// Show the given field as having an error
function showError(fieldId, message) {
  if(!fieldId) {
    console.error(message);
    return;
  }
  removeError(fieldId);
  errorNode = $('<span class="help-block alert alert-danger">' + horizon.escape_html(message) + '</span>');
  $group = $(fieldId).closest('.form-group');
  $group.find('input').after(errorNode);
  $group.addClass('has-error');
}

// Check if the template is an XML template or a JSON config strategy file.
function templateCheck(xmlOrJson, $node, fieldId) {
  xmlOrJson = xmlOrJson.trim();
  if(xmlOrJson[0] == '{') {
    try {
      var configStrategy = JSON.parse(xmlOrJson);
      var template = configStrategy.properties.metadata_template;
      var mapping = configStrategy.properties.mapping;
      parseTemplate(template, $node, fieldId, mapping);
    }
    catch(e) {
      showError(fieldId, gettext('There was an error parsing the configuration strategy JSON file. Make sure the file contains well formed JSON.'));
    }
  }
  else if(xmlOrJson[0] == '<') {
    parseTemplate(xmlOrJson, $node, fieldId);
  }
  else {
    showError(fieldId, gettext('The file must be either an XML or JSON file.'));
  }
}

// Parse the configuration strategy template
function parseTemplate(template, $node, fieldId, mapping) {
  var props;
  try {
    $xml = $($.parseXML(template));
    if($xml.find('ovf\\:Envelope, Envelope').length) {
      $('#id_template_type').val('ovf');
      $('#id_template').val(template);
      props = parseOvf($xml);
    }
    else if($xml.find('unattend').length) {
      $('#id_template_type').val('sysprep');
      $('#id_template').val(template);
      props = parseSysprep($xml);
    }
    else {
      showError(fieldId, gettext('There was an error parsing the template file. Make sure the file is either an OVF template or an unattend XML file.'));
    }
  }
  catch(error) {
    showError(fieldId, gettext('There was an error parsing the template file. Make sure the file contains well formed XML.'));
  }

  displayConfigStrategyProps(props, $node, mapping);
}

// Parse the given OVF template document
function parseOvf($xml) {
  var map = {};
  $xml.find('ovf\\:Property, Property[ovf\\:userConfigurable="true"]').each(function() {
    var $prop = $(this);
    var $section = $prop.closest('ovf\\:ProductSection, ProductSection');
    var sectionLabel = $section.find('ovf\\:Info, Info').text();
    var key = $section.attr('ovf:class') + '.' + $prop.attr('ovf:key');
    var propLabel = $prop.find('ovf\\:Label, Label').text();
    var propDescription = $prop.find('ovf\\:Description, Description').text();
    if(!map[sectionLabel]) {
      map[sectionLabel] = [];
    }
    map[sectionLabel].push({key: key, label: propLabel, description: propDescription});
  });
  return map;
}

// Parse the given SYSPREP template document
function parseSysprep($xml) {
  var map = {};
  var ns = $xml.find('unattend').attr('xmlns');
  var sep = ' : ';
  function generateTargets(index, node) {
    if(node.childNodes.length == 1 && node.childNodes[0].nodeType == 3) {
      $node = $(node);
      var propLabel = $node.prop('tagName');
      var parent = $node.parent();
      var sectionLabel = null;
      var target = '/{' + ns + '}' + propLabel;
      while(parent.prop('tagName') != 'unattend') {
        var parentTag = parent.prop('tagName');
        if(parentTag == 'component') {
          sectionLabel = parent.attr('name');
        }
        if(!sectionLabel) {
          propLabel = parentTag + sep + propLabel;
        }
        target = '/{' + ns + '}' + parentTag + target;
        parent = parent.parent();
      }
      target = '/{' + ns + '}unattend' + target;
      if(!map[sectionLabel]) {
        map[sectionLabel] = [];
      }
      map[sectionLabel].push({key: target, label: propLabel});
    }
    else {
      $.each(node.childNodes, generateTargets);
    }
  }
  generateTargets(0, $xml[0]);
  return map;
}

// Get the source property from the mapping using the given target property
function getMappedSourceProperty(mapping, target) {
  for(var i = 0; i < mapping.length; i++) {
    if(mapping[i].target == target) {
      return mapping[i].source;
    }
  }
  return '';
}

function displayConfigStrategyProps(layout, $node, mapping) {
  $('#id_template_file').closest('.form-group').nextAll().remove();
  for(var label in layout) {
    var props = layout[label];
    $node.append($('<h4>' + horizon.escape_html(label) + '</h4>'));
    for(var i = 0; i < props.length; i++) {
      var p = props[i];
      var value = '';
      if(mapping) {
        value = getMappedSourceProperty(mapping, p.key);
      }
      var help = '';
      if(p.description) {
        help = '<span class="help-icon" data-toggle="tooltip" data-placement="top" title="" data-original-title="' + horizon.escape_html(p.description) + '">' +
            '<span class="glyphicon glyphicon-question-sign"></span></span>';
      }
      $node.append($('<div class="form-group form-field clearfix config-strategy-prop">' +
          '<label for="' + horizon.escape_html(p.key) + '">' + horizon.escape_html(p.label) + '</label> ' + help +
          '<div>' +
          '<input id="' + horizon.escape_html(p.key) + '" maxlength="255" type="text" class="form-control mapping" value="' + value + '">' +
          '</div>'));
    }
  }

  // Update the mapping field when submitting the form
  $node.closest('form').on('submit', function() {
    setMapping($node);
    return true;
  });
}

// Set the configuration strategy mapping
function setMapping($node) {
  var mapping = [];
  $node.find('.mapping').each(function() {
    $prop = $(this);
    if($prop.val()) {
      mapping.push({
        source: $prop.val(),
        target: $prop.attr('id')
      });
    }
  });
  $('#id_mapping').val(JSON.stringify(mapping));
}

// Feature detection to see if we can read the content of a local file
function canReadLocalFile() {
  return typeof File !== 'undefined' && typeof FileReader !== 'undefined';
}

// Scroll the given node into view
function scrollIntoView($node) {
  var offset = $node.offset();
  // Firefox seems to need a small timeout otherwise this doesn't work
  setTimeout(function() {
    $('html, body').scrollTop(offset.top);
  }, 20);
}

// Initialize the configuration strategy fields
function initConfigStrategyForm() {
  var $imageForm = $('#create_image_form, #update_image_form');
  if(!$imageForm.length) {
    return;
  }

  // Create the collapsible Configuration Strategy section
  var $fieldset = $('#id_template_source_type').closest('fieldset');
  var $configStrategyFields = $('#id_template_source_type').closest('.form-group').prev().nextAll();
  var $heading = $('<a href="#" id="config-strategy-heading"><span class="arrow">&#9658</span> <h4>' + gettext('Configuration Strategy') + '</h4></a>');
  $fieldset.append($heading);
  var $pane = $('<div id="config-strategy-pane" style="display: none;"></div>');
  $fieldset.append($pane);
  var $help = $('<div id="config-strategy-help"><h4>' + gettext('Configuration Strategy') + '</h4><p>' + gettext('The configuration strategy allows you to use either an OVF or Sysprep template to provide configuration properties to the image when it is booted. Use this section to enter the source property names to map to the target properties from the template. The source properties can be OpenStack provided properties or come from the server metadata.') + '</p><p>' + gettext('You can choose to load an OVF template file, an unattend XML template file, or a configuration strategy JSON file.') + '</div>');
  $pane.closest('.left').next().append($help);
  $pane.append($configStrategyFields);
  $heading.on('click', function() {
    var $pane = $('#config-strategy-pane');
    if($pane.css('display') == 'none') {
      $pane.css('display', '');
      $('#config-strategy-heading .arrow').html('&#9660');
      $('#id_template_source_type').change();
      scrollIntoView($heading);
    }
    else {
      $pane.css('display', 'none');
      $('#config-strategy-heading .arrow').html('&#9658');
    }
  });

  // Add the Load Template button
  var $button = $('<a href="#" id="load_template_btn" class="btn btn-default btn-sm">' + gettext('Load') + '</a>');
  $button.on('click', function() {
    $button.attr('disabled', true).addClass('disabled');
    loadTemplateFromUrl($pane);
    $('#id_template_file').val('');
    $button.attr('disabled', false).removeClass('disabled');
    scrollIntoView($('#config-strategy-heading'));
  });
  $('#id_template_url').closest('div').append($button);

  // Parse local file after selecting
  $('#id_template_file').on('change', function() {
    loadTemplateFromFile($pane);
    scrollIntoView($('#config-strategy-heading'));
  });

  // Disable the Local File option for loading the configuration strategy
  // template if the browser does not support reading a local file.
  if(!canReadLocalFile()) {
    $('#id_template_source_type').val('template-url').change().attr('disabled', true);
  }

  // If a template file already exists then we need to parse it and display
  // the fields along with any existing mapping. This happens on the Update
  // Image page and when submitting the Create Image page with errors.
  var templateFile = $('#id_template').val();
  if(templateFile) {
    var mapping = $('#id_mapping').val();
    if(mapping) {
      mapping = JSON.parse(mapping);
    }
    var fieldId = '#id_template_file';
    if($('#id_template_source_type').val() == 'template-url') {
      fieldId = '#id_template_url';
    }
    parseTemplate(templateFile, $pane, fieldId, mapping);
  }
}

horizon.modals.addModalInitFunction(function (modal) {
  initConfigStrategyForm();
});
horizon.addInitFunction(function() {
  initConfigStrategyForm();
})