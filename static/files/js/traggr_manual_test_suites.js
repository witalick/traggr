/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    document.body.style.cursor = 'wait';

    window.onload = function () {
        document.body.style.cursor = 'default';
    };

    $("#liAdd").click(function () {
        if ($("#liAdd").hasClass("active")) {
            $("#liAdd").removeClass("active");
        }
        else {
            $("#liAdd").addClass("active");
            addTestCase(false, pageData.component)
        }
    });

    window.removeManualTestOrSuiteWithConfirmation = function (component, suite, test_id) {
        $("#btnConfirmDeletion").click(function () {
            if (test_id){$("#td" + test_id).remove();}
            else{$("#div" + suite.replace(' ', '-')).remove();}

            var url = "/manual/" + pageData.project + "/" + component;
            var data = {'component': component,
                        'suite': suite};
            if (test_id){
                data['test_id'] = test_id
            }
            $.ajax({
                type: "DELETE",
                url: url,
                data: JSON.stringify(data),
                contentType: "application/json; charset=utf-8",
                dataType: "json"
            })
            .success(function () {})
            .fail(function (error) {alert(error.responseText)});
        });
        if (test_id){
            $("#divBodyConfirmDeletion").text("Remove " + test_id + "?");
            $("#ModalConfirmDeletion").modal();
        }
        else {
            $("#divBodyConfirmDeletion").text("Remove " + suite + "?");
            $("#ModalConfirmDeletion").modal();
        }
    };

    window.editManualTest = function (event, test_id) {
        var test_data = {
            'component': pageData.component,
            'test_id': test_id
        };
        $.ajax({
            type: "POST",
            url: "/manual/_get_manual_test/" + pageData.project,
            data: JSON.stringify(test_data),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        })
            .success(function (data) {
                $("#inputTestTitle").val(data.title);
                $("#inputTestSteps").val(data.steps);
                $("#inputTestExpectedResults").val(data.expected_results);
                $("#modalAddTestCaseText").text("Edit Test Case");
                addTestCase(event, true, true, test_id);
            })
            .fail(function (error) {
                alert(error.responseText)
            });

    };

    window.editSuiteName = function (event, suite_name) {
        event = event || window.event;
        event.preventDefault();
        event.stopPropagation();
        $("#ModalEditName").modal();
        $("#btnEditName").click(function () {
            var x = document.forms["formEditName"].elements;
            var new_name = x['inputNewName'].value.replace(/\s{2,}/g, ' ').trim();
            $.ajax({
                type: "POST",
                url: '/manual/'+ pageData.project + '/' + pageData.component,
                data: JSON.stringify({
                    suite: suite_name,
                    suite_new: new_name}),
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