
openerp.kormlenie = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.analiz_kormleniya = instance.Widget.extend({
        template: "HomePage",
        start: function() {
        	
        	/*this.$el.append("<div>Hello dear Odoo user!</div>");*/
        	 return $.when(
                new local.stado_zagon_list(this).appendTo(this.$('.oe_petstore_homepage_left'))
                
            );
        },
    });

    instance.web.client_actions.add('korm.analiz_kormleniya', 'instance.kormlenie.analiz_kormleniya');

    local.stado_zagon_list = instance.Widget.extend({
	    template: 'stado_zagon_list',
	    
	    start: function () {

	    	var self = this;
	        var model = new instance.web.Model("korm.analiz_kormleniya_report");
	        model.call("my_method", {context: new instance.web.CompoundContext()}).then(function(result) {
	            self.$el.append("<div>Hello " + result["hello"] + "</div>");
	            // will show "Hello world" to the user
	        });
	       /* var self = this;
	        return new instance.web.Model('stado.zagon')
	            .query(['name'])
	            .limit(15)
	            .all()
	            .then(function (results) {
	                _(results).each(function (item) {
	                    self.$el.append(QWeb.render('stado_zagon', {item: item}));
	                });
	            });*/
	    },
	});

	
}
