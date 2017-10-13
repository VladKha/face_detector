$(document).ready(
    function() {
        $("#file_chooser").change(function(event) {
            event.preventDefault();
            $("#submit_button").click();
        });
    }()
);