odoo.define('cms_notification.read_unread', function (require) {
    'use strict';
    /*
    Mark messages as read/unread
    */

    var animation = require("web_editor.snippets.animation");
    var $ = require("$");
    var session = require('web.session');
    var Model = require('web.Model');
    var MessageModel = new Model('mail.message', session.user_context);

    return animation.registry.CMSNotificationsReadUnread = animation.Class.extend({
      selector: ".notification_listing a.mark_as",
      start: function (editable_mode) {
        var self = this;
        this.$el.on('click', function(e){
          e.stopPropagation();
          var action = $(e.currentTarget).data('action');
          var ids = [$(e.currentTarget).closest('.list_item').data('id')];
          self[action](ids).then($.proxy(self.update_ui, self, ids));
        });
      },
      mark_as_read: function (ids) {
        return MessageModel.call('set_message_done', [ids]);
      },
      mark_as_unread: function (ids) {
        return MessageModel.call('mark_as_unread', [ids]);
      },
      update_ui: function(ids){
        var self = this;
        $.each(ids, function(){
          var $item = $('#item_' + this),
              status = $item.data('status'),
              next_status = status == 'unread'? 'read': 'unread';
          // update current item status
          $item.data('status', next_status);
          $item.switchClass('item_' + status, 'item_' + next_status);
        });
        // update global indicator
        var unread_count =
          self.$el.closest('.listing').find('.item_unread').length;
        if (unread_count) {
          $('#user-menu').addClass('has_unread_notif');
        } else {
          $('#user-menu').removeClass('has_unread_notif');
        }
      }

    });

});
