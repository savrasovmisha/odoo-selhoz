openerp.oepetstore = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.HomePage = instance.Widget.extend({
        template: "HomePage",
        start: function() {
        	 return $.when(
                new local.PetToysList(this).appendTo(this.$('.oe_petstore_homepage_left')),
                new local.MessageOfTheDay(this).appendTo(this.$('.oe_petstore_homepage_right'))
                
            );
        },
    });

    instance.web.client_actions.add('petstore.homepage', 'instance.oepetstore.HomePage');

    local.MessageOfTheDay = instance.Widget.extend({
        template: "MessageOfTheDay",
        start: function() {
            var self = this;
            return new instance.web.Model("oepetstore.message_of_the_day")
                .query(["message"])
                .order_by('-create_date', '-id')
                .first()
                .then(function(result) {
                    self.$(".oe_mywidget_message_of_the_day").text(result.message);
                });
        },
    });

    local.PetToysList = instance.Widget.extend({
	    template: 'PetToysList',
	    events: {
	        'click .oe_petstore_pettoy': 'selected_item',
	    },
	    start: function () {
	        var self = this;
	        return new instance.web.Model('product.product')
	            .query(['name', 'image'])
	            .filter([['categ_id.name', '=', "Pet Toys"]])
	            .limit(5)
	            .all()
	            .then(function (results) {
	                _(results).each(function (item) {
	                    self.$el.append(QWeb.render('PetToy', {item: item}));
	                });
	            });
	    },
	    selected_item: function (event) {
	        this.do_action({
	            type: 'ir.actions.act_window',
	            res_model: 'product.product',
	            res_id: $(event.currentTarget).data('id'),
	            views: [[false, 'form']],
	        });
	    },
	});

	local.FieldColor = instance.web.form.AbstractField.extend({
	    events: {
	        'change input': function (e) {
	            if (!this.get('effective_readonly')) {
	                this.internal_set_value($(e.currentTarget).val());
	            }
	        }
	    },
	    init: function() {
	        this._super.apply(this, arguments);
	        this.set("value", "");
	    },
	    start: function() {
	        this.on("change:effective_readonly", this, function() {
	            this.display_field();
	            this.render_value();
	        });
	        this.display_field();
	        return this._super();
	    },
	    display_field: function() {
	        this.$el.html(QWeb.render("FieldColor", {widget: this}));
	    },
	    render_value: function() {
	        if (this.get("effective_readonly")) {
	            this.$(".oe_field_color_content").css("background-color", this.get("value") || "#FFFFFF");
	        } else {
	            this.$("input").val(this.get("value") || "#FFFFFF");
	        }
	    },
	});
	instance.web.form.widgets.add('color', 'instance.oepetstore.FieldColor');


	local.WidgetCoordinates = instance.web.form.FormWidget.extend({
	    events: {
	        'click button': function () {
	            navigator.geolocation.getCurrentPosition(
	                this.proxy('received_position'));
	        }
	    },
	    start: function() {
	        var sup = this._super();
	        this.field_manager.on("field_changed:provider_latitude", this, this.display_map);
	        this.field_manager.on("field_changed:provider_longitude", this, this.display_map);
	        this.on("change:effective_readonly", this, this.display_map);
	        this.display_map();
	        return sup;
	    },
	    display_map: function() {
	        this.$el.html(QWeb.render("WidgetCoordinates", {
	            "latitude": this.field_manager.get_field_value("provider_latitude") || 0,
	            "longitude": this.field_manager.get_field_value("provider_longitude") || 0,
	        }));
	        this.$("button").toggle(! this.get("effective_readonly"));
	    },
	    received_position: function(obj) {
	        this.field_manager.set_values({
	            "provider_latitude": obj.coords.latitude,
	            "provider_longitude": obj.coords.longitude,
	        });
	    },
	});

	instance.web.form.custom_widgets.add('coordinates', 'instance.oepetstore.WidgetCoordinates');
}
