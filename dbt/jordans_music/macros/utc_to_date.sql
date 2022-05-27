{% macro utc_to_date(column_name) %}
    datetime(timestamp({{ column_name }}))
{% endmacro %}