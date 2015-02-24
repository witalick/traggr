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

    window.removeSuiteResultstWithConfirmation = function (project, sprint, component, suite) {

        $("#btnConfirmDeletion").click(function () {

            $("#li" + component).remove();
            $.ajax({type: "DELETE",
                    url: "/manual/" + project + "/" + "sprint/" + sprint + "/" + component,
                    data: JSON.stringify({'suite': suite})
            });
        });
        $("#divBodyConfirmDeletion").text("Remove " + suite + "?");

        $("#ModalConfirmDeletion").modal();

    };

});