odoo.define('cms_form.master_slave', function (require) {
    'use strict';
    /*
    Handle master / slave fields automatically.
    TODO: explain behavior.
    */

    // TODO: this does not work ATM :(
    // var pyeval = require('web.pyeval');
    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.CMSFormMasterSlave = sAnimation.Class.extend({
      selector: ".cms_form_wrapper form",
      start: function () {
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
                var $input = $(this),
                    val = $input.val();
                if ($input.is(':checkbox')) {
                  // value == 'on' => true/false
                  val = $input.is(':checked');
                }
                $.each(mapping, function(slave_fname, values){
                  if (_.contains(values, val)) {
                    handler(slave_fname);
                  }
                });
              }).filter(
                'select,[type=checkbox],[type=radio]:checked,[type=text]'
              ).trigger('change');
              // trigger change to apply maste/slave rules at load
            }
          });
        });
      },
      handle_hide: function(slave_fname){
        $('[name="' + slave_fname +'"]').closest('.form-group').hide();
      },
      handle_show: function(slave_fname){
        $('[name="' + slave_fname +'"]').closest('.form-group').show();
      },
      handle_readonly: function(slave_fname){
        $('[name="' + slave_fname +'"]')
          .attr('disabled', 'disabled')
          .closest('.form-group').addClass('disabled');
      },
      handle_no_readonly: function(slave_fname){
        $('[name="' + slave_fname +'"]')
          .attr('disabled', null)
          .closest('.form-group').removeClass('disabled');
      },
      handle_required: function(slave_fname){
        $('[name="' + slave_fname +'"]').attr('required', 'required');
      },
      handle_no_required: function(slave_fname){
        $('[name="' + slave_fname +'"]').attr('required', null);
      }
    });

});
