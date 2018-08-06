odoo.define('cms_notification.read_unread', function (require) {
    'use strict';
    /*
    Mark messages as read/unread
    */

    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.CMSNotificationsReadUnread = sAnimation.Class.extend({
      selector: ".notification_listing a.mark_as",
      start: function () {
        var self = this;
        this.$el.on('click', function(e){
          e.stopPropagation();
          var action = $(e.currentTarget).data('action');
          var ids = [$(e.currentTarget).closest('.list_item').data('id')];
          self[action](ids).then($.proxy(self.update_ui, self, ids));
        });
      },
      mark_as_read: function (ids) {
        return this._rpc({
          model: 'mail.message',
          method: 'set_message_done',
          args: [ids]
        })
      },
      mark_as_unread: function (ids) {
        return this._rpc({
          model: 'mail.message',
          method: 'mark_as_unread',
          args: [ids]
        })
      },
      update_ui: function(ids){
        var self = this;
        $.each(ids, function(){
          var $item = $('#item_' + this),
              status = $item.data('status'),
              next_status = 'unread';
          if (status === 'unread') {
            next_status = 'read';
          }
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
