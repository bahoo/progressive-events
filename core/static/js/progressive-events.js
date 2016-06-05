var progressive_events = function(){


    var self = {

        utils: {

            getElementPosition: function (field){
                var offsetLeft = 0;
                var offsetTop = 0;
                while (field) {
                    offsetLeft += field.offsetLeft;
                    offsetTop += field.offsetTop;
                    field = field.offsetParent;
                }

                return {
                    left: offsetLeft,
                    top: offsetTop
                };
            }

        },

        bind: function(){
            return self;
        },

        searchForm: {

            bind: function(){
                document.querySelector('.search-form [data-attribute="event_types"]').addEventListener('focus', self.searchForm.eventTypesFieldFocus);
                document.querySelector('.search-form').addEventListener('keyup', self.searchForm.keyup);
                document.querySelector('.search-form').addEventListener('keypress', self.searchForm.keypress);
                document.getElementById('id_event_types').addEventListener('click', self.searchForm.eventTypeClick);
                document.addEventListener('click', self.searchForm.hideChecklist);

                self.searchForm.eventTypeClick({'target': document.querySelector('#id_event_types input')});

                return self;
            },

            eventTypeClick: function(e){

                if(['INPUT', 'LABEL'].indexOf(e.target.tagName) != -1){
                    if(e.stopPropagation){
                        e.stopPropagation();
                    }
                } else {
                    return;
                }

                var sentenceParts = [];
                var checked = e.target.closest('ul').querySelectorAll('input:checked');
                for(var i = 0; i < checked.length; i++){
                    sentenceParts.push((checked[i].closest('label').innerText + 's').toLowerCase());
                }

                if(sentenceParts.length == e.target.closest('ul').querySelectorAll('input').length){
                    sentence = 'all events';
                } else if(sentenceParts.length == 0){
                    sentence = '';
                } else if(sentenceParts.length == 1){
                    sentence = sentenceParts[0];
                } else if(sentenceParts.length == 2) {
                    sentence = sentenceParts.join(' and ');
                } else {
                    sentence = sentenceParts.slice(0, sentenceParts.length-1).join(', ') + ', and ' + sentenceParts[sentenceParts.length-1];
                }

                var elem = document.querySelector('span[data-attribute="event_types"]');
                elem.innerHTML = sentence

                if(e.isTrusted){
                    self.searchForm.eventTypesFieldFocus({'target': elem});
                }

            },

            eventTypesFieldFocus: function(e){
                var field = e.target;
                var fieldPosition = self.utils.getElementPosition(field);
                var checklist = e.target.closest('form').querySelector('ul');
                checklist.classList.remove('hidden');
                checklist.style.position = 'absolute';
                checklist.style.left = (fieldPosition.left + (field.offsetWidth / 2) - (checklist.offsetWidth / 2)) + 'px';
                checklist.style.top = (fieldPosition.top + field.offsetHeight + 5) + 'px';
            },

            hideChecklist: function(e){
                if(e.target.tagName == 'INPUT' || e.target.hasAttribute('data-attribute')){
                    e.stopPropagation();
                    return;
                }
                document.querySelector('ul#id_event_types').classList.add('hidden');
            },

            keyup: function(e){

                // update data
                var attribute = e.target.getAttribute('data-attribute');

                if(!attribute){
                    return;
                }

                if(attribute == 'event_types'){

                    console.log(e.which);

                } else {

                    var field = e.target.closest('form').querySelector('[name="' + e.target.getAttribute('data-attribute') + '"]');
                    field.value = e.target.innerHTML;


                    if(field.value == e.target.innerHTML && field.checkValidity()){
                        e.target.classList.remove('invalid');

                        if(e.which == 13){
                            e.target.closest('form').submit();
                        }

                    } else {
                        e.target.classList.add('invalid');
                    }

                }

            },

            keypress: function(e){

                // no enter key.
                if(e.which == 13){
                    e.preventDefault();
                }

            }
        }
    };

    return self.bind();

}();