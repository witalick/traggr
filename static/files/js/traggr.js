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
    window.eventStopPropagation = function(event){
        event = event || window.event;
        event.preventDefault();
        event.stopPropagation();
    };

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
        eventStopPropagation(event);
        var component = modal_add_test_case.attr('component'),
            suite = modal_add_test_case.attr('suite'),
            test_id = modal_add_test_case.attr('test_id'),
            dont_reload = modal_add_test_case.attr('dont_reload');
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
        component = component.replace(/\s{2,}/g, ' ').trim();
        suite = suite.replace(/\s{2,}/g, ' ').trim();
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
            .success(function (data) {
                modal_add_test_case.removeAttr('component');
                modal_add_test_case.removeAttr('suite');
                modal_add_test_case.removeAttr('test_id');
                modal_add_test_case.modal('hide');
                if (dont_reload && data['test_id']) {
                    $(document).trigger('new_test_case_added', [data['test_id'], suite, title]);
                }
                else if(dont_reload && test_id){
                    $(document).trigger('test_case_edited', [test_id, suite, title]);
                }
                else{
                    window.location.reload()
                }

            })
            .fail(function (error) {
                alert(error.responseText)
            });
    });

    window.addTestCase = function (event, component, suite, test_id, dont_reload) {
        if (event) {
            eventStopPropagation(event);
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
        if (dont_reload){
            modal_add_test_case.attr('dont_reload', dont_reload)
        }
        modal_add_test_case.modal();
    };

    $("#btnAddTestCaseCancel").click(function () {
            modal_add_test_case.modal('hide');
            $("#liAdd").removeClass("active");
        }
    );

});