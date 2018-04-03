odoo.define('cms_form.lock_copy_paste', function (require) {
  'use strict';

  var sAnimation = require('website.content.snippets.animation');

  sAnimation.registry.CMSFormLockCopyPaste = sAnimation.Class.extend({
    selector: ".cms_form_wrapper form .lock_copy_paste",
    start: function () {
      this.setup_handlers();
    },
    setup_handlers: function(){
      this.$el.bind('cut copy paste', function (e) {
        e.preventDefault();
      });
      this.$el.on('contextmenu', function (e) {
        return false;
      });
    }
  });

});
