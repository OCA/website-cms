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
        this.handlers = {
          'hide': $.proxy(this.handle_hide, this),
          'show': $.proxy(this.handle_show, this)
        };
        this.load_master_slave();
      },
      load_master_slave: function(){
        var self = this;
        $.each(this.data.master_slave, function(master, slaves){
          var $master_input = $('[name="' + master +'"]');
          $.each(slaves, function(action, mapping){
            var handler = self.handlers[action];
            if (handler) {
              $master_input.on('change', function(){ handler($master_input, mapping) }).trigger('change');
            }
          })
        })
      },
      // TODO: merge these functions (only difference is "show()" vs "hide()")
      handle_hide: function($input, mapping){
        $.each(mapping, function(slave_fname, values){
          console.log($input.val(), slave_fname, values);
          if ($.inArray($input.val(), values) >= 0) {
            $('[name="' + slave_fname +'"]').closest('.form-group').hide();
          }
        });
      },
      handle_show: function($input, mapping){
        $.each(mapping, function(slave_fname, values){
          console.log($input.val(), slave_fname, values);
          if ($.inArray($input.val(), values) >= 0) {
            $('[name="' + slave_fname +'"]').closest('.form-group').show();
          }
        });
      }
    });

});
