odoo.define('cms_toolbar.publish', function (require) {
  'use strict';

  var WebsiteRoot = require('website.WebsiteRoot').WebsiteRoot;
  var msg_tool = require('cms_status_message.tool');
  var core = require('web.core');
  var _t = core._t;

  /*
  Override publish btn handler to inject status messages.
  */

  WebsiteRoot.include({
    /*
    FIXME: barely copied from `webste.website_root.js`
    Reason: this function does not return a Deferred object to hook to
    hence there's no reliable way to hook to state change.
    */
    _onPublishBtnClick: function (ev) {
        ev.preventDefault();

        var self = this;
        var $data = $(ev.currentTarget).parents(".js_publish_management:first");
        this._rpc({
            route: $data.data('controller') || '/website/publish',
            params: {
                id: +$data.data('id'),
                object: $data.data('object'),
            },
        })
        .done(function (result) {
            $data.toggleClass("css_unpublished css_published");
            $data.find('input').prop("checked", result);
            $data.parents("[data-publish]").attr("data-publish", +result ? 'on' : 'off');
            if ($data.closest('.cms_toolbar')) {
              self._on_publish_status_message($data.hasClass('css_published'));
            }
        })
        .fail(function (err, data) {
            return new Dialog(self, {
                title: data.data ? data.data.arguments[0] : "",
                $content: $('<div/>', {
                    html: (data.data ? data.data.arguments[1] : data.statusText)
                        + '<br/>'
                        + _.str.sprintf(
                            _t('It might be possible to edit the relevant items or fix the issue in <a href="%s">the classic Odoo interface</a>'),
                            '/web#return_label=Website&model=' + $data.data('object') + '&id=' + $data.data('id')
                        ),
                }),
            }).open();
        });
    },
    _on_publish_status_message: function (published) {
      // inject status message
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
      msg_tool.render_messages(msg).then(function(html) {
        $('.status_message').remove();
        $(html).hide().prependTo('#wrap').fadeIn('slow');
      });
    }
  });

});
