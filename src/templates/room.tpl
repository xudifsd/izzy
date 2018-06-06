<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <title>Gomoku Room {{ room_id }}</title>
    <link rel="stylesheet" href="/static/izzy.css">
    <script type="text/javascript" src="http://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js">
    </script>
    <script type="text/javascript" src="/static/room.js">
    </script>
    <script type="text/javascript">
        $(document).ready(function() {
            $("#page").css("display", "block");
            $("#loading").css("display", "none");

            window.room.start();
        });
    </script>
</head>
<body>

<div id="loading">
    <div class="center">loading</div>
</div>

<div id="page">
    <div style="position: absolute; top: 20px;"><a href="/">Home</a></div>

    <div class="center" style="width:600px; height:600px; background-color:#f8f8f8">
        <table id="broad">
        </table>
    </div>

    <div id="me" class="people-info" style="position: absolute; bottom: 10px; left: 10px; border: 0;">
    <table>
        <tr>
            <td id="me-name"></td>
        </tr>
        <tr>
            <td id="me-status"></td>
        </tr>
    </table>
    </div>

    <div id="other" class="people-info" style="position: absolute; top: 10px; right: 10px; border: 0;">
    <table>
        <tr>
            <td id="other-name"></td>
        </tr>
        <tr>
            <td id="other-status"></td>
        </tr>
    </table>
    </div>
</div>

</body>
</html>
