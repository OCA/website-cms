odoo.define('cms_toolbar', function (require) {
  'use strict';

  var sAnimation = require('website.content.snippets.animation');
  var msg_tool = require('cms_status_message.tool');
  var core = require('web.core');
  var _t = core._t;

  sAnimation.registry.CMSToolbar = sAnimation.Class.extend({
    selector: ".cms_toolbar",
    tooltip_selector: ".js_toolbar_action[data-toggle=popover]",
    events: _.extend({}, sAnimation.Class.prototype.events || {}, {
      'click .js_state_manager [data-action]': 'on_action_state_button_click'
    }),
    init: function () {
      this._super.apply(this, arguments);
      this.options = _.defaults(
        this.$el.data('options') || {}, {dimissStatusMsgTimeout: 5000}
      );
    },
    start: function () {
      this.$state_manage = this.$('.js_state_manager');
      this._tooltip_setup();
    },
    _tooltip_setup: function(){
      var self = this;
      self._tooltips = [];
      this.$(this.tooltip_selector).each(function() {
        var $el = $(this),
            options = self._tooltip_options($el);
        $el.popover(options);
        self._tooltips.push($el.data('bs.popover'));
        if($el.is(':visible') && $el.hasClass('popover_sticky')){
          $el.popover('show')
        } else {
          $el.popover('hide');
        }
      })
    },
    _tooltip_reset: function () {
      _.each(this._tooltips, function(popover) {
        popover.destroy();
      });
    },
    _tooltip_options: function($el){
      return {
        // TODO: use _.defaults
        html: true,
        content: $($el.data('htmlcontent')) ? $($el.data('htmlcontent')).html(): $el.data('content'),
        placement: $el.data('placement') ? $el.data('placement') : 'bottom',
        title: $el.data('title') ? $el.data('title') : '',
        trigger: 'click|hover|focus'
      }
    },
    on_action_state_button_click: function (ev) {
      ev.preventDefault();
      var self = this,
          action = $(ev.target).data('action'),
          data = self.$state_manage.data();
      return self._rpc({
        route: data.controller || '/cms/toolbar/action/state',
        params: {
          rec_id: data.id,
          model: data.model,
          old_state: data.state,
          transition: action,
          // TODO: make re-rendering optional
          reload: true
        },
      }).done(
        self.proxy('on_action_state_done')
      ).fail(self.proxy('on_action_state_fail'));
    },
    on_action_state_done: function (result) {
      return $.when(
        this.update_ui(result),
        // TODO: at the moment we support only "published/unpublished"
        // but in the future we'll have to handle more than this 2 states.
        this.update_status_message(result.new_state == 'published')
      );
    },
    update_ui: function (result){
      if (result.html) {
        var self = this;
        this._tooltip_reset();
        this._reload(result);
        this._reload_animations();
      }
    },
    _reload: function (result) {
      var $parent = this.$el.parent();
      this.$el.replaceWith(result.html);
      this.attachTo($parent.find(this.selector));
    },
    _reload_animations: function (result) {
      var self = this;
      // TODO: get them from [data-animation]
      // make animations set a `data-animation` attr on our actions
      // so that we can retrieve them automatically.
      _.each(['CMSDeleteConfirm', ], function(animation) {
        var Klass = sAnimation.registry[animation];
        new Klass(self).attachTo(self.$(Klass.prototype.selector));
      });
    },
    update_status_message: function (published) {
      // inject status message
      var self = this;
      var msg;
      if (published) {
        msg = {
          'msg': _t('Item published.'),
          'title': _t('Info')
        };
      } else {
        msg = {
          'msg': _t('Item unpublished.'),
          'title': _t('Warning'),
          'type': 'warning'
        };
      }
      return msg_tool.render_messages(msg).then(function(html) {
        $('.status_message').remove();
        var $msg = $(html).hide().prependTo('#wrap').fadeIn('slow');
        if (self.options.dimissStatusMsgTimeout) {
          $msg.fadeOut(self.options.dimissStatusMsgTimeout)
        }
      });
    },
    on_action_state_fail: function (result) {
      // TODO
      console.log('TOOLBAR STATE ACTION FAILING', result);
    }
  });

});
