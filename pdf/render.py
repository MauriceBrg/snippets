import base64
import os
from pandas.core import base

import plotly.express as px

from pdf_reports import pug_to_html, write_report, preload_stylesheet

rows = [
    ["time", "event", "subevent","text", "room"],
    ["time", "event", "subevent","text", "room"],
    ["time", "event", "subevent","text", "room"],
    ["time", "event", "subevent","text", "room"],
]

def main():

    params = {
        "table_rows": rows
    }
    current_dir = os.path.dirname(os.path.abspath(__file__))
    params["workdir"] = f"file:///{current_dir}"

    df = px.data.tips()
    fig = px.pie(df, values='tip', names='day')
    # fig.show()

    fig_as_bytes = bytes(fig.to_image(format="png"))
    fig_as_b64 = base64.b64encode(fig_as_bytes)

    params["fig_as_b64"] = fig_as_b64.decode("utf-8")

    # css = preload_stylesheet('style.css')
    html = pug_to_html("template.pug", title=" Report", **params)
    # , extra_stylesheets=[css])
    write_report(html, "example.pdf")
    with open("report.html", "w") as out:
        out.write(html)


if __name__ == "__main__":
    main()