{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        silver
    {%- else -%}
        {{ custom_schema_name }}
    {%- endif -%}
{%- endmacro %}
