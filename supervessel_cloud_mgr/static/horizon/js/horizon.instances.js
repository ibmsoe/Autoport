horizon.instances = {
  user_decided_length: false,
  networks_selected: [],
  networks_available: [],

  getConsoleLog: function(via_user_submit) {
    var form_element = $("#tail_length"),
      data;

    if (!via_user_submit) {
      via_user_submit = false;
    }

    if(this.user_decided_length) {
      data = $(form_element).serialize();
    } else {
      data = "length=35";
    }

    $.ajax({
      url: $(form_element).attr('action'),
      data: data,
      method: 'get',
      success: function(response_body) {
        $('pre.logs').text(response_body);
      },
      error: function(response) {
        if(via_user_submit) {
          horizon.clearErrorMessages();
          horizon.alert('error', gettext('There was a problem communicating with the server, please try again.'));
        }
      }
    });
  },

  /*
   * Gets the html select element associated with a given
   * network id for network_id.
   **/
  get_network_element: function(network_id) {
    return $('li > label[for^="id_network_' + network_id + '"]');
  },

  /*
   * Initializes an associative array of lists of the current
   * networks.
   **/
  init_network_list: function () {
    horizon.instances.networks_selected = [];
    horizon.instances.networks_available = [];
    $(this.get_network_element("")).each(function () {
      var $this = $(this);
      var $input = $this.children("input");
      var name = horizon.escape_html($this.text().replace(/^\s+/, ""));
      var network_property = {
        "name": name,
        "id": $input.attr("id"),
        "value": $input.attr("value")
      };
      if ($input.is(":checked")) {
        horizon.instances.networks_selected.push(network_property);
      } else {
        horizon.instances.networks_available.push(network_property);
      }
    });
  },

  /*
   * Generates the HTML structure for a network that will be displayed
   * as a list item in the network list.
   **/
  generate_network_element: function(name, id, value) {
    var $li = $('<li>');
    $li.attr('name', value).html(name + '<em class="network_id">(' + value + ')</em><a href="#" class="btn btn-primary"></a>');
    return $li;
  },

  /*
   * Generates the HTML structure for the Network List.
   **/
  generate_networklist_html: function() {
    var self = this;
    var updateForm = function() {
      var lists = $("#networkListId li").attr('data-index',100);
      var active_networks = $("#selected_network > li").map(function(){
        return $(this).attr("name");
      });
      $("#networkListId input:checkbox").removeAttr('checked');
      active_networks.each(function(index, value){
        $("#networkListId input:checkbox[value=" + value + "]")
          .prop('checked', true)
          .parents("li").attr('data-index',index);
      });
      $("#networkListId ul").html(
        lists.sort(function(a,b){
          if( $(a).data("index") < $(b).data("index")) { return -1; }
          if( $(a).data("index") > $(b).data("index")) { return 1; }
          return 0;
        })
      );
    };
    $("#networkListSortContainer").show();
    $("#networkListIdContainer").hide();
    self.init_network_list();
    // Make sure we don't duplicate the networks in the list
    $("#available_network").empty();
    $.each(self.networks_available, function(index, value){
      $("#available_network").append(self.generate_network_element(value.name, value.id, value.value));
    });
    // Make sure we don't duplicate the networks in the list
    $("#selected_network").empty();
    $.each(self.networks_selected, function(index, value){
      $("#selected_network").append(self.generate_network_element(value.name, value.id, value.value));
    });
    // $(".networklist > li").click(function(){
    //   $(this).toggleClass("ui-selected");
    // });
    $(".networklist > li > a.btn").click(function(e){
      var $this = $(this);
      e.preventDefault();
      e.stopPropagation();
      if($this.parents("ul#available_network").length > 0) {
        $this.parent().appendTo($("#selected_network"));
      } else if ($this.parents("ul#selected_network").length > 0) {
        $this.parent().appendTo($("#available_network"));
      }
      updateForm();
    });
    if ($("#networkListId > div.form-group.error").length > 0) {
      var errortext = $("#networkListId > div.form-group.error").find("span.help-block").text();
      $("#selected_network_label").before($('<div class="dynamic-error">').html(errortext));
    }
    $(".networklist").sortable({
      connectWith: "ul.networklist",
      placeholder: "ui-state-highlight",
      distance: 5,
      start:function(e,info){
        $("#selected_network").addClass("dragging");
      },
      stop:function(e,info){
        $("#selected_network").removeClass("dragging");
        updateForm();
      }
    }).disableSelection();
  },

  workflow_init: function(modal) {
    // Initialise the drag and drop network list
    horizon.instances.generate_networklist_html();
  }
};

