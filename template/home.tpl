<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <title>Gomoku</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link rel="stylesheet" href="/static/izzy.css">
    <script type="text/javascript" src="http://apps.bdimg.com/libs/jquery/2.1.4/jquery.min.js">
    </script>
</head>
<body>
    <div><a href="/new-room">new room</a></div>

    {% for room in rooms %}
        <div>
            <a href="/room/{{ room['id'] }}/"><span>room {{ room['id']}}</span></a>
        </div>
    {% endfor %}

</body>
</html>

