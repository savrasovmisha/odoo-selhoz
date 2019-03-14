
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
	            self.$el.append("<input class='o_datepicker_input' type='text' name='date'>");
	            self.$el.append(
	            
	           '<div class="o_datepicker">'+
			        '<input type="date" name="date">'+
			        
			   '</div>');


	            self.$el.append('<div id="chart"><svg></svg></div>')

	              var data = [
							  {
							    key: "Cumulative Return",
							    values: [
							      { 
							        "label" : "A" ,
							        "value" : -29.765957771107
							      } , 
							      { 
							        "label" : "B" , 
							        "value" : 0
							      } , 
							      { 
							        "label" : "C" , 
							        "value" : 32.807804682612
							      } , 
							      { 
							        "label" : "D" , 
							        "value" : 196.45946739256
							      } , 
							      { 
							        "label" : "E" ,
							        "value" : 0.19434030906893
							      } , 
							      { 
							        "label" : "F" , 
							        "value" : -98.079782601442
							      } , 
							      { 
							        "label" : "G" , 
							        "value" : -13.925743130903
							      } , 
							      { 
							        "label" : "H" , 
							        "value" : -5.1387322875705
							      }
							    ]
							  }
							];

				nv.log('Hello World');
	           	nv.addGraph(function() {
				  var chart = nv.models.discreteBarChart()
				    .x(function(d) { return d.label })
				    .y(function(d) { return d.value })
				    .staggerLabels(true)
				    .showValues(true)

				  d3.select('#chart svg')
				    .datum(data)
				    .transition().duration(500)
				    .call(chart)
				    ;

				  nv.utils.windowResize(chart.update);

				  return chart;
				});






	        });





	      












	       var self = this;
	        return new instance.web.Model('stado.zagon')
	            .query(['name'])
	            .limit(15)
	            .all()
	            .then(function (results) {
	                _(results).each(function (item) {
	                    self.$el.append(QWeb.render('stado_zagon', {item: item}));
	                });
	            });

	   


	    },
	});

	
}




						