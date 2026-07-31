FUNCTION_QUERY = """
(
    function_definition
        name: (identifier) @function.name
)
"""

CLASS_QUERY = """
(
    class_definition
        name: (identifier) @class.name
)
"""

IMPORT_QUERY = """
(
    import_statement
) @import

(
    import_from_statement
) @import
"""

METHOD_QUERY = """
(
    function_definition
        name: (identifier) @method.name
)
"""