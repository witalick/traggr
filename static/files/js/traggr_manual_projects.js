/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    var modal_add_project = $("#ModalAddProject");

    $("#liAdd").click(function () {
        if ($("#liAdd").hasClass("active")) {
            $("#liAdd").removeClass("active");
            modal_add_project.hide();
        }
        else {
            $("#liAdd").addClass("active");
            modal_add_project.modal();
        }
    });

    $("#formAddProject").submit(function (event) {
            eventStopPropagation(event);
            var x = document.forms["formAddProject"].elements;
            var project = x['inputProject'].value.replace(/\s{2,}/g, ' ').trim().replace(' ', '_');
            if (confirm("Do You Really Want To Create New Project - " + project + "?")) {
                $.ajax({
                    type: "POST",
                    url: "/manual",
                    data: JSON.stringify({'project_name': project}),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json"
                })
                    .success(function () {
                        modal_add_project.modal('hide');
                        window.location.reload()
                    })
                    .fail(function (error) {
                        alert(error.responseText)
                    });
            }
            else {
                modal_add_project.modal('hide');
                $("#liAdd").removeClass("active")
            }
        }
    );

    $("#btnAddProjectCancel").click(function () {
            modal_add_project.modal('hide');
            $("#liAdd").removeClass("active")
        }
    );
});