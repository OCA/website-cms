odoo.define('cms_delete_content.delete_confirm', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var msg_tool = require('cms_status_message.tool');
    var core = require('web.core');
    var _t = core._t;
    var animation = require("web_editor.snippets.animation");
    var $ = require("$");

    return animation.registry.countryDropdown = animation.Class.extend({
      selector: ".cms_delete_confirm",
      start: function (editable_mode) {
        this.modal_url = this.$el.attr('href');
        this.$el.on('click', $.proxy(this.handle_click, this));
      },
      handle_click: function(evt){
        evt.preventDefault();
        var self = this;
        $.ajax({
          method: "GET",
          url: this.modal_url,
          data: {}
        }).done(function (modal) {
          self.$modal = $(modal);
          self.$modal.appendTo('body').modal();
          self.$form = $('form', self.$modal);
          self.$form.submit($.proxy(self.handle_modal_submit, self));
        });
      },
      handle_modal_submit: function(evt){
        evt.preventDefault();
        var self = this;
        var url = self.$form.attr('action'),
            data = self.$form.serialize();
        $.ajax({
          type: 'POST',
          url: url,
          data: data,
          dataType: 'json',
        }).done(function (result) {
          self.handle_modal_success(result);
        });
        return false;
      },
      handle_modal_success: function(result){
        // hide modal
        this.$modal.modal('hide');
        if(result.redirect){
          window.setTimeout(function() {
            location.href = result.redirect;
          }, 1000);
        } else {
          // inject status message if not redirecting
          var msg = {
            'msg': result.message,
            'title': _t('Info')
          }
          // wipe existing
          $('.status_message').remove();
          // inject new
          $(msg_tool.render_messages(msg))
            .hide().prependTo('main').fadeIn('slow');
        }
        // TODO: trigger custom event as hook
      }
    });

});
