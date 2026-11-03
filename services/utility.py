import re


class UtilityService:
    def __init__(self):
        print("UtilityService initialized")

    def clean_sql_query(self, text: str) -> str:
        """Strip markdown code blocks, prefixes, and backticks from LLM SQL output."""
        # Remove code fences (```sql ... ```)
        block_pattern = r"```(?:sql|SQL|SQLQuery|mysql|postgresql)?\s*(.*?)\s*```"
        text = re.sub(block_pattern, r"\1", text, flags=re.DOTALL)

        # Remove prefixes like "SQL Query:" or "MySQL:"
        prefix_pattern = r"^(?:SQL\s*Query|SQLQuery|MySQL|PostgreSQL|SQL)\s*:\s*"
        text = re.sub(prefix_pattern, "", text, flags=re.IGNORECASE)

        # Extract the SELECT query if wrapped in other text
        sql_statement_pattern = r"(SELECT.*?;)"
        sql_match = re.search(
            sql_statement_pattern, text, flags=re.IGNORECASE | re.DOTALL
        )
        if sql_match:
            text = sql_match.group(1)

        # Strip backticks
        text = re.sub(r"`([^`]*)`", r"\1", text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        keywords = ["SELECT", "FROM", "WHERE", "GROUP BY"]
        pattern = "|".join(r"\b{}\b".format(k) for k in keywords)
        text = re.sub(f"({pattern})", r"\n\1", text, flags=re.IGNORECASE)

        text = text.strip()
        text = re.sub(r"\n\s*\n", "\n", text)

        return text

