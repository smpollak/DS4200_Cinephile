"""
Visualizations 3: Interactive Sankey diagram
"""

import pandas as pd
import plotly.graph_objects as go


movie_df = pd.read_csv("ds4200_data.csv")

sankey_df = movie_df.copy()
sankey_df = sankey_df.rename(
    columns={
        "Are you currently a student?": "Student",
        "What is your biggest barrier to going to the movie theater?": "barrier",
        "How would you best describe yourself?": "Gender",
    }
)

# Use the updated column names in left-to-right flow order.
flow_columns = ["Student", "barrier", "Gender"]

# Keep only rows that have all required fields.
sankey_data = sankey_df[flow_columns].dropna().copy()
sankey_data = sankey_data.astype(str)


def build_links(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Build aggregated source-target counts for each adjacent column pair."""
    all_links = []
    for i in range(len(columns) - 1):
        source_col = columns[i]
        target_col = columns[i + 1]
        links = (
            df.groupby([source_col, target_col])
            .size()
            .reset_index(name="value")
            .rename(columns={source_col: "source", target_col: "target"})
        )
        all_links.append(links)
    return pd.concat(all_links, ignore_index=True)


links_df = build_links(sankey_data, flow_columns)
all_nodes = pd.Index(pd.concat([links_df["source"], links_df["target"]]).unique())
node_map = {label: i for i, label in enumerate(all_nodes)}

# Stage hues: light node fills (dark labels) + stronger tints for link ribbons.
STAGE_NODE_FILL = ["#cfe2f3", "#d9ead3", "#ead1dc"]  # Student, barrier, Gender
STAGE_LINK_TINT = ["#3d85c6", "#6aa84f", "#a64d79"]


def stage_for_label(label: str) -> int:
    """Assign Sankey column (0–2) by first survey column that contains this category."""
    for i, col in enumerate(flow_columns):
        if label in sankey_data[col].unique():
            return i
    return 0


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


node_stages = [stage_for_label(str(lbl)) for lbl in all_nodes]
node_colors = [STAGE_NODE_FILL[s] for s in node_stages]

# Color each flow by its source stage (slightly transparent so overlaps read cleanly).
link_colors = [
    hex_to_rgba(STAGE_LINK_TINT[stage_for_label(str(src))], 0.42)
    for src in links_df["source"]
]

fig = go.Figure(
    data=[
        go.Sankey(
            arrangement="snap",
            # Node labels use trace-level textfont (node.font is not valid in Plotly Sankey).
            textfont=dict(size=12, color="#1a1a1a", family="Arial, sans-serif"),
            node=dict(
                pad=15,
                thickness=18,
                line=dict(color="rgba(0,0,0,0.35)", width=1),
                label=all_nodes.tolist(),
                color=node_colors,
            ),
            link=dict(
                source=links_df["source"].map(node_map).tolist(),
                target=links_df["target"].map(node_map).tolist(),
                value=links_df["value"].tolist(),
                color=link_colors,
            ),
        )
    ]
)

fig.update_layout(
    title_text="Sankey Diagram: Student Status -> Barrier -> Gender",
    font=dict(size=13, color="#1a1a1a"),
    paper_bgcolor="#fafafa",
    plot_bgcolor="#fafafa",
)

fig.write_html("vis4_sankey.html", full_html=False)

fig.show()