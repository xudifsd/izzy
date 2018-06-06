window.room = (function() {
    var refresh_handler = "";
    var my_name = "";

    function refresh() {
        $.ajax({
            type: "GET",
            url: "status",
            success: function (response) {
                window.status_response = response
                refresh_people(response);
                if (response.hasOwnProperty("table")) {
                    draw_broad(response["table"]);
                }
                console.log("success " + response);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log("failed to get " + xhr.status + ", " + thrownError);
            }
        });
    }

    function make_move(row, col) {
        $.ajax({
            type: "POST",
            url: "move",
            data: {"row": row, "col": col},
            success: function (response) {
                window.move_response = response
                if (response["status"] === "finished") {
                    alert("you win!");
                } // TODO alert other player
                console.log("success move " + response);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log("failed to get " + xhr.status + ", " + thrownError);
            }
        });
    }

    function get_my_name() {
        $.ajax({
            type: "GET",
            url: "/my-name",
            success: function (response) {
                $("#me-name").text(response["name"]);
                my_name = response["name"];
            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log("failed to get " + xhr.status + ", " + thrownError);
            }
        });
    }

    function refresh_people(response) {
        var other_name = "";
        if (response["players"].length === 2) {
            if (response["players"][0] === my_name) {
                other_name = response["players"][1];
            } else {
                other_name = response["players"][0];
            }
            $("#other-name").text(other_name);
        }

        if (response["status"] === "waiting") {
            $("#me-status").text("waiting other");
        } else if (response["status"] === "playing") {
            if (response["current"] === my_name) {
                $("#me-status").text("your turn");
                $("#other-status").text("waiting your move");
            } else {
                $("#other-status").text("thinking");
                $("#me-status").text("waiting play");
            }
        } else if (response["status"] === "finished") {
            var winner = response["winner"];
            var is_winner = winner === my_name;
            $("#me-status").text(is_winner ? "winner" : "loser");
            $("#other-status").text(is_winner ? "loser" : "winner");
            clearInterval(refresh_handler);
        } else {
            $("#me-status").text("unknown");
        }
    }

    function generate_slot(value, row, col) {
        var color = "#FFAFA";
        if (value === 1) {
            color = "#696969";
        } else if (value === 2) {
            color = "#FFA54F";
        }
        return "<td class='slot' style='background-color: "
            + color + "' data-row='" + row + "' data-col='" + col + "'></td>";
    }

    function draw_broad(array) {
        $("#broad").empty();
        var content = "";

        for (var i = 0; i < array.length; i++) {
            var row = "<tr>";
            for (var j = 0; j < array[i].length; j++) {
                row += generate_slot(array[i][j], i, j);
            }
            row += "</tr>"
            content += row;
        }
        $("#broad").append(content);

        var all_slots = $(".slot");
        for (var i = 0; i < all_slots.length; i++) {
            var node = $(all_slots[i]);
            node.click(function() {
                var data = $(this).data();
                console.log(data.row + "," + data.col);

                make_move(data.row, data.col);
            });
        }
    }

    function room_start() {
        get_my_name();
        refresh();

        refresh_handler = setInterval(refresh, 300);
    }

    return {"start": room_start, "make_move": make_move};
})();
