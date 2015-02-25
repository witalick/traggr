/**
 * Created by vkhomchak on 2/24/15.
 */

$(document).ready(function () {

    var modal_add_test_case = $("#ModalAddTestCase");

    $("#liAdmin").click(function () {
        if ($("#liAdmin").hasClass("active")) {
            $("#liAdmin").removeClass("active");
            $(".btnRemove").hide();
            $(".btnRename").hide();
            $(".btnEdit").hide();
            $(".btnSet").hide();
        } else {
            $("#liAdmin").addClass("active");
            $(".btnRemove").show();
            $(".btnRename").show();
            $(".btnEdit").show();
            $(".btnSet").show();
        }
    });

    window.composeTestAddForm = function (component, suite){
         function showHide(id, show) {
             var el = $('#' + id);
            if (show) {
                el.hide();
                el.find('input').removeAttr('required');
            } else {
                 el.show();
                 el.find('input').attr('required', 'required');
            }
         }
        showHide('inputTestComponent-group', component);
        showHide('inputTestSuite-group', suite)
    };

    $("#formAddTestCase").submit(function (event) {
        event.preventDefault();
        var component = modal_add_test_case.attr('component'),
            suite = modal_add_test_case.attr('suite'),
            test_id = modal_add_test_case.attr('test_id');
        var x = document.forms["formAddTestCase"].elements;
        var title = x['inputTestTitle'].value.replace(/\s{2,}/g, ' ').trim();
        var steps = x['inputTestSteps'].value;
        var expected_results = x['inputTestExpectedResults'].value;
        var test_data = {
            'other_attributes': {
                'title': title,
                'steps': steps,
                'expected_results': expected_results
            }
        };
        if (!component){
            component =  !pageData.component ? x['inputTestComponent'].value: pageData.component
        }
        if (!suite){
            suite = x['inputTestSuite'].value;
        }
        test_data['component'] = component;
        test_data['suite'] = suite;
        var url = "/manual/" + pageData.project;

        if (test_id){
            url = "/manual/_edit_manual_test/" + pageData.project;
            test_data['test_id'] = test_id
        }

        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify(test_data),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        })
            .success(function () {
                modal_add_test_case.removeAttr('component');
                modal_add_test_case.removeAttr('suite');
                modal_add_test_case.removeAttr('test_id');
                modal_add_test_case.modal('hide');
                window.location.reload()
            })
            .fail(function (error) {
                alert(error.responseText)
            });
    });

    window.addTestCase = function (event, component, suite, test_id) {
        if (event) {
            event = event || window.event;
            event.preventDefault();
            event.stopPropagation();
        }
        composeTestAddForm(component, suite);
        if (!test_id){
            $("#modalAddTestCaseText").text("Add Test Case");
            $("#inputTestTitle").val('');
            $("#inputTestSteps").val('');
            $("#inputTestExpectedResults").val('');
        }
        modal_add_test_case.attr('component', component);
        modal_add_test_case.attr('suite', suite);
        if (test_id){
            modal_add_test_case.attr('test_id', test_id)
        }
        modal_add_test_case.modal();
    };

    $("#btnAddTestCaseCancel").click(function () {
            modal_add_test_case.modal('hide');
            $("#liAdd").removeClass("active");
        }
    );

});