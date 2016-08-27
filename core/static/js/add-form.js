var progressive_events = progressive_events || {}

progressive_events.addForm = function(){

    var self = {

        bind: function(){
            document.addEventListener("DOMContentLoaded", function(){
                new sigo('id_venue-title', '/api/1/venues', 'id_venue-venue_id', 'venue_form', "<b>${item.title}</b>, ${item.address}, ${item.city}, ${item.state}, ${item.zipcode}");
                new sigo('id_organization-title', '/api/1/orgs', 'id_organization-organization_id', 'organization_form', "<b>${item.title}</b>");
            });
            return self;
        }

    };

    return self.bind();

}();