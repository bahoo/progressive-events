var progressive_events = progressive_events || {}

progressive_events.addForm = function(){

    var self = {

        bind: function(){
            document.addEventListener("DOMContentLoaded", function(){
                sigo.init('id_venue-title', '/api/1/venues', 'id_venue-venue_id', 'venue_form', "<b>${item.title}</b>, ${item.address}, ${item.city}, ${item.state}, ${item.zipcode}");
            });
            return self;
        }

    };

    return self.bind();

}();