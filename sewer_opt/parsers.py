import pandas as pd
import re

def parse_sewer_file(filepath):
    """
    Parse the same file format as CedritosNorte.txt
    Returns:
        nodes_df: DataFrame with columns ['id','flow','x','y','elevation']
        edges_df: DataFrame with columns ['u','v']
    """
    with open(filepath, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    # find "Manholes" line index
    idx = 0
    if not lines[0].lower().startswith("manholes"):
        raise ValueError("File must start with 'Manholes <count>'")
    manholes_count = int(lines[0].split()[1])
    manhole_lines = lines[1: 1 + manholes_count]

    nodes = []
    for ln in manhole_lines:
        parts = ln.split()
        if len(parts) < 5:
            raise ValueError("Expected 5 columns in manholes rows")
        nid = int(parts[0])
        flow = float(parts[1])
        x = float(parts[2])
        y = float(parts[3])
        elev = float(parts[4])
        nodes.append((nid, flow, x, y, elev))
    nodes_df = pd.DataFrame(nodes, columns=["id", "flow", "x", "y", "elevation"]).set_index("id")

    # next line after manholes block should be "Sections <count>"
    sec_line_idx = 1 + manholes_count
    if not lines[sec_line_idx].lower().startswith("sections"):
        raise ValueError("Expected 'Sections <count>' after Manholes block")
    sec_count = int(lines[sec_line_idx].split()[1])
    section_lines = lines[sec_line_idx + 1: sec_line_idx + 1 + sec_count]

    edges = []
    for ln in section_lines:
        parts = ln.split()
        if len(parts) < 2:
            continue
        u, v = int(parts[0]), int(parts[1])
        edges.append((u, v))
    edges_df = pd.DataFrame(edges, columns=["u", "v"])
    return nodes_df, edges_df


def _split_cols(line: str):
    """Split a line by whitespace/tabs but preserve negative signs and decimals."""
    return re.split(r'\s+', line.strip())

def parse_sewer_file_1(filepath: str):
    """
    Parse a sewer network .txt file in the 'CedritosNorte' or 'Li' format.

    Returns:
        nodes_df: DataFrame indexed by 'id' with columns ['flow','x','y','elevation']
        edges_df: DataFrame with columns ['u','v']
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    # ---- MANHOLES BLOCK ----
    idx = 0
    while idx < len(lines) and not lines[idx].lower().startswith("manholes"):
        idx += 1
    if idx >= len(lines):
        raise ValueError("File must start with 'Manholes <count>'")
    manholes_count = int(_split_cols(lines[idx])[1])

    # detect header row (like: ID X Y Z INFLOW)
    manhole_start = idx + 1
    if re.search(r'[A-Za-z]', lines[manhole_start]):
        manhole_lines = lines[manhole_start + 1: manhole_start + 1 + manholes_count]
    else:
        manhole_lines = lines[manhole_start: manhole_start + manholes_count]

    nodes = []
    for ln in manhole_lines:
        parts = _split_cols(ln)
        if len(parts) < 5:
            continue
        nid = int(parts[0])
        x = float(parts[1])
        y = float(parts[2])
        elev = float(parts[3])
        flow = float(parts[4])
        nodes.append((nid, flow, x, y, elev))

    nodes_df = pd.DataFrame(nodes, columns=["id", "flow", "x", "y", "elevation"]).set_index("id")

    # ---- SECTIONS BLOCK ----
    sec_line_idx = manhole_start + 1 + manholes_count
    while sec_line_idx < len(lines) and not lines[sec_line_idx].lower().startswith("sections"):
        sec_line_idx += 1
    if sec_line_idx >= len(lines):
        raise ValueError("Could not find 'Sections' block")

    sec_count = int(_split_cols(lines[sec_line_idx])[1])

    # detect section header like "v1 v2 slope intercept"
    section_start = sec_line_idx + 1
    if re.search(r'[A-Za-z]', lines[section_start]):
        section_lines = lines[section_start + 1: section_start + 1 + sec_count]
    else:
        section_lines = lines[section_start: section_start + sec_count]

    edges = []
    for ln in section_lines:
        parts = _split_cols(ln)
        if len(parts) < 2:
            continue
        u, v = int(parts[0]), int(parts[1])
        edges.append((u, v))

    edges_df = pd.DataFrame(edges, columns=["u", "v"])

    return nodes_df, edges_df