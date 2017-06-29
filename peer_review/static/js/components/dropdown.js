// TODO put this in a CommonJS module

var Dropdown = {
    props: ['id', 'value', 'options', 'label', 'disabled', 'empty-caption'],
    computed: {
        displayName: function() {
            return (this.value && this.value.name) || this.emptyCaption;
        }
    },
    template: '<div>' +
                  '<label :for="id">{{ label }}</label>' +
                  '<button :id="id"' +
                         ' type="button"' +
                         ' class="mdl-button mdl-js-button"' +
                         ' :disabled="disabled">' +
                      '<span>{{ displayName }}</span>' +
                  '</button>' +
                  '<ul :for="id" class="mdl-menu mdl-js-menu">' +
                      '<li class="mdl-menu__item" v-for="option in options" :key="option.value" @click="$emit(\'input\', option)">' +
                          '{{ option.name }}' +
                      '</li>' +
                  '</ul>' +
              '</div>',
    mounted: function() {
        componentHandler.upgradeElement(this.$el.querySelector('button'));
    }
};
