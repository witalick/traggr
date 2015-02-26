/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    var modal_confirm_delete = $("#ModalConfirmDeletion");
    var modal_confirm_sync = $("#ModalConfirmSysnc");

    $("#spanContextFailed").click(function () {
        if ($("#failedTestsList").is(":visible")) {
            $("#failedTestsList").hide();
        } else {
            $("#failedTestsList").show();
        }
    });

    $("#btnConfirmDeletion").click(function () {
        var component = modal_confirm_delete.attr('component');
        $("#li" + component.replace(/\s/g, '-')).remove();
        $.ajax({type: "DELETE",
            url: "/manual/" + pageData.project + "/" + "sprint/" + pageData.sprint,
            data: JSON.stringify({'component': component})
        })
            .success(function () {
                modal_confirm_delete.removeAttr('component');
                modal_confirm_delete.modal('hide')
            })
            .fail(function (error) {alert(error.responseText)});
    });

    $(".btnRemoveSprintComponent").click(function () {
        var component = $(this).attr("data-test-component");
        modal_confirm_delete.attr('component', component);
        $("#divBodyConfirmDeletion").text("Remove " + component + "?");
        modal_confirm_delete.modal();
    });

    $("#btnConfirmSync").click(function() {
        $.ajax({
            type: "POST",
            url: "/manual/_sync_sprint/" + pageData.project + "/" + pageData.sprint
        })
            .success(function () {
                modal_confirm_sync.modal('hide');
                window.location.reload()})
            .fail(function (error) {alert(error.responseText)});
    });

    $("#liSyncSprint").click(function(){
        $("#divBodyConfirmSync").text('Do You really what to Sync This Sprint with Test Cases ?');
        modal_confirm_sync.modal();
    });

});