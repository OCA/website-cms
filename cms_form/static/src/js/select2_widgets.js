odoo.define('cms_form.select2', function (require) {
  'use strict';

  var weContext = require("web_editor.context");
  var sAnimation = require('website.content.snippets.animation');

  var CMSFormSelect2 = sAnimation.Class.extend({
    start: function () {
      this.setup_options();
      this.setup_widget();
      this.current_results = [];
    },
    setup_options: function(){
      this.w_options =  _.defaults(this.$el.data('params') || {}, {
        'search_field': 'name',
        'display_name': 'name',
        'fields': ['name'],
        'context': weContext.get(),
        'placeholder': this.$el.attr('placeholder')
      });
      // make sure we read display name field too
      if (!_.contains(this.w_options.fields, this.w_options.display_name)) {
        this.w_options.fields.push(this.w_options.display_name);
      }
      this.s2_options = {
        'query': $.proxy(this.s2_query, this),
        'initSelection': $.proxy(this.s2_initSelection, this),
        'placeholder': this.w_options.placeholder
      };
    },
    setup_widget: function(){
      this.$el.select2(this.s2_options);
    },
    get_domain: function (options) {
      var self = this,
          domain = [];
      if (options.term){
        domain.push([
          self.w_options.search_field, 'ilike', '%' + options.term + '%'
        ])
      }
      // TODO: use data.CompundDomain to build domain
      // ATM it's just in backend assets
      // and requires both data.js and pyeval.js
      return _.union(domain, self.w_options.domain);
    },
    s2_query: function(options) {
      var self = this,
          domain = self.get_domain(options);
      return this._rpc({
        model: self.w_options.model,
        method: 'search_read',
        domain: domain,
        fields: self.w_options.fields,
        context: self.w_options.context
      }).then($.proxy(self.s2_handle_query_results, self, options));
    },
    s2_handle_query_results: function (options, results) {
      var self = this;
      var display_name = self.w_options.display_name;
      results.sort(function(a, b) {
        return a[display_name].localeCompare(b[display_name]);
      });
      var res = {
        results: []
      };
      _.each(results, function(x) {
        res.results.push({
          id: x.id,
          text: x[display_name],
          isNew: false
        });
      });
      self.current_results = res.results;
      options.callback(res);
    },
    s2_initSelection: function(element, callback) {
      callback(this._s2_initSelection_value(element, callback));
    },
    _s2_initSelection_value: function(element, callback) {
      console.log('You should implement this...')
    }
  });

  sAnimation.registry.CMSFormSelect2M2O = CMSFormSelect2.extend({
    selector: ".js_select2_x2x_widget.m2o",
    setup_options: function(){
      this._super();
      this.s2_options = _.extend(this.s2_options, {
        'multiple': false
      });
    },
    _s2_initSelection_value: function(element, callback) {
      var value = this.w_options.init_value;
      if (value) {
        value.text = value[this.w_options.display_name];
      } else {
        // make sure placeholder is displayed w/ no value
        value = {'id': -1, 'text': this.w_options.placeholder};
      }
      return value;
    }
  });

  sAnimation.registry.CMSFormSelect2X2M = CMSFormSelect2.extend({
    selector: ".js_select2_x2x_widget.x2m",
    setup_options: function(){
      this._super();
      this.s2_options = _.extend(this.s2_options, {
        'multiple': true,
        'tags': true,
        'tokenSeparators': [",", " ", "_"],
        'formatResult': $.proxy(this.s2_formatResult, this),
      });
    },
    s2_formatResult: function(term) {
      if (term.isNew) {
        // TODO: creating new records is not supported yet
        return '<span class="label label-primary">New</span> ' + _.escape(term.text);
      } else {
        return _.escape(term.text);
      }
    },
    _s2_initSelection_value: function(element, callback) {
      var self = this;
      var values = [];
      if (this.w_options.init_value.length > 0) {
        $(this.w_options.init_value).each(function () {
          values.push({id: this.id, text: this[self.w_options.display_name]});
        });
      }
      // HACK: this seems the only way to make placehoder show up
      element.val('');
      return values;
    }
  });

  return CMSFormSelect2;

});
