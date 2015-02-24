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

    window.setTestCaseResult = function (suite, test_id, result) {
        if (result == 'passed'){
            $("#tc" + test_id).attr('class','success');
        }
        else if(result == 'failed') {
            $("#tc" + test_id).attr('class', 'danger');
        }

        $.ajax({type: "POST",
                url: "/manual/_edit_manual_test_result/" + pageData.project,
                data: JSON.stringify({'suite': suite,
                                      'component': pageData.component,
                                      'sprint': pageData.sprint,
                                      'test_id': test_id,
                                      'result': result})
        })
            .success(function () {
            })
            .fail(function (error) {
                alert(error.responseText)
            });
    }
});