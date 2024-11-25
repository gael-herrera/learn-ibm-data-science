import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


def create_dash_app():
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Layout with enhanced visualization options
    app.layout = html.Div(
        [
            html.H1(
                "Automobile Sales Analytics Dashboard",
                style={"textAlign": "center", "padding": "20px"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select Visualization"),
                            dcc.Dropdown(
                                id="visualization-dropdown",
                                options=[
                                    {
                                        "label": "Yearly Sales Trend",
                                        "value": "yearly_sales",
                                    },
                                    {
                                        "label": "Recession Sales by Vehicle Type",
                                        "value": "recession_sales",
                                    },
                                    {
                                        "label": "Sales Comparison (Recession vs Non-Recession)",
                                        "value": "sales_comparison",
                                    },
                                    {
                                        "label": "GDP Comparison",
                                        "value": "gdp_comparison",
                                    },
                                    {
                                        "label": "Seasonality Impact",
                                        "value": "seasonality",
                                    },
                                    {"label": "Price vs Sales", "value": "price_sales"},
                                    {
                                        "label": "Advertisement Expenditure",
                                        "value": "ad_expenditure",
                                    },
                                    {
                                        "label": "Vehicle Type Advertisement",
                                        "value": "vehicle_ad",
                                    },
                                    {
                                        "label": "Unemployment Effect",
                                        "value": "unemployment",
                                    },
                                ],
                                value="yearly_sales",
                            ),
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            html.Label("Select Year (when applicable)"),
                            dcc.Dropdown(
                                id="year-dropdown",
                                options=[
                                    {"label": str(year), "value": year}
                                    for year in sorted(data["Year"].unique())
                                ],
                                value=data["Year"].min(),
                            ),
                        ],
                        width=6,
                    ),
                ],
                className="mb-4",
            ),
            html.Div(id="output-container", className="output-container"),
        ]
    )

    @app.callback(
        Output("output-container", "children"),
        [Input("visualization-dropdown", "value"), Input("year-dropdown", "value")],
    )
    def update_output(selected_viz, selected_year):
        if selected_viz == "yearly_sales":
            yearly_sales = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
            fig = px.line(
                yearly_sales,
                x="Year",
                y="Automobile_Sales",
                title="Automobile Sales Fluctuations by Year",
            )

        elif selected_viz == "recession_sales":
            recession_data = data[data["Recession"] == 1]
            fig = px.line(
                recession_data,
                x="Year",
                y="Automobile_Sales",
                color="Vehicle_Type",
                title="Sales Trends by Vehicle Type During Recession Periods",
            )

        elif selected_viz == "sales_comparison":
            fig = px.box(
                data,
                x="Vehicle_Type",
                y="Automobile_Sales",
                color="Recession",
                title="Vehicle Sales: Recession vs Non-Recession Periods",
            )

        elif selected_viz == "gdp_comparison":
            fig = px.line(
                data,
                x="Year",
                y="GDP",
                color="Recession",
                title="GDP Comparison: Recession vs Non-Recession Periods",
            )

        elif selected_viz == "seasonality":
            seasonality_data = (
                data.groupby("Month")["Automobile_Sales"].mean().reset_index()
            )
            sizes = data.groupby("Month")["Seasonality_Weight"].mean().values * 1000
            fig = px.scatter(
                seasonality_data,
                x="Month",
                y="Automobile_Sales",
                size=[s for s in sizes],
                title="Impact of Seasonality on Automobile Sales",
            )

        elif selected_viz == "price_sales":
            recession_data = data[data["Recession"] == 1]
            fig = px.scatter(
                recession_data,
                x="Price",
                y="Automobile_Sales",
                title="Price vs Sales During Recession",
            )

        elif selected_viz == "ad_expenditure":
            grouped_data = (
                data.groupby("Recession")["Advertising_Expenditure"].sum().reset_index()
            )
            fig = px.pie(
                grouped_data,
                values="Advertising_Expenditure",
                names="Recession",
                title="Advertising Expenditure Distribution",
            )

        elif selected_viz == "vehicle_ad":
            recession_data = data[data["Recession"] == 1]
            vehicle_ad_spending = (
                recession_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
                .sum()
                .reset_index()
            )
            fig = px.pie(
                vehicle_ad_spending,
                values="Advertising_Expenditure",
                names="Vehicle_Type",
                title="Advertisement Expenditure by Vehicle Type During Recession",
            )

        elif selected_viz == "unemployment":
            recession_data = data[data["Recession"] == 1]
            fig = px.line(
                recession_data,
                x="Year",
                y="Automobile_Sales",
                color="Vehicle_Type",
                title="Effect of Unemployment Rate on Vehicle Sales during Recession",
            )

        return dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(figure=fig),
                    ],
                    width=12,
                )
            ]
        )

    return app


if __name__ == "__main__":
    # Read the data
    data = pd.read_csv(
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
    )
    data["Date"] = pd.to_datetime(data["Date"])

    app = create_dash_app()
    app.run_server(debug=True)
