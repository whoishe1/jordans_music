{% macro datetime_to_date(column_name) %}
    date({{column_name}})
{% endmacro %}