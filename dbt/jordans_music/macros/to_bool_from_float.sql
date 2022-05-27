{% macro to_bool_from_float(column_name) %}
    cast(cast({{column_name}} as int) as bool)
{% endmacro %}

