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

    $("#btnConfirmDeletion").on("click", function () {
        var test_id = modal_confirm_delete.attr('test_id'),
            suite = modal_confirm_delete.attr('suite');

        if (test_id || suite) {
            if (test_id){$("#tr" + test_id).remove();}
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

    $(".table-test-cases").on('click', ".btnRemoveManualTestCaseOrSuite", function () {
        var el = $(this);
        var suite = el.attr('data-test-suite'),
            test_id = el.attr('data-test-test_id');
        modal_confirm_delete.attr('suite', suite);
        modal_confirm_delete.attr('test_id', test_id);

        if (test_id){
            $("#divBodyConfirmDeletion").text("Remove " + test_id + "?");
        }
        else {
            $("#divBodyConfirmDeletion").text("Remove " + suite + "?");
        }
        modal_confirm_delete.modal();
    });

    $(".table-test-cases").on('click', ".btnEditManualTestCase", function (event) {
        var test_id = $(this).attr('data-test-test_id'),
            suite = $(this).attr('data-test-suite');
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
                addTestCase(event, true, suite, test_id, true);
            })
            .fail(function (error) {
                alert(error.responseText)
            });

    });

    $(".btnAddOneTestCase").on('click', function(event){
        var el = $(this);
        var suite = el.attr('data-test-suite'),
            component = el.attr('data-test-component');
        addTestCase(event, component, suite, false, true);

    });

    $(document).on('new_test_case_added', function(event, test_id, suite, title){
        var last_tr = $("#table" + suite.replace(" ", "-") + " tr:last-child");
        var new_tr = last_tr.clone();
        new_tr.attr('id', 'tr' + test_id);
        new_tr.find('button[data-test-test_id]').attr('data-test-test_id', test_id);
        new_tr.find('button[data-test-suite]').attr('data-test-suite', suite);
        var second_td = new_tr.find('td[data-target]');
        second_td.attr('data-target', '#Modal' + suite.replace(" ", "-") + test_id);
        second_td.text(title);
        new_tr.find('.spTest_id').text(test_id);
        new_tr.insertAfter(last_tr)
    });


    $(document).on('test_case_edited', function(event, test_id, suite, title){
        var table = $("#table" + suite.replace(" ", "-"));
        var second_td = table.find('td[data-target]');
        second_td.text(title);
    });

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

    $(".btnEditSuiteName").click(function (event) {
        event = event || window.event;
        event.preventDefault();
        event.stopPropagation();
        var suite = $(this).attr('data-test-suite');
        modal_edit_name.attr('suite_name', suite);
        $("#inputNewName").val('');
        modal_edit_name.modal();
    });

    $("#btnEditNameCancel").click(function () {
            modal_edit_name.modal('hide');
        }
    );

});