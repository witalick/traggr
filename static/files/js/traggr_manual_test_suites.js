/**
 * Created by vkhomchak on 2/24/15.
 */
$(document).ready(function () {

    document.body.style.cursor = 'wait';

    window.onload = function () {
        document.body.style.cursor = 'default';
    };

    var modal_confirm_delete = $("#ModalConfirmDeletion");
    var modal_edit_name = $("#ModalEditName");

    $("#liAdd").click(function () {
        if ($("#liAdd").hasClass("active")) {
            $("#liAdd").removeClass("active");
        }
        else {
            $("#liAdd").addClass("active");
            addTestCase(false, pageData.component)
        }
    });

    $("#btnConfirmDeletion").click(function () {
        var test_id = modal_confirm_delete.attr('test_id'),
            suite = modal_confirm_delete.attr('suite');

        if (test_id || suite) {
            if (test_id){$("#td" + test_id).remove();}
            else{$("#div" + suite.replace(' ', '-')).remove();}

            var url = "/manual/" + pageData.project + "/" + pageData.component;
            var data = {'suite': suite};
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
            .success(function () {
                    modal_confirm_delete.removeAttr('test_id');
                    modal_confirm_delete.removeAttr('suite');
                })
            .fail(function (error) {alert(error.responseText)});
        }

    });

    window.removeManualTestOrSuiteWithConfirmation = function (suite, test_id) {
        modal_confirm_delete.attr('suite', suite);
        modal_confirm_delete.attr('test_id', test_id);

        if (test_id){
            $("#divBodyConfirmDeletion").text("Remove " + test_id + "?");
        }
        else {
            $("#divBodyConfirmDeletion").text("Remove " + suite + "?");
        }
        modal_confirm_delete.modal();
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

    $("#formEditName").submit(function (event) {
        event.preventDefault();
        var x = document.forms["formEditName"].elements;
        var new_name = x['inputNewName'].value.replace(/\s{2,}/g, ' ').trim();
        var suite_name = modal_edit_name.attr('suite_name');
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
                modal_edit_name.removeAttr('suite_name');
                modal_edit_name.modal('hide');
                window.location.reload()
            })
            .fail(function (error) {
                alert(error.responseText)
            });

    });

    window.editSuiteName = function (event, suite_name) {
        event = event || window.event;
        event.preventDefault();
        event.stopPropagation();
        modal_edit_name.attr('suite_name', suite_name);
        modal_edit_name.modal();
    };

    $("#btnEditNameCancel").click(function () {
            modal_edit_name.modal('hide');
        }
    );

});