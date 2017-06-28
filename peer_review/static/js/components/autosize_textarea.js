// TODO put this in a CommonJS module

var AutosizeTextarea = {
    props: ['value', 'label'],
    components: {
        'mdl-textfield': VueMdl.components.MdlTextfield
    },
    template: '<div class="mdl-textfield mdl-js-textfield">' +
                  '<textarea :id="_uid" class="mdl-textfield__input" type="text" rows="1" @input="$emit(\'input\', $event.target.value)">{{ value }}</textarea>' +
                  '<label :for="_uid" class="mdl-textfield__label">{{ label }}</label>' +
              '</div>',
    mounted: function() {
        autosize(this.$el.querySelector('textarea'));
        componentHandler.upgradeElement(this.$el);
    },
    updated: function() {
        this.$el.MaterialTextfield.checkDirty();
    }
};
