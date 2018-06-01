var add_log = function(data) {
    // $("div#log").data(data);
};

var get_room_status = function() {
    $.get("status", add_log);
    $.ajax({
        type: "GET",
        url: "status",
        success: function (response) {
            window.response = response;
            console.log("success " + response);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.log("failed to get " + xhr.status + ", " + thrownError);
        }
    });
};

var room_start = function() {
    get_room_status();
    setInterval(get_room_status, 1000);
};
