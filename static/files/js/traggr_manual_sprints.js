/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    var modal_confirm_delete = $("#ModalConfirmDeletion");
    var modal_edit_name = $("#ModalEditName");

    $("#liAdd").click(function () {
            addTestCase();
    });

    $("#liAddSprint").click(function(){
        $("#inputSprint").val('');
        $("#ModalAddSprint").modal()
    });

    $("#btnConfirmDeletion").click(function () {
        var sprint_name = modal_confirm_delete.attr('sprint_name');
        $("#li" + sprint_name.replace(/\s/g, '-')).remove();
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

    $(".btnRemoveSprint").click(function () {
        var sprint_name = $(this).attr("data-test-sprint");
        modal_confirm_delete.attr('sprint_name', sprint_name);
        $("#divBodyConfirmDeletion").text("Remove " + sprint_name + "?");
        modal_confirm_delete.modal();
    });

    $("#formEditName").submit(function (event) {
        eventStopPropagation(event);
        var x = document.forms["formEditName"].elements;
        var new_name = x['inputNewName'].value.replace(/\s{2,}/g, ' ').trim();
        var sprint_name = modal_edit_name.attr('sprint_name');
        $.ajax({
            type: "POST",
            url: '/manual/_edit_manual_sprint/'+ pageData.project,
            data: JSON.stringify({
                sprint: sprint_name,
                sprint_new: new_name}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        })
            .success(function () {
                modal_edit_name.removeAttr('sprint_name');
                modal_edit_name.modal('hide');
                window.location.reload()
            })
            .fail(function (error) {
                alert(error.responseText)
            });
    });

    $(".btnEditSprint").click(function () {
        var sprint_name = $(this).attr("data-test-sprint");
        modal_edit_name.attr('sprint_name', sprint_name);
        $("#inputNewName").val(sprint_name);
        modal_edit_name.modal();
    });

    $("#btnEditNameCancel").click(function () {
            modal_edit_name.modal('hide');
        }
    );

});