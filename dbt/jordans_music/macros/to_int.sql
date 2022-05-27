{% macro to_int(column_name) %}
    cast({{ column_name }} as int)
{% endmacro %}