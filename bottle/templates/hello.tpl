{% extends "templates/master.tpl" %}
{% block content %}
    <p>Lorem ipsum dolor sit amet, consecteteur adipiscing elit nisi ultricies. Condimentum vel, at augue nibh sed. Diam praesent metus ut eros, sem penatibus. Pellentesque. Fusce odio posuere litora non integer habitant proin. Metus accumsan nibh facilisis nostra lobortis cum diam tellus. Malesuada nostra a volutpat pede primis congue nisl feugiat in fermentum. Orci in hymenaeos. Eni tempus mi mollis lacinia orci interdum lacus. Sollicitudin aliquet, etiam. Ac. Mi, nullam ligula, tristique penatibus nisi eros nisl pede pharetra congue, aptent nulla, rhoncus tellus morbi, ornare. Magna condimentum erat turpis. Fusce arcu ve suscipit nisi phasellus rutrum a dictumst leo, laoreet dui, ultricies platea. Porta venenatis fringilla vestibulum arcu etiam condimentum non.</p>
    
    {#
    <table border="1">
        {% for k, v in request.environ.iteritems() %}
            <tr><td>{{ k | escape }}</td><td>{{ v | escape }}</td></tr>
        {% endfor %}
    </table>
    #}
{% endblock %}
