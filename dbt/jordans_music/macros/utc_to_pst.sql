{% macro utc_to_pst(column_name) %}
    datetime({{ column_name }}, 'America/Vancouver')
{% endmacro %}