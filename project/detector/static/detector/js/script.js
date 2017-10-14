$(document).ready(function() {
    $("#file_chooser").change(function (event) {
        event.preventDefault();
        $("#image_form").submit();
        $('#error_block').hide();
        $("#images").hide();
        $("#blank_placeholders").show();
    });

    $('#file_chooser').on('click touchstart', function () {
        $(this).val('');
    });

    $("#image_form").submit(function (event) {
        event.preventDefault();
        var data = new FormData($("#image_form").get(0));
        $.ajax({
            url: '/',
            type: 'POST',
            data: data,
            cache: false,
            processData: false,
            contentType: false,
            success: function(data) {
                console.log('upload success');
                $("#progress").show();

                var task_id = data["task_id"];
                console.log('task id: ' + task_id);
                var stop_progress_bar = false;
                var poll = function(){
                    $.ajax({
                        url:'poll_hog_state/',
                        type: 'GET',
                        cache: false,
                        // processData: false,
                        // contentType: false,
                        data: {
                            task_id: task_id
                        },
                        success: function(result) {
                            if (result !== null && result !== undefined) {
                                if (result.length === undefined) {
                                    console.log('1 ' + result)
                                }
                                else {
                                    console.log('2 result len: ' + result.length + ', ' + result[1])
                                }
                                if (result.process_percent == null || result.process_percent === undefined) {
                                    stop_progress_bar = true;
                                    $('#progress_bar').css({'width': 100 + '%'});
                                    $('#progress_bar').html(100 + '%');

                                    console.log('!' + result.length);
                                    $("#original_image").attr('src', result[1]);
                                    $("#original_image").attr('onclick', "window.open('" + result[1] + "', '_blank')");

                                    $("#hog_image").attr('src', result[2]);
                                    $("#hog_image").attr('onclick', "window.open('" + result[2] + "', '_blank')");
                                } else {
                                    $('#progress_bar').css({'width': result.process_percent + '%'});
                                    $('#progress_bar').html('Processing: ' + result.process_percent + '%');
                                }
                            } else {
                                console.log('!!!')
                            }
                        }

                    });
                };
                var refreshIntervalId = setInterval(function() {
                    poll();
                    if(stop_progress_bar) {
                        clearInterval(refreshIntervalId);
                        $("#progress").hide();
                        $("#images").show();
                        $("#blank_placeholders").hide();
                    }
                },500);
            },
            error: function (result) {
                var error_message = result['responseText'];
                console.log(error_message);
                $('#error_block').html(error_message);
                $('#error_block').show();
            }
        });
    });

    // You need these methods to add the CSRF token using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});