import re
import ast

class QueryParser:
    @staticmethod
    def _parse_props(props_str):
        if not props_str: return {}
        # Quote unquoted keys (e.g. {name: "Alice"} -> {"name": "Alice"})
        props_str = re.sub(r'(\w+):', r'"\1":', props_str)
        return ast.literal_eval(props_str)

    @staticmethod
    def parse_create_node(query):
        pattern = r"CREATE NODE \((\w+):(\w+)\s*({.*?})\)"
        match = re.match(pattern, query)
        if match:
            alias, label, props_str = match.groups()
            props = QueryParser._parse_props(props_str)
            return {"type": "CREATE_NODE", "alias": alias, "label": label, "props": props}
        return None

    @staticmethod
    def parse_create_edge(query):
        pattern = r"CREATE EDGE \((\w+)\)-\[:(\w+)\s*({.*?})?\]->\((\w+)\)"
        match = re.match(pattern, query)
        if match:
            from_alias, edge_type, props_str, to_alias = match.groups()
            props = QueryParser._parse_props(props_str)
            return {"type": "CREATE_EDGE", "from": from_alias, "to": to_alias, "edge_type": edge_type, "props": props}
        return None

    @staticmethod
    def parse_match(query):
        parts = re.split(r"(WHERE|RETURN)", query, flags=re.IGNORECASE)
        match_clause = parts[0].strip()
        where_clause = parts[2].strip() if "WHERE" in query.upper() else ""
        return_clause = parts[-1].strip() if "RETURN" in query.upper() else ""
        
        return {
            "type": "MATCH",
            "match": match_clause,
            "where": where_clause,
            "return": return_clause
        }

    @staticmethod
    def parse_shortest_path(query):
        pattern = r"SHORTEST_PATH \((\w+)\)-\[.*?\]->\((\w+)\)"
        match = re.match(pattern, query)
        if match:
            return {"type": "SHORTEST_PATH", "start": match.group(1), "end": match.group(2)}
        return None
