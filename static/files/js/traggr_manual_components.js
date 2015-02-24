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

});