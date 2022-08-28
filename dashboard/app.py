from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv("data.csv")
# Lista de paises
paises = df["Country"].unique()

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="map-with-dropdown"),
        dcc.Dropdown(paises, paises, multi=True, id="paises-dropdown"),
    ]
)


@app.callback(
    Output("map-with-dropdown", "figure"),
    Input("paises-dropdown", "value"),
)
def update_map(paises_selecionados):
    filtered_df = df.loc[df["Country"].isin(paises_selecionados)]

    fig = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Country",
        size="Value",
        hover_data=["Value"],
        color_discrete_sequence=["fuchsia"],
        zoom=2,
        height=800,
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0")
