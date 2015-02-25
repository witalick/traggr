/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    var modal_confirm_delete = $("#ModalConfirmDeletion");

    $("#btnConfirmDeletion").click(function () {
        var sprint_name = modal_confirm_delete.attr('sprint_name');
        $("#li" + sprint_name).remove();
        $.ajax({type: "DELETE",
            url: "/manual/" + pageData.project + "/" + "sprint",
            data: JSON.stringify({'sprint_name': sprint_name})
        })
            .success(function () {
                modal_confirm_delete.removeAttr('sprint_name');
                modal_confirm_delete.modal('hide')
            })
            .fail(function (error) {alert(error.responseText)});
    });

    window.removeSprintResultstWithConfirmation = function (sprint_name) {
        modal_confirm_delete.attr('sprint_name', sprint_name);
        $("#divBodyConfirmDeletion").text("Remove " + sprint_name + "?");
        modal_confirm_delete.modal();

    };

});