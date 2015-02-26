/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    var modal_confirm_delete = $("#ModalConfirmDeletion");
    var modal_set_failed = $('#ModalSetFailed');

    $("#spanContextFailed").click(function () {
        if ($("#failedTestsList").is(":visible")) {
            $("#failedTestsList").hide();
        } else {
            $("#failedTestsList").show();
        };
    });

    $("#btnConfirmDeletion").click(function () {
        var suite = modal_confirm_delete.attr('suite'),
            test_id = modal_confirm_delete.attr('test_id');
        if (test_id || suite){
            if (test_id){
                $("#trTc" + test_id).remove();
            }
            else{
                $("#div" + suite.replace(/\s/g, '-')).remove();
            }

            var data = {'suite': suite};
            if (test_id){
                data['test_id'] = test_id
            }

            $.ajax({
                type: "DELETE",
                url: "/manual/" + pageData.project + "/" + "sprint/" + pageData.sprint + "/" + pageData.component,
                data: JSON.stringify(data)
            })
                .success(function () {
                    modal_confirm_delete.removeAttr('test_id');
                    modal_confirm_delete.removeAttr('suite');
                    modal_confirm_delete.modal('hide');
                })
                .fail(function (error) {
                    alert(error.responseText)
            });
        }
    });

    $(".btnRemoveSprintTestSuiteOrTest").click(function (event) {
        eventStopPropagation(event);
        var el = $(this);
        var suite = el.attr('data-test-suite'),
            test_id = el.attr('data-test-test_id');
        modal_confirm_delete.attr('suite', suite);
        modal_confirm_delete.attr('test_id', test_id);
        if (test_id){
            $("#divBodyConfirmDeletion").text("Remove " + test_id + "?");
        }
        else{
            $("#divBodyConfirmDeletion").text("Remove " + suite + "?");
        }
        modal_confirm_delete.modal();

    });

    window.setTestCaseResult = function (event, suite, test_id, result, error, result_attributes) {
        if(event){
            eventStopPropagation(event);
        }
        if (result == 'passed'){
            $("#trTc" + test_id).attr('class','success');
            $("#spTc" + test_id).text('passed');
        }
        else if(result == 'failed') {
            $("#trTc" + test_id).attr('class', 'danger');
            $("#spTc" + test_id).text('failed');
        }
        var data = {'suite': suite,
                    'component': pageData.component,
                    'sprint': pageData.sprint,
                    'test_id': test_id,
                    'result': result};
        if (result_attributes){
            data['result_attributes'] = result_attributes
            }
        if (error){
            data['error'] = error
        }


        $.ajax({type: "POST",
                url: "/manual/_edit_manual_test_result/" + pageData.project,
                data: JSON.stringify(data)
        })
            .success(function () {})
            .fail(function (error) {alert(error.responseText)});
    };

    $('#formSetFailed').submit(function (event) {
        eventStopPropagation(event);
        var suite = modal_set_failed.attr('suite'),
            test_id = modal_set_failed.attr('test_id');
        var x = document.forms["formSetFailed"].elements;
        var bugs = x['inputSetFailedBug'].value.replace(/\s{2,}/g, ' ').trim();
        var fail_reason = x['inputSetFailedReason'].value;
        var result_attributes = {};
        var error = '';

        if (bugs){
            result_attributes['bugs'] = bugs
        }
        if (fail_reason){
            error = fail_reason
        }

        $('#ModalSetFailed').modal('hide');
        setTestCaseResult(false, suite, test_id, "failed", error, result_attributes);

    });

    $(".btnSetTestCaseResultPassed").click(function(event) {
        eventStopPropagation(event);
        var el = $(this);
        var suite = el.attr('data-test-suite'),
            test_id = el.attr('data-test-test_id');
        setTestCaseResult(false, suite, test_id, "passed")
    });

    $(".btnSetTestCaseResultFailed").click(function(event) {
        eventStopPropagation(event);
        var el = $(this);
        var suite = el.attr('data-test-suite'),
            test_id = el.attr('data-test-test_id');
        modal_set_failed.attr('suite', suite);
        modal_set_failed.attr('test_id', test_id);
        $("#inputSetFailedBug").val('');
        $("#inputSetFailedReason").val('');
        modal_set_failed.modal();
    });

    $('#btnSetFailedCancel').click(function(){
        modal_set_failed.modal('hide')
    });

});