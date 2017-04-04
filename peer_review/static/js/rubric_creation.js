/* eslint-env jquery */
/* global Materialize */
/* global defaultToastDuration */
/* global postToEndpoint */
/* global showGenericErrorMessage */

/* exported addRubricCriteria */
function addRubricCriteria(template) {
    $('[data-criteria-container]').append(template);
}

/* exported removeRubricCriteria */
function removeRubricCriteria(removeButton) {
    $(removeButton).parents('.card').first().remove();
}

function getRubricCriteria() {
    return $('[data-criterion-container]').map(function(index, element) {
        return {description: $(element).find('[data-criterion-description]').val()};
    }).get();
}

function areCriteriaValid(criteria) {
    if(criteria.length < 1) {
        return false;
    }
    for(var i = 0; i < criteria.length; ++i) {
        if(!criteria[i].description.trim()) {
            return false;
        }
    }
    return true;
}

/* exported submitRubricCriteria */
function submitRubricCriteria() {
    try {
        var criteria = getRubricCriteria();
        var rubricDescription = $('#rubric-description').val();
        var promptAssignment = $('#prompt-selector-parent').find('select').val();
        var revisionAssignment = $('#revision-selector-parent').find('select').val() || null;
        if(!areCriteriaValid(criteria)) {
            Materialize.toast('You have left some criteria blank.', defaultToastDuration);
        }
        else if(!rubricDescription.trim()) {
            Materialize.toast('You must give this rubric a description.', defaultToastDuration);
        }
        else if(promptAssignment === null) {
            Materialize.toast('You must select an assignment.', defaultToastDuration);
        }
        else {
            var data = {
                criteria: criteria,
                promptAssignment: promptAssignment,
                revisionAssignment: revisionAssignment,
                rubricDescription: rubricDescription
            };
            var endpoint = $('[data-rubric-form]').attr('action');
            var submitButton = $('[data-submit-button]');
            postToEndpoint(endpoint,
                        submitButton,
                        function() {
                            Materialize.toast('Rubric successfully created.', defaultToastDuration);
                        },
                        showGenericErrorMessage,
                        data);
        }
    }
    catch(error) {
        console.error(error);
        showGenericErrorMessage();
    }
}

(function() {
    var assignmentIDsToNames = $('#rubric-data').data('potential-prompts-and-revisions');

    // hack required because Materialize moves the select around in the DOM tree :(
    function isPromptSelector(select) {
        var promptSelector = $('#prompt-selector-parent').find('select');
        return select.attr('id') == promptSelector.attr('id');
    }
    window.isPromptSelector = isPromptSelector;
    
    function updateSelect(selectElement, selectedAssignmentID, skippedAssignmentID) {
        var selectedAssignmentName = assignmentIDsToNames[selectedAssignmentID];
        selectElement.empty();

        var placeholder = $('<option></option>');
        if(isPromptSelector(selectElement)) {
            placeholder.attr('disabled', '').text('Select an assignment');
        }
        else {
            placeholder.text('No revision').attr('value', '');
        }
        if(selectedAssignmentID === null) {
            placeholder.attr('selected', '');
        }
        selectElement.append(placeholder);

        $.each(Object.keys(assignmentIDsToNames).sort(), function(i, id) {
            if(id !== skippedAssignmentID) {
                var assignmentName = assignmentIDsToNames[id];
                var option = $('<option></option>').attr('value', id).text(assignmentName);
                if(id === selectedAssignmentID) {
                    option.attr('selected', '');
                }
                selectElement.append(option);
            }
        });
        selectElement.material_select();
    } 

    function selectAssignment(element) {
        var changedSelect = $(element);
        var unchangedSelect = (isPromptSelector(changedSelect) ? $('#revision-selector-parent') : $('#prompt-selector-parent')).find('select');

        var newlySelectedAssignment = changedSelect.val();
        var unchangedSelectedAssignment = unchangedSelect.val();

        updateSelect(changedSelect, newlySelectedAssignment, unchangedSelectedAssignment);
        updateSelect(unchangedSelect, unchangedSelectedAssignment, newlySelectedAssignment);
    }
    window.selectAssignment = selectAssignment;
})();

$('document').ready(function() {
    $('select')
        .on('change', function(event) {
            var select = $(event.target);
            selectAssignment(select);
            updateValidationStatus(select);
        })
        .each(function(i, element) {
            var select = $(element);
            var selectValue = select.val() || null;
            selectAssignment(select);
            if(selectValue !== null) {
                updateValidationStatus(select);
            }
            else {
                if(isPromptSelector(select)) {
                    $('[data-submit-button]').prop('disabled', true);
                }
            }
        });
});

