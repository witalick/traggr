/**
 * Created by vkhomchak on 2/24/15.
 */

$(document).ready(function () {

    var modal_confirm_delete = $("#ModalConfirmDeletion");
    var modal_edit_name = $("#ModalEditName");

    $("#liAdd").click(function () {
        if ($("#liAdd").hasClass("active")) {
            $("#liAdd").removeClass("active");
        }
        else {
            $("#liAdd").addClass("active");
            addTestCase();
        }
    });

    $("#liAddSprint").click(function(){
        $("#ModalAddSprint").modal()
    });

    $("#formAddSprint").submit(function (event) {
            eventStopPropagation(event);
            var x = document.forms["formAddSprint"].elements;
            var sprint = x['inputSprint'].value.replace(/\s{2,}/g, ' ').trim().replace(' ', '_');
            if (confirm("Do You Really Want To Create New Sprint - " + sprint + "?")) {
                $.ajax({
                    type: "POST",
                    url: "/manual/" + pageData.project + "/" + "sprint",
                    data: JSON.stringify({'sprint_name': sprint}),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json"
                })
                    .success(function () {
                        $("#ModalAddSprint").modal('hide');
                        window.location.reload()
                    })
                    .fail(function (error) {
                        alert(error.responseText)
                    });
            }
            else {
                $("#ModalAddSprint").modal('hide');
            }
        }
    );

    $("#btnAddSprintCancel").click(function(){
        $("#ModalAddSprint").modal('hide');
    });

    $("#btnConfirmDeletion").click(function () {
        var component = modal_confirm_delete.attr('component');
        $("#li" + component.replace(' ', '-')).remove();
        var url = "/manual/" + pageData.project;
        $.ajax({
            type: "DELETE",
            url: url,
            data: JSON.stringify({'component': component}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        })
            .success(function () {
                modal_confirm_delete.removeAttr('component');
            })
            .fail(function (error) {
                alert(error.responseText)
            });
    });

    $(".btnRemoveManualComponent").click(function () {
        var component = $(this).attr("data-test-component");
        modal_confirm_delete.attr('component', component);
        $("#divBodyConfirmDeletion").text("Remove " + component + "?");
        modal_confirm_delete.modal();
    });

    $("#formEditName").submit(function (event) {
        eventStopPropagation(event);
        var x = document.forms["formEditName"].elements;
        var new_name = x['inputNewName'].value.replace(/\s{2,}/g, ' ').trim();
        var component_name = modal_edit_name.attr('component_name');
        $.ajax({
            type: "POST",
            url: '/manual/_edit_manual_component/'+ pageData.project,
            data: JSON.stringify({
                component: component_name,
                component_new: new_name}),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        })
            .success(function () {
                modal_edit_name.removeAttr('component_name');
                modal_edit_name.modal('hide');
                window.location.reload()
            })
            .fail(function (error) {
                alert(error.responseText)
            });
    });

    $(".btnEditManualComponent").click(function () {
        var component = $(this).attr("data-test-component");
        modal_edit_name.attr('component_name', component);
        $("#inputNewName").val('');
        modal_edit_name.modal();
    });

    $("#btnEditNameCancel").click(function () {
            modal_edit_name.modal('hide');
        }
    );
});