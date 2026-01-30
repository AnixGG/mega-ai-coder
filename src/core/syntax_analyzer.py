from tree_sitter_languages import get_language, get_parser
import re
from typing import Dict, List, Optional, Tuple


class SyntaxAnalyzer:
    EXT_TO_LANG = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
    }

    QUERIES = {
        "python": """
            (function_definition name: (identifier) @name) @def
            (class_definition name: (identifier) @name) @def
            (async_function_definition name: (identifier) @name) @def
        """,
        "javascript": """
            (function_declaration name: (identifier) @name) @def
            (class_declaration name: (identifier) @name) @def
            (method_definition name: (property_identifier) @name) @def
            (arrow_function) @def
        """,
        "typescript": """
            (function_declaration name: (identifier) @name) @def
            (class_declaration name: (type_identifier) @name) @def
            (method_definition name: (property_identifier) @name) @def
            (interface_declaration name: (type_identifier) @name) @def
            (type_alias_declaration name: (type_identifier) @name) @def
        """,
        "go": """
            (function_declaration name: (identifier) @name) @def
            (method_declaration name: (field_identifier) @name) @def
            (type_declaration (type_spec name: (type_identifier) @name)) @def
        """,
        "rust": """
            (function_item name: (identifier) @name) @def
            (struct_item name: (type_identifier) @name) @def
            (impl_item) @def
            (trait_item name: (type_identifier) @name) @def
        """,
        "java": """
            (class_declaration name: (identifier) @name) @def
            (method_declaration name: (identifier) @name) @def
            (interface_declaration name: (identifier) @name) @def
        """,
        "cpp": """
            (class_specifier name: (type_identifier) @name) @def
            (function_definition declarator: (function_declarator declarator: (identifier) @name)) @def
        """,
        "c": """
            (function_definition declarator: (function_declarator declarator: (identifier) @name)) @def
            (struct_specifier name: (type_identifier) @name) @def
        """
    }

    @classmethod
    def get_language_name(cls, filename: str) -> Optional[str]:
        match = re.search(r'\.\w+$', filename)
        if match:
            ext = match.group()
            return cls.EXT_TO_LANG.get(ext)

        if filename == "Dockerfile":
            return None
        elif filename.endswith("Makefile") or filename.endswith("makefile"):
            return None
        elif filename.endswith(".gitignore"):
            return None

        return None

    @staticmethod
    def get_backbone(code: str, filename: str) -> str:
        lang_name = SyntaxAnalyzer.get_language_name(filename)

        if not lang_name:
            lines = code.splitlines()[:20]
            if len(lines) == 20:
                lines.append("...")
            return "\n".join(lines)

        try:
            language = get_language(lang_name)
            if not language:
                return f"Language {lang_name} not supported by tree-sitter"

            parser = get_parser(lang_name)
            if not parser:
                return f"Parser for {lang_name} not available"

            tree = parser.parse(bytes(code, "utf8"))

            query_scm = SyntaxAnalyzer.QUERIES.get(lang_name)
            if not query_scm:
                return f"Parsed as {lang_name}, but no skeleton query defined."

            query = language.query(query_scm)
            captures = query.captures(tree.root_node)

            signatures = []
            seen_nodes = set()

            for node, tag in captures:
                if tag == "def":
                    node_id = (node.start_byte, node.end_byte)
                    if node_id in seen_nodes:
                        continue
                    seen_nodes.add(node_id)

                    start_line = node.start_point[0]
                    end_line = min(node.start_point[0] + 3, node.end_point[0])

                    code_lines = code.splitlines()
                    if start_line < len(code_lines):
                        signature_lines = []
                        for i in range(start_line, min(start_line + 3, len(code_lines), end_line + 1)):
                            line = code_lines[i].rstrip()
                            if line:
                                signature_lines.append(line)
                            if i == end_line or '}' in line or '):' in line or line.endswith('{'):
                                break

                        signature = " ".join(signature_lines[:3])
                        if len(signature) > 150:
                            signature = signature[:147] + "..."

                        signatures.append(f"L{start_line + 1}: {signature}")

            if not signatures:
                lines = code.splitlines()[:10]
                if lines:
                    return f"No structural definitions found. First lines:\n" + "\n".join(lines)
                return "File is empty"

            signatures.sort(key=lambda x: int(x.split(':')[0][1:]))

            result = [f"=== {filename} ({lang_name}) ==="]
            result.extend(signatures)

            result.append(f"\nTotal definitions: {len(signatures)}")
            result.append(f"Total lines: {len(code.splitlines())}")

            return "\n".join(result)

        except Exception as e:
            error_msg = f"Error parsing {filename} as {lang_name}: {str(e)[:100]}"

            lines = code.splitlines()
            if len(lines) > 30:
                return f"{error_msg}\n\nFirst 30 lines:\n" + "\n".join(lines[:30])
            elif lines:
                return f"{error_msg}\n\nContent:\n" + code
            else:
                return f"{error_msg}\n\nFile is empty"

    @staticmethod
    def get_file_summary(code: str, filename: str) -> Dict:
        backbone = SyntaxAnalyzer.get_backbone(code, filename)

        lines = code.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]

        return {
            "filename": filename,
            "language": SyntaxAnalyzer.get_language_name(filename),
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty_lines),
            "backbone": backbone,
            "has_definitions": "L" in backbone,
        }

    @staticmethod
    def analyze_multiple_files(file_contents: List[Tuple[str, str]]) -> str:
        results = []

        for filename, code in file_contents:
            summary = SyntaxAnalyzer.get_file_summary(code, filename)

            results.append(f"📁 {filename}")
            results.append(f"   Language: {summary['language'] or 'Unknown'}")
            results.append(f"   Lines: {summary['total_lines']} ({summary['non_empty_lines']} non-empty)")

            backbone_lines = summary['backbone'].split('\n')
            if len(backbone_lines) > 8:
                results.extend(["   Structure:"] + [f"     {line}" for line in backbone_lines[:8]])
                results.append(f"     ... and {len(backbone_lines) - 8} more lines")
            else:
                results.extend(["   Structure:"] + [f"     {line}" for line in backbone_lines])

            results.append("")

        return "\n".join(results)