horizon.addInitFunction(function () {
  $(document).on('submit', '#tail_length', function (evt) {
    horizon.instances.user_decided_length = true;
    horizon.instances.getConsoleLog(true);
    evt.preventDefault();
  });

  /* Launch instance workflow */

  // Handle field toggles for the Launch Instance source type field
  function update_launch_source_displayed_fields (field) {
    var $this = $(field),
      base_type = $this.val();
    var use_accelerator_radios = document.getElementsByName('use_accelerator');

    $this.closest(".form-group").nextAll().hide();
    //$(".well-sm").hide();
    $("#flavor_info").hide();
    $("#flavor_status").hide();
    $("#selected_accelerator").hide();

    $("input:checkbox[name=use_accelerator]").removeAttr("checked");
    init_choice_status();
    switch(base_type) {
        case "kvm":
        case "docker":
          $("#id_image_id, #id_use_accelerator, #id_sys_type, #id_architecture, #id_flavor").closest(".form-group").show();
          //$(".well-sm").show();
          $("#flavor_info").show();
          $("#flavor_status").show();
          $("input:radio[name=use_accelerator]").removeAttr("checked");
          $("input:radio[name=use_accelerator]").removeAttr("disabled");
          use_accelerator_radios[0].checked = true;
            if (base_type == "kvm") {
              for (var i = 0; i< use_accelerator_radios.length;  i++) {
                if (use_accelerator_radios[i].value == 'gpu') {
                  use_accelerator_radios[i].disabled = true;
                }
              }
            }
          init_accelerator_type();
          set_default_options();
          update_image_choice();
          update_flavor_choice();
        break;

      case "instance_snapshot_id":
        $("#id_instance_snapshot_id").closest(".form-group").show();
          if (document.getElementById("id_instance_snapshot_id").value) {
            $("#id_flavor").closest(".form-group").show();
          }
        update_flavor_use_snapshot();
          //$(".well-sm").show();
        $("#flavor_info").show();
        $("#flavor_status").show();
        break;

      case "volume_id":
        $("#id_volume_id, #id_delete_on_terminate").closest(".form-group").show();
        break;

      case "volume_image_id":
        $("#id_image_id, #id_volume_size, #id_device_name, #id_delete_on_terminate")
          .closest(".form-group").show();
        break;

      case "volume_snapshot_id":
        $("#id_volume_snapshot_id, #id_device_name, #id_delete_on_terminate")
          .closest(".form-group").show();
        break;
    }
  }

  function init_accelerator_type() {
    var base_type = $(".workflow #id_source_type").val();
    var radios = document.getElementsByName('accelerator_type');
    var use_accelerator_choice = $("input:radio[name=use_accelerator]:checked").val();
    if (base_type == "kvm") {
      for (var i = 0; i< radios.length;  i++) {
        if (radios[i].value != "pcie") {
          radios[i].disabled = true;
        } else {
          radios[i].checked = true;
        }
      }
    } else {
      for (var i = 0; i< radios.length;  i++) {
        if (radios[i].value != "capi") {
          radios[i].disabled = true;
        } else {
          radios[i].checked = true;
        }
      }
    }
    init_sys_architecture_for_acc(use_accelerator_choice);
  }

  function init_choice_status() {
    $("input:radio[name=accelerator_type]").removeAttr("checked");
    $("input:radio[name=accelerator_type]").removeAttr("disabled");
    $("input:checkbox[name=accelerator]").removeAttr("checked");
    $("input:radio[name=capi]").removeAttr("checked");
    $("input:radio[name=sys_type]").removeAttr("disabled");
    $("input:radio[name=architecture]").removeAttr("disabled");
    $("#selected_accelerator_content").html("");
  }

  function set_default_options() {
    var radios = document.getElementsByName('sys_type');
    for (var i = 0; i< radios.length;  i++){
      if (radios[i].disabled == false) {
        radios[i].checked = true;
        break;
      }
    }
    var architecture_radios = document.getElementsByName('architecture');
    for (var i=0; i<architecture_radios.length; i++) {
      if (architecture_radios[i].disabled == false) {
        architecture_radios[i].checked = true;
        break;
      }
    }
  }

  $(document).on('mouseover', '.accelerator_hover', function (evt) {
    var input_obj = $(this).parent().prev();
    var json_str = input_obj.val().replace(/u'/g, "'");
    var json_obj = eval('('+json_str+')');
    $("#acc_name").html(json_obj.name);
    $.get(
        horizon.conf.web_root+'/get_accelerator_info?image_id='+json_obj.id,
        function(data) {
          $("#chip_vendor").html(data.chip_vendor);
          $("#chip_sn").html(data.chip_sn);
          $("#acc_blue_points").html(data.points);
          $("#acc_desc").html(data.acc_desc);
        }
    );
  });

  function check_capi(image_id) {
    $.get(
        horizon.conf.web_root+'/check_capi?image_id='+image_id,
        function (data) {
          var radios = document.getElementsByName('accelerator_type');
          if (!data.status_ok) {
            for (var i = 0; i < radios.length; i++) {
              if (radios[i].value == 'capi') {
                radios[i].disabled = true;
              }
            }
            $("#capi_error").html(gettext("All CAPI resource is being used by other users."));
            var time_message = "Please wait " + data.time;
            $("#capi_error").append(gettext(time_message));
            $("input[type=submit]").attr('disabled','disabled');
          } else {
            for (var i = 0; i < radios.length; i++) {
              if (radios[i].value == 'capi') {
                radios[i].disabled = false;
              }
            }
            $("#capi_error").html("");
            $("input[type=submit]").removeAttr('disabled');
          }
        }
    );
  }

  function initial_for_accelerator() {
    init_choice_status();
    $("#id_accelerator_type").closest(".form-group").hide();
    $("#id_accelerator").closest(".form-group").hide();
    $("#id_capi").closest(".form-group").hide();
    $("#selected_accelerator").hide();
    $("#capi_error").html("");
  }

  function enable_one_choice_for_raidos(radios, radio_name) {
    var radios = document.getElementsByName(radios);
    for (var i = 0; i< radios.length;  i++){
      if (radios[i].value != radio_name) {
        radios[i].disabled = true;
      } else {
        radios[i].checked = true;
      }
    }
  }

  $(document).on('change', '.workflow #id_use_accelerator', function (evt) {
    var use_accelerator_choice = $("input:radio[name=use_accelerator]:checked").val();
    initial_for_accelerator();
    if (use_accelerator_choice == 'fpga') {
      init_accelerator_type();
      $("#id_accelerator_type").closest(".form-group").show();
      var base_type = $(".workflow #id_source_type").val();
      //if (base_type == "docker") {
      //  check_capi();
      //}
    } else if (use_accelerator_choice == 'gpu') {
      $("#id_accelerator_type").closest(".form-group").show();
      enable_one_choice_for_raidos('accelerator_type', 'pcie');
      enable_one_choice_for_raidos('sys_type', 'ubuntu');
      enable_one_choice_for_raidos('architecture', 'ppc64le');
    }
    update_image_choice();
    $("input[type=submit]").removeAttr('disabled');
  });

  $(document).on('change', '.workflow #id_capi', function (evt) {
    var capi_choice = $("input:radio[name=capi]:checked").val();
    var json_str = capi_choice.replace(/u'/g, "'");
    var json_obj = eval('('+json_str+')');
    check_capi(json_obj.id);
    console.log('after check capi');
  });

  function init_sys_architecture_for_acc(use_accelerator_choice) {
    var accelerator_type = $("input:radio[name=accelerator_type]:checked").val();
    if (use_accelerator_choice == 'fpga') {
      switch (accelerator_type) {
        case 'capi':
          $("#id_capi").closest(".form-group").show();
          $("#selected_accelerator").show();
          enable_one_choice_for_raidos('sys_type', 'ubuntu');
          enable_one_choice_for_raidos('architecture', 'ppc64le');
          break;
        case 'pcie':
          $("#id_accelerator").closest(".form-group").show();
          $("#selected_accelerator").show();
          enable_one_choice_for_raidos('sys_type', 'rhel');
          enable_one_choice_for_raidos('architecture', 'ppc64');
          break;
      }
    } else if (use_accelerator_choice == 'gpu') {
      switch (accelerator_type) {
        case 'pcie':
          enable_one_choice_for_raidos('sys_type', 'ubuntu');
          enable_one_choice_for_raidos('architecture', 'ppc64le');
          break;
      }
    }
  }

  $(document).on('change', '.workflow #id_accelerator_type', function (evt) {
    var use_accelerator_choice = $("input:radio[name=use_accelerator]:checked").val();
    $("input:radio[name=sys_type]").removeAttr("disabled");
    $("input:radio[name=architecture]").removeAttr("disabled");
    $("input:radio[name=sys_type]").removeAttr("checked");
    $("input:radio[name=architecture]").removeAttr("checked");
    set_default_options();
    init_sys_architecture_for_acc(use_accelerator_choice);
    update_image_choice();
  });

  $(document).on('change', '.workflow #id_source_type', function (evt) {
    update_launch_source_displayed_fields(this);
  });

  $('.workflow #id_source_type').change();
  horizon.modals.addModalInitFunction(function (modal) {
    $(modal).find("#id_source_type").change();
  });

  function update_image_choice() {
    var source_type = $(".workflow #id_source_type").val();
    var sys_type = $('input:radio[name=sys_type]:checked').val();
    var architecture = $('input:radio[name=architecture]:checked').val();
    var accelerator_type = $('input:radio[name=accelerator_type]:checked').val();
    var use_accelerator_choice = $('input:radio[name=use_accelerator]:checked').val();
    var images_choice_field = "#id_image_id";
    var loadingContent = layer.load(1, {
      shade: [0.1,'#fff'] //0.1透明度的白色背景
    });
    jQuery(images_choice_field).empty();
    jQuery(images_choice_field).prepend("<option value='1'>"+gettext('Loading Image ...')+"</option>");
    if (use_accelerator_choice != '') {
      var tmp_accelerator_type = accelerator_type;
      accelerator_type = use_accelerator_choice + '_' + tmp_accelerator_type;
    } else {
      accelerator_type = 'none';
    }
    //if (accelerator_type == 'undefined_undefined') {
    //  accelerator_type = 'none';
    //}
    if (accelerator_type.indexOf('undefined') == 0) {
      accelerator_type = 'none';
    }
    $.get(
        horizon.conf.web_root+'/image_list?hypervisor_type='+source_type+'&sys_type='+sys_type+'&architecture='+architecture+'&accelerator_type='+accelerator_type+'&accelerator_choice='+use_accelerator_choice,
        function(data) {
          jQuery(images_choice_field).empty();
          for (var i= 0, length=data.image_list.length; i<length; i++) {
            jQuery(images_choice_field).append("<option value='"+data.image_list[i][0]+"'>"+data.image_list[i][1]+"</option>");
          }
          if (data.image_list.length == 0) {
            jQuery(images_choice_field).prepend("<option value='1'>"+gettext('No available image found')+"</option>")
          }
          layer.close(loadingContent);
        }
    );
  }

    function update_flavor_choice() {
      var source_type = $(".workflow #id_source_type").val();
      var flavors_choice_field = "#id_flavor";
      jQuery(flavors_choice_field).empty();
      jQuery(flavors_choice_field).prepend("<option value='1'>" + gettext('Loading Flavor ...') + "</option>");
      $.get(
          horizon.conf.web_root+'/flavor_list?source_type=' + source_type,
          function (data) {
            jQuery(flavors_choice_field).empty();
            for (var i = 0, length = data.flavor_list.length; i < length; i++) {
              jQuery(flavors_choice_field).append("<option value='" + data.flavor_list[i][0] + "'>" + data.flavor_list[i][1] + "</option>");
            }
            if (data.flavor_list.length == 0) {
              jQuery(flavors_choice_field).prepend("<option value='1'>" + gettext('No available flavor found') + "</option>")
            }
            horizon.Quota.showFlavorDetails();
            horizon.Quota.disableFlavorsForImage();
          }
      )
    }

    function update_flavor_use_snapshot() {
      var image_id = $('#id_instance_snapshot_id option:selected').val();
      var flavors_choice_field = "#id_flavor";
      jQuery(flavors_choice_field).empty();
      jQuery(flavors_choice_field).prepend("<option value='1'>" + gettext('Loading Flavor ...') + "</option>");
      $.get(
          horizon.conf.web_root+'/flavor_list?image_id=' + image_id,
          function (data) {
            jQuery(flavors_choice_field).empty();
            for (var i = 0, length = data.flavor_list.length; i < length; i++) {
              jQuery(flavors_choice_field).append("<option value='" + data.flavor_list[i][0] + "'>" + data.flavor_list[i][1] + "</option>");
            }
            if (data.flavor_list.length == 0) {
              jQuery(flavors_choice_field).prepend("<option value='1'>" + gettext('No available flavor found') + "</option>")
            }
            horizon.Quota.showFlavorDetails();
          }
      )
    }

    $(document).on('change', '.workflow #id_sys_type', function (evt) {
        update_image_choice();
    });

    $(document).on('change', '.workflow #id_instance_snapshot_id', function (evt) {
      if (this.value) {
        $("#id_flavor").closest(".form-group").show();
        update_flavor_use_snapshot();
      } else {
        $("#id_flavor").closest(".form-group").hide();
      }
    });

    $(document).on('change', '.workflow #id_architecture', function (evt) {
        update_image_choice();
    });

  /*
   Update the device size value to reflect minimum allowed
   for selected image and flavor
   */
  function update_device_size() {
    var volume_size = horizon.Quota.getSelectedFlavor().disk;
    var image = horizon.Quota.getSelectedImage();

    if(image !== undefined) {
      if(image.min_disk > volume_size) {
        volume_size = image.min_disk;
      }
    }

    // Make sure the new value is >= the minimum allowed (1GB)
    if(volume_size < 1) {
      volume_size = 1;
    }

    $("#id_volume_size").val(volume_size);
  }

  $(document).on('change', '.workflow #id_flavor', function (evt) {
    update_device_size();
  });

  $(document).on('change', '.workflow #id_image_id', function (evt) {
    update_device_size();
  });

  horizon.instances.decrypt_password = function(encrypted_password, private_key) {
    var crypt = new JSEncrypt();
    crypt.setKey(private_key);
    return crypt.decrypt(encrypted_password);
  };

  $(document).on('change', '#id_private_key_file', function (evt) {
    var file = evt.target.files[0];
    var reader = new FileReader();
    if (file) {
      reader.onloadend = function(event) {
        $("#id_private_key").val(event.target.result);
      };
      reader.onerror = function(event) {
        horizon.clearErrorMessages();
        horizon.alert('error', gettext('Could not read the file'));
      };
      reader.readAsText(file);
    }
    else {
      horizon.clearErrorMessages();
      horizon.alert('error', gettext('Could not decrypt the password'));
    }
  });
  /*
    The font-family is changed because with the default policy the major I
    and minor the l cannot be distinguished.
  */
  $(document).on('show', '#password_instance_modal', function (evt) {
    $("#id_decrypted_password").css("font-family","monospace");
    $("#id_decrypted_password").css("cursor","text");
    $("#id_encrypted_password").css("cursor","text");
    $("#id_keypair_name").css("cursor","text");
  });

  $(document).on('click', '#decryptpassword_button', function (evt) {
    encrypted_password = $("#id_encrypted_password").val();
    private_key = $('#id_private_key').val();
    if (!private_key) {
      evt.preventDefault();
      $(this).closest('.modal').modal('hide');
    }
    else {
      if (private_key.length > 0) {
        evt.preventDefault();
        decrypted_password = horizon.instances.decrypt_password(encrypted_password, private_key);
        if (decrypted_password === false || decrypted_password === null) {
          horizon.clearErrorMessages();
          horizon.alert('error', gettext('Could not decrypt the password'));
        }
        else {
          $("#id_decrypted_password").val(decrypted_password);
          $("#decryptpassword_button").hide();
        }
      }
    }
  });
});
