odoo.define('cms_status_message.autodismiss', function (require) {
    'use strict';

  var sAnimation = require('website.content.snippets.animation');

  sAnimation.registry.CMSStatusMessageAutoDismiss = sAnimation.Class.extend({
    selector: ".status_message [data-autodismiss]",
    start: function () {
      this.dimissTimeout = this.$el.data('autodismissTimeout') || 8000;
      this.handle_autodimiss();
    },
    handle_autodimiss: function () {
      this.$el.fadeOut(this.dimissTimeout, function() {
        this.$el.remove();
      }).on("mouseover", function(e) {
        $(this).stop(true /*, false implied */ ).fadeIn(0);
      });
    }
  });

});
