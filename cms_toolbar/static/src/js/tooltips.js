odoo.define('cms_toolbar.tooltips', function (require) {
  'use strict';

  var sAnimation = require('website.content.snippets.animation');

  sAnimation.registry.CMSToolbarTooltips = sAnimation.Class.extend({
    selector: '.cms_toolbar [data-toggle="popover"]',
    start: function () {
      this.setup_tooltips();
    },
    setup_tooltips: function(){
      var options = this.popover_options();
      this.$el.popover(options);
      if(this.$el.is(':visible') && this.$el.hasClass('popover_sticky')){
        this.$el.popover('show')
      }
    },
    popover_options: function(){
      return {
        html: true,
        content: $(this.$el.data('htmlcontent')) ? $(this.$el.data('htmlcontent')).html(): this.$el.data('content'),
        placement: this.$el.data('placement') ? this.$el.data('placement') : 'bottom',
        title: this.$el.data('title') ? this.$el.data('title') : '',
        trigger: 'click|hover|focus'
      }
    }
  });

});
