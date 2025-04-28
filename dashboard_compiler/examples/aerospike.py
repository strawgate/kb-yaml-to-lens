from dashboard_compiler.compile import compile_dashboard
from dashboard_compiler.models.config import Dashboard
from dashboard_compiler.models.config.controls import OptionsListControl
from dashboard_compiler.models.config.panels import LensPanel, LinksPanel, MarkdownPanel
from dashboard_compiler.models.config.panels.lens_charts.components.dimension import Dimension
from dashboard_compiler.models.config.panels.lens_charts.components.metric import Metric
from dashboard_compiler.models.config.panels.lens_charts.pie import LensPieChart
from dashboard_compiler.models.config.panels.lens_charts.xy import LensXYChart

# Example configuration for an Aerospike Metrics dashboard

dashboard = Dashboard(
    title="[Metrics Aerospike] Overview Yaml",
    description="A dashboard for Aerospike Metrics"
)

dashboard.add_control(
    OptionsListControl(
        label="Aerospike Namespace",
        data_view="metrics-*",
        field="aerospike.namespace"
    )
)

dashboard.add_panel(
    MarkdownPanel(
        title="On-dashboard description of Aerospike Metrics",
        hide_title=True,
        content=(
            "This dashboard provides an overview of Aerospike metrics, including node and namespace metrics.\n"
            "It includes links to the Aerospike documentation and community resources. See the integration page for setup instructions."
        ),
        grid={"x": 0, "y": 0, "w": 48, "h": 3}
    )
)

dashboard.add_panel(
    LinksPanel(
        title="Links",
        grid={"x": 0, "y": 3, "w": 48, "h": 3},
        description="Links to Aerospike documentation and other resources",
        layout="horizontal",
        links=[
            {"label": "Overview", "dashboard": "0aa67124-5f70-a811-7ec5-063c196c5e6e"},
            {"label": "Node Metrics", "dashboard": "ec958c2b-aefe-43ad-8864-60d0fe767280"},
            {"label": "Namespace Metrics", "dashboard": "70cf3a9f-94b5-4663-989b-b290aa94f43a"},
            {"label": "Vendor Documentation", "url": "https://www.aerospike.com/docs/"},
            {"label": "Community Forum", "url": "https://discuss.aerospike.com/"}
        ]
    )
)

dashboard.add_panel(
    LensPanel(
        title="Nodes by Namespace",
        description="A chart showing the number of nodes by namespace",
        index_pattern="metrics-*",
        grid={"x": 0, "y": 6, "w": 16, "h": 16},
        chart=LensPieChart(
            dimensions=[Dimension(field="aerospike.namespace", type="terms", size=5)],
            metrics=[Metric(type="count", label="Count of records", field="___records___")]
        )
    )
)

dashboard.add_panel(
    LensPanel(
        title="Free Memory by Node",
        description="A chart showing the minimum free memory by node",
        index_pattern="metrics-*",
        grid={"x": 16, "y": 6, "w": 32, "h": 16},
        chart=LensXYChart(
            dimensions=[Dimension(field="@timestamp", type="date_histogram", interval="auto")],
            metrics=[Metric(type="min", field="aerospike.node.memory.free")]
        )
    )
)

dashboard.add_panel(
    LensPanel(
        title="Open Connections by Node",
        description="A chart showing the number of open connections by node",
        index_pattern="metrics-*",
        grid={"x": 16, "y": 22, "w": 32, "h": 16},
        chart=LensXYChart(
            dimensions=[Dimension(field="@timestamp", type="date_histogram", interval="auto")],
            metrics=[Metric(type="max", field="aerospike.node.connection.open")]
        )
    )
)

print(compile_dashboard(dashboard))