from __future__ import annotations


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    columns = [str(header) for header in headers]
    widths = [len(header) for header in columns]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(str(cell)))
    lines = []
    lines.append("  ".join(columns[i].ljust(widths[i]) for i in range(len(columns))).rstrip())
    lines.append("  ".join("-" * widths[i] for i in range(len(columns))))
    for row in rows:
        cells = [str(row[i]).ljust(widths[i]) for i in range(len(columns))]
        lines.append("  ".join(cells).rstrip())
    return "\n".join(lines)
