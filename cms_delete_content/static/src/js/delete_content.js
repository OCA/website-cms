odoo.define('cms_delete_content.delete_confirm', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var msg_tool = require('cms_status_message.tool');
    var core = require('web.core');
    var _t = core._t;

    $(document).ready(function () {
      $(".cms_delete_confirm").click(function(evt){
        evt.preventDefault();
        // load modal
        $.ajax({
          method: "GET",
          url: $(this).attr('href'),
          data: {}
        }).done(function (modal) {
          var $modal = $(modal),
              $form = $('form', $modal);
          // handle modal form submit
          $form.submit(function(evt){
            evt.preventDefault();
            $.ajax({
              type: 'POST',
              url: $form.attr('action'),
              data: $form.serialize(),
              dataType: 'json',
              success: function (result) {
                // hide modal
                $modal.modal('hide');
                if(result.redirect){
                  window.setTimeout(function() {
                    location.href = result.redirect;
                  }, 2000);
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
            return false;
          });
          // inject and show modal
          $modal.appendTo('body').modal();
        })
      })
    });

});
