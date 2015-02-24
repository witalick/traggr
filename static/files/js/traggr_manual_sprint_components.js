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

    window.removeComponentResultstWithConfirmation = function (project, sprint, component) {

        $("#btnConfirmDeletion").click(function () {

            $("#li" + component).remove();
            $.ajax({type: "DELETE",
                    url: "/manual/" + project + "/" + "sprint/" + sprint,
                    data: JSON.stringify({'component': component})
        })
            .success(function () {})
            .fail(function (error) {alert(error.responseText)});
        });
        $("#divBodyConfirmDeletion").text("Remove " + component + "?");

        $("#ModalConfirmDeletion").modal();

    };

});