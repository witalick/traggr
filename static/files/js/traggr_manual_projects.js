/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    $("#liAdd").click(function () {
        if ($("#liAdd").hasClass("active")) {
            $("#liAdd").removeClass("active");
            $("#ModalAddProject").hide();
        }
        else {
            $("#liAdd").addClass("active");
            $("#ModalAddProject").modal();
        }
    });

    $("#btnAddProject").click(function () {
            var x = document.forms["formProjectAdd"].elements;
            var project = x['inputProject'].value;
            if (confirm("Do You Really Want To Create New Project - " + project + "?")) {
                $.ajax({
                    type: "POST",
                    url: "/manual",
                    data: JSON.stringify({'project_name': project}),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json"
                })
                    .success(function () {
                        $("#ModalAddProject").modal('hide');
                        window.location.reload()
                    })
                    .fail(function (error) {
                        alert(error.responseText)
                    });
            }
            else {
                $("#ModalAddProject").modal('hide');
                $("#liAdd").removeClass("active")
            }
        }
    );

    $("#btnAddProjectCancel").click(function () {
            $("#ModalAddProject").modal('hide');
            $("#liAdd").removeClass("active")
        }
    );
});