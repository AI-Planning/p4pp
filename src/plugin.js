
var ALIGNMENT_SITE = "http://localhost/";

var PDDL_ALIGNMENT_MODAL = "\
<div class=\"modal fade\" id=\"alignmentModal\" tabindex=\"-1\" role=\"dialog\" aria-labelledby=\"alignmentModalLabel\" aria-hidden=\"true\">\
  <div class=\"modal-dialog modal-sm\">\
    <div class=\"modal-content\">\
      <div class=\"modal-header\">\
        <button type=\"button\" class=\"close\" data-dismiss=\"modal\"><span aria-hidden=\"true\">&times;</span><span class=\"sr-only\">Close</span></button>\
        <h4 class=\"modal-title\" id=\"alignmentModalLabel\">Choose Problem to Align</h4>\
      </div>\
      <div id=\"alignmentModalContent\" class=\"modal-body\">\
      </div>\
      <div class=\"modal-footer\">\
        <button type=\"button\" class=\"btn btn-default\" data-dismiss=\"modal\">Close</button>\
      </div>\
    </div>\
  </div>\
</div>\
";

function alignProblem() {

    window.align_domain_text = window.ace.edit($('#domainSelection').find(':selected').val()).getSession().getValue();
    window.align_problem_text = window.ace.edit($('#problemSelection').find(':selected').val()).getSession().getValue();

    // Get the problems available on the server
    $.ajax({
        url: ALIGNMENT_SITE + "problems/",
        type: "GET",
        contentType: 'application/json'
    }).done(function (res) {
        console.log("server sucesses", res);
        var problems = res.problems;

        var html = '';

        html += '<form class="form-horizontal">';

        // bootstrap-select
        html += '<div class="form-group">';
        html += '  <label for="alignmentProblemSelection" class="col-sm-4 control-label">Problem</label>';
        html += '  <div class="col-sm-4">';
        html += '    <select id="alignmentProblemSelection" class="selectpicker" data-live-search="true">';
        for (var i = 0; i < problems.length; i++) {
            html += '      <option value="' + problems[i] + '">' + problems[i] + '</option>';
        }
        html += '    </select>';
        html += '  </div>';
        html += '</div>';
        html += '<br/>';
        html += '<button style="margin-left:26px" type="button" onclick="doAlignment(); return false;" class="btn btn-primary btn-lg">Align</button>';
        html += '</form>';

        $('#alignmentModalContent').html(html);

        $('#alignmentModal').modal('toggle');

    }).fail(function (res) {
        window.toastr.error('Error: Malformed URL?');
        console.log('server fail', res);
    });

    $('#chooseFilesModal').modal('toggle');
}

function doAlignment() {

    var problem = $('#alignmentProblemSelection').find(':selected').val();

    window.toastr.info('Running alignment...');

    // Get the problems available on the server
    $.ajax({
        url: ALIGNMENT_SITE + "align/" + problem + "/",
        type: "POST",
        contentType: 'application/json',
        data: JSON.stringify({"domain": window.align_domain_text, "problem": window.align_problem_text})
    }).done(function (res) {
        console.log("server sucesses", res);
        if (res.status === 'success') {
            window.toastr.success('Alignment complete!');
            showAlignment(res.result);
        } else if (res.status === 'error') {
            window.toastr.error('Error: ' + res.error);
        } else
            window.toastr.error('Problem with the server.');

    }).fail(function (res) {
        window.toastr.error('Error: Malformed URL?');
        console.log('server fail', res)
    });

    $('#alignmentModal').modal('toggle');
}


function showAlignment(output) {

    var tab_name = 'Alignment (' + (Object.keys(window.alignments).length + 1) + ')';

    window.new_tab(tab_name, function(editor_name) {
        window.alignments[editor_name] = output;
        var plan_html = '';
        plan_html += '<div class=\"plan-display\">\n';
        plan_html += '<h2>Alignment Result</h2>\n';
        plan_html += '<pre class=\"plan-display-action well\">\n';
        plan_html += output;
        plan_html += '</pre>';
        $('#' + editor_name).html(plan_html);
    });

}

define(function () {

    // Create a store for the Action-usability analysis done
    window.alignments = {};

    return {

        name: "Theory Alignment",
        author: "Christian Muise",
        email: "christian.muise@gmail.com",
        description: "Plugin to align local domain/problem with a remote reference.",

        // This will be called whenever the plugin is loaded or enabled
        initialize: function() {

            // Add our button to the top menu
            window.add_menu_button('Problem Alignment', 'AlignmentMenuItem', 'glyphicon-random', "chooseFiles('Alignment')");

            // Register this as a user of the file chooser interface
            window.register_file_chooser('Alignment',
            {
                showChoice: function() {
                    window.setup_file_chooser('Align', 'Align Problem');
                    $('#plannerURLInput').hide();
                },
                selectChoice: alignProblem
            });

            $('body').append(PDDL_ALIGNMENT_MODAL);
        },

        // This is called whenever the plugin is disabled
        disable: function() {
            window.remove_menu_button('AlignmentMenuItem');
        },

        save: function() {
            // Used to save the plugin settings for later
            return {};
        },

        load: function(settings) {
            // Restore the plugin settings from a previous save call
        }

    };
});
