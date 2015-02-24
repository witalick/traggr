/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    $("#spanContextFailed").click(function () {

        if ($("#failedTestsList").is(":visible")) {
            $("#failedTestsList").hide();
        } else {
            $("#failedTestsList").show();
        }
        ;
    });

    window.removeSuiteResultstWithConfirmation = function (suite) {
        $("#btnConfirmDeletion").click(function () {
            $("#div" + suite.replace(' ', '-')).remove();
            $.ajax({type: "DELETE",
                    url: "/manual/" + pageData.project + "/" + "sprint/" + pageData.sprint + "/" + pageData.component,
                    data: JSON.stringify({'suite': suite})
            });
        });
        $("#divBodyConfirmDeletion").text("Remove " + suite + "?");

        $("#ModalConfirmDeletion").modal();

    };

    window.setTestCaseResult = function (suite, test_id, result, error, result_attributes) {
        if (result == 'passed'){
            $("#tc" + test_id).attr('class','success');
        }
        else if(result == 'failed') {
            $("#tc" + test_id).attr('class', 'danger');
        }
        var data = {'suite': suite,
                    'component': pageData.component,
                    'sprint': pageData.sprint,
                    'test_id': test_id,
                    'result': result};
        if (result_attributes){
            data['result_attributes'] = result_attributes
            }

        $.ajax({type: "POST",
                url: "/manual/_edit_manual_test_result/" + pageData.project,
                data: JSON.stringify(data)
        })
            .success(function () {})
            .fail(function (error) {alert(error.responseText)});
    };

    window.setTestCaseFailed = function(suite, test_id) {
        $('#btnSetFailed').click(function () {
            var x = document.forms["formSetFailed"].elements;
            var is_bug_for = x['inputSetFailedBug'].value.replace(/\s{2,}/g, ' ').trim();
            var fail_reason = x['inputSetFailedReason'].value;
            var result_attributes = {};
            var error = '';

            if (is_bug_for){
                result_attributes['is_bug_for'] = is_bug_for
            }
            if (fail_reason){
                error = fail_reason
            }

            $('#ModalSetFailed').modal('hide');
            setTestCaseResult(suite, test_id, "failed", error, result_attributes);

        });
        $('#ModalSetFailed').modal();
    };

    $('#btnSetFailedCancel').click(function(){
        $('#ModalSetFailed').modal('hide')
    });

});