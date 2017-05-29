odoo.define('cms_form.master_slave', function (require) {
    'use strict';
    /*
    Handle master / slave fields automatically.
    TODO: explain behavior.
    */

    // TODO: this does not work ATM :(
    // var pyeval = require('web.pyeval');
    var animation = require("web_editor.snippets.animation");
    var $ = require("$");

    return animation.registry.CMSFormMasterSlave = animation.Class.extend({
      selector: ".cms_form_wrapper form",
      start: function (editable_mode) {
        this.data = this.$el.data('form');
        this.setup_handlers();
        this.load_master_slave();
      },
      setup_handlers: function(){
        this.handlers = {
          'hide': $.proxy(this.handle_hide, this),
          'show': $.proxy(this.handle_show, this),
          'readonly': $.proxy(this.handle_readonly, this),
          'no_readonly': $.proxy(this.handle_no_readonly, this),
          'required': $.proxy(this.handle_required, this),
          'no_required': $.proxy(this.handle_no_required, this)
        };
      },
      load_master_slave: function(){
        var self = this;
        $.each(this.data.master_slave, function(master, slaves){
          var $master_input = $('[name="' + master +'"]');
          $.each(slaves, function(action, mapping){
            var handler = self.handlers[action];
            if (handler) {
              $master_input.on('change', function(){
                handler($(this), mapping) }
              ).filter(':selected,:checked,[type=text]').trigger('change'); // trigger change only for specific inputs
            }
          })
        })
      },
      // TODO: merge these functions as they are pretty much equals
      handle_hide: function($input, mapping){
        $.each(mapping, function(slave_fname, values){
          if ($.inArray($input.val(), values) >= 0) {
            $('[name="' + slave_fname +'"]').closest('.form-group').hide();
          }
        });
      },
      handle_show: function($input, mapping){
        $.each(mapping, function(slave_fname, values){
          if ($.inArray($input.val(), values) >= 0) {
            $('[name="' + slave_fname +'"]').closest('.form-group').show();
          }
        });
      },
      handle_readonly: function($input, mapping){
        $.each(mapping, function(slave_fname, values){
          if ($.inArray($input.val(), values) >= 0) {
            $('[name="' + slave_fname +'"]').attr('disabled', 'disabled');
          }
        });
      },
      handle_no_readonly: function($input, mapping){
        $.each(mapping, function(slave_fname, values){
          if ($.inArray($input.val(), values) >= 0) {
            $('[name="' + slave_fname +'"]').attr('disabled', null);
          }
        });
      },
      handle_required: function($input, mapping){
        $.each(mapping, function(slave_fname, values){
          if ($.inArray($input.val(), values) >= 0) {
            $('[name="' + slave_fname +'"]').attr('required', 'required');
          }
        });
      },
      handle_no_required: function($input, mapping){
        $.each(mapping, function(slave_fname, values){
          if ($.inArray($input.val(), values) >= 0) {
            $('[name="' + slave_fname +'"]').attr('required', null);
          }
        });
      }
    });

});
