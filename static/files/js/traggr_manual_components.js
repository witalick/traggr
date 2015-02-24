/**
 * Created by vkhomchak on 2/24/15.
 */

$(document).ready(function () {

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

    $("#btnAddSprint").click(function () {
            var x = document.forms["formAddSprint"].elements;
            var sprint = x['inputSprint'].value;
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

    window.removeManualComponentWithConfirmation = function (component) {
        $("#btnConfirmDeletion").click(function () {
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
//                            window.location.reload()
                })
                .fail(function (error) {
                    alert(error.responseText)
                });
        });

        $("#divBodyConfirmDeletion").text("Remove " + component + "?");
        $("#ModalConfirmDeletion").modal();

    };
    window.editComponentName = function (component_name) {
        $("#ModalEditName").modal();
        $("#btnEditName").click(function () {
            var x = document.forms["formEditName"].elements;
            var new_name = x['inputNewName'].value.replace(/\s{2,}/g, ' ').trim();
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
                    $("#ModalEditName").modal('hide');
                    window.location.reload()
                })
                .fail(function (error) {
                    alert(error.responseText)
                });

        });
    };

    $("#btnEditNameCancel").click(function () {
            $("#ModalEditName").modal('hide');
        }
    );
});