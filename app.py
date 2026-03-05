import dash
from dash import dcc, html, Input, Output, State, dash_table, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3, pickle, warnings

warnings.filterwarnings("ignore")

# ─── Color Palette ──────────────────────────────────────────────────────────
BG_COLOR = "#FBEFEF"      # Pale Pink
HEADER_COLOR = "#E0AED0"  # Soft Purple-Pink
PRIMARY_COLOR = "#756AB6" # Deep Lavender
SECONDARY_COLOR = "#AC87C5" # Medium Purple

G_PRIME = "#6367FF"
G_HIGH = "#8494FF"
G_EMERGING = "#C9BEFF"
G_WATCH = "#FFDBFD"
GRAPH_PALETTE = [G_PRIME, G_HIGH, G_EMERGING, G_WATCH]

# ─── Data & Models ──────────────────────────────────────────────────────────
def load_data():
    conn = sqlite3.connect("data/darkstore.db")
    df = pd.read_sql("SELECT * FROM zones_enriched", conn)
    trends = pd.read_sql("SELECT * FROM monthly_trends", conn)
    feat_imp = pd.read_sql("SELECT * FROM feature_importance", conn); conn.close()
    return df, trends, feat_imp

def load_models():
    with open("models/classifier.pkl", "rb") as f: clf = pickle.load(f)
    with open("models/regressor.pkl", "rb") as f: reg = pickle.load(f)
    with open("models/scaler.pkl", "rb") as f: scaler = pickle.load(f)
    with open("models/label_encoder.pkl","rb") as f: le = pickle.load(f)
    return clf, reg, scaler, le

try:
    df, trends, feat_imp = load_data()
    clf, reg, scaler, le = load_models()
except Exception as e:
    print(f"Error: {e}"); df = pd.DataFrame() 

ALL_CITIES = sorted(df["city"].unique()) if not df.empty else []
COLOR_MAP = {"Prime": G_PRIME, "High Potential": G_HIGH, "Emerging": G_EMERGING, "Wait and Watch": G_WATCH}

# ─── App Init ────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;600&display=swap"], 
                suppress_callback_exceptions=True, title="Dark Store IQ")
server = app.server

# ─── Master CSS ──────────────────────────────────────────────────────────────
app.index_string = f'''<!DOCTYPE html><html><head>{{%metas%}}<title>Dark Store IQ</title>{{%favicon%}}{{%css%}}
<style>
:root {{ --bg: {BG_COLOR}; --header: {HEADER_COLOR}; --primary: {PRIMARY_COLOR}; --secondary: {SECONDARY_COLOR}; }}
body {{ background: var(--bg); font-family: 'Inter', sans-serif; margin: 0; color: #4A4A4A; overflow-x: hidden; }}
.main-content {{ padding: 1rem 5%; min-height: 100vh; background: var(--bg); }}
.top-panel {{ background: var(--bg); padding: 2rem 0; text-align: center; position: sticky; top: 0; z-index: 1001; }}
.app-title {{ font-size: 2.5rem; font-weight: 800; color: var(--primary); font-family: 'Plus Jakarta Sans'; margin-bottom: 1.5rem; letter-spacing: -1px; }}
.nav-container {{ display: flex; justify-content: center; gap: 12px; flex-wrap: wrap; padding: 0 1rem; }}
.nav-btn {{ background: transparent; border: 2px solid var(--secondary); border-radius: 12px; padding: 0.6rem 1.2rem; color: var(--primary); font-weight: 700; text-decoration: none; transition: 0.3s ease; cursor: pointer; }}

.nav-btn:hover {{ background: var(--header); transform: scale(1.05); }}
.nav-btn.active {{ background: var(--primary); color: white !important; border-color: var(--primary); box-shadow: 0 4px 15px rgba(117, 106, 182, 0.2); }}
.glass-card {{ background: white; border-radius: 20px; border: 1px solid rgba(172, 135, 197, 0.2); box-shadow: 0 4px 20px rgba(0,0,0,0.02); padding: 1.5rem; transition: 0.3s; height: 100%; }}
.hero-banner {{ background: #FFE4EF; border-radius: 20px; padding: 2rem; margin-bottom: 2.5rem; color: var(--primary); border: 2px solid var(--header); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.kpi-value {{ font-size: 2.2rem; font-weight: 800; color: var(--primary); font-family: 'Plus Jakarta Sans'; }}
.kpi-label {{ font-size: 0.8rem; color: var(--secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }}
.filter-bar {{ background: var(--bg); padding: 1rem 0; z-index: 1000; }}
.filter-label {{ color: var(--primary); font-weight: 800; margin-bottom: 8px; font-size: 0.9rem; }}
.share-btn {{ position: absolute; top: 2rem; right: 5%; background: white; border: 2px solid var(--header); border-radius: 50%; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.3s; color: var(--primary); font-weight: bold; }}
.share-btn:hover {{ background: var(--header); transform: rotate(15deg); }}
.page-break {{ break-before: page; margin-top: 3rem; }}
@media print {{ .top-panel, .filter-bar, .btn-print, .nav-container, .share-btn, .page-nav {{ display: none !important; }} .main-content {{ padding: 0 !important; background: white !important; }} .glass-card {{ border: 2px solid {HEADER_COLOR} !important; -webkit-print-color-adjust: exact; }} .hero-banner {{ background: #FFE4EF !important; -webkit-print-color-adjust: exact; }} .page-break {{ display: block !important; break-before: page !important; }} }}
</style></head><body>{{%app_entry%}}<footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer></body></html>'''

# ─── Components ───────────────────────────────────────────────────────────────
def make_top_panel():
    nav = [("overview","Overview"), ("map","Site Map"), ("vault","Data Vault"), ("predictor","AI Predictor"), ("trends","Trends"), ("ml","ML Insights"), ("compare","Zone Compare"), ("report","Executive Report")]
    return html.Div(className="top-panel", children=[
        html.Div("Dark Store IQ", className="app-title"),
        html.Div(className="nav-container", children=[html.Div(l, id=f"nav-{k}", className="nav-btn") for k, l in nav]),
        html.Div("Link", id="btn-share", className="share-btn", title="Copy Share Link")
    ])

def make_filter_bar():
    return html.Div(className="filter-bar", children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([html.Div("Search Zones / Cities", className="filter-label"), dcc.Dropdown(id="f-search", options=[{"label": f"{r['zone']} ({r['city']})", "value": r["zone_id"]} for _, r in df.iterrows()], placeholder="Type to search...", className="mb-2")], md=3),
                dbc.Col([html.Div("Select Cities", className="filter-label"), dcc.Dropdown(id="f-cities", options=[{"label": c, "value": c} for c in ALL_CITIES], value=ALL_CITIES[:5], multi=True)], md=3),
                dbc.Col([html.Div("Min Score", className="filter-label"), dcc.Slider(id="f-score", min=0, max=100, step=5, value=20, marks={0:"0",50:"50",100:"100"})], md=3),
                dbc.Col([dbc.ButtonGroup([dbc.Button("Export Data", id="btn-export", className="fw-bold", style={"background":SECONDARY_COLOR, "border":"none"}), dbc.Button("Export PDF", id="btn-pdf-global", className="fw-bold", style={"background":PRIMARY_COLOR, "border":"none"})], className="w-100", style={"marginTop":"1.6rem"})], md=3),
            ], className="align-items-center"),
            dcc.Download(id="download-data")
        ])
    ])

app.layout = html.Div([
    dcc.Store(id="cur-page", data="overview"),
    dcc.Store(id="pinned-zones", storage_type="local", data=[]),
    dcc.Location(id="url", refresh=False),
    make_top_panel(),
    make_filter_bar(),
    html.Div(className="main-content", id="page-content"),
    dbc.Toast("Dashboard link copied!", id="toast-share", header="Success", icon="success", duration=3000, is_open=False, style={"position":"fixed", "top":20, "right":20, "zIndex":2000})
])

# ─── Callbacks ───────────────────────────────────────────────────────────────
@app.callback(Output("cur-page","data"), [Input(f"nav-{k}","n_clicks") for k in ["overview","map","vault","predictor","trends","ml","compare","report"]])
def switch_tab(*args):
    if not ctx.triggered: return "overview"
    return ctx.triggered[0]["prop_id"].split(".")[0].replace("nav-", "")

@app.callback([Output(f"nav-{k}","className") for k in ["overview","map","vault","predictor","trends","ml","compare","report"]], Input("cur-page","data"))
def nav_style(page):
    return ["nav-btn active" if k == page else "nav-btn" for k in ["overview","map","vault","predictor","trends","ml","compare","report"]]

@app.callback(Output("page-content","children"), [Input("cur-page","data"), Input("f-cities","value"), Input("f-score","value"), Input("f-search","value"), Input("pinned-zones","data")])
def render_page(page, cities, min_score, search_id, pinned):
    if df.empty: return html.Div("Data missing.")
    filt = df.copy()
    if search_id: filt = filt[filt["zone_id"] == search_id]
    elif cities: filt = filt[filt["city"].isin(cities)]
    filt = filt[filt["opportunity_score"] >= (min_score or 0)]
    
    if page == "map": return page_map(filt)
    if page == "vault": return page_vault(filt)
    if page == "predictor": return page_predictor()
    if page == "trends": return page_trends(cities or ALL_CITIES)
    if page == "ml": return page_ml(filt)
    if page == "compare": return page_compare(pinned)
    if page == "report": return page_report(filt)
    return page_overview(filt)

@app.callback(Output("pinned-zones","data"), Input({"type":"pin-btn", "id": dash.ALL}, "n_clicks"), State("pinned-zones","data"), prevent_initial_call=True)
def update_pins(n_clicks, pinned):
    if not ctx.triggered: return pinned
    zone_id = ctx.triggered_id["id"]
    if zone_id in pinned: pinned.remove(zone_id)
    else: pinned.append(zone_id)
    return pinned

app.clientside_callback("function(n) { if(n) { navigator.clipboard.writeText(window.location.href); return true; } return false; }", Output("toast-share", "is_open"), Input("btn-share", "n_clicks"))

# ─── Page Functions ─────────────────────────────────────────────────────────
def kpi_card(val, label):
    return html.Div(className="glass-card text-center animated-card", children=[html.Div(val, className="kpi-value"), html.Div(label, className="kpi-label")])

def page_report(filt):
    if filt.empty: return html.Div("No data.")
    top_5 = filt[filt["recommend_darkstore"] == 1].sort_values("opportunity_score", ascending=False).head(5)
    avg_score = top_5["opportunity_score"].mean() if not top_5.empty else 0
    avg_rent = filt["real_estate_cost_sqft"].mean(); total_setup = 1500000 * len(top_5); total_rent = avg_rent * 2500 * 12 * len(top_5); total_inv = total_setup + total_rent
    roi = ((top_5["monthly_revenue_potential_inr"].sum()*12*0.15)-total_rent)/total_inv*100 if total_inv>0 else 0
    
    bullet = go.Figure(go.Indicator(mode="number+gauge+delta", value=avg_score, delta={'reference':70}, gauge={'shape':"bullet", 'axis':{'range':[None,100]}, 'threshold':{'line':{'color':"red",'width':2}, 'value':70}, 'steps':[{'range':[0,50],'color':G_WATCH},{'range':[50,75],'color':G_EMERGING},{'range':[75,100],'color':G_HIGH}], 'bar':{'color':G_PRIME}}))
    bullet.update_layout(height=150, margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor="rgba(0,0,0,0)")

    return html.Div([
        html.Div([dbc.Row([dbc.Col([html.H2("Expansion Executive Report"), html.P(f"Strategic Summary for {len(top_5)} Locations")], md=8), dbc.Col(dbc.Button("Print Report", id="print-btn", className="w-100", style={"background":PRIMARY_COLOR,"border":"none"}), md=4)])], className="hero-banner"),
        dbc.Row([dbc.Col(kpi_card(f"₹{total_inv/1e7:.2f}Cr", "Total Investment"), md=4), dbc.Col(kpi_card(f"{roi:.1f}%", "Projected ROI"), md=4), dbc.Col(kpi_card("Medium", "Risk Profile"), md=4)], className="g-4 mb-4"),
        html.Div(className="glass-card mb-4", children=[html.H5("Performance vs Growth Threshold"), dcc.Graph(figure=bullet, config={"displayModeBar":False})]),
        html.Div(className="page-break", children=[
            html.Div(className="glass-card", children=[
                html.H5("Top 5 Strategic Priority Sites", className="mb-4"),
                dash_table.DataTable(data=top_5[["city","zone","opportunity_score","monthly_revenue_potential_inr"]].to_dict("records"), columns=[{"name":i.replace("_"," ").title(),"id":i} for i in ["city","zone","opportunity_score","monthly_revenue_potential_inr"]], style_cell={"padding":"15px","textAlign":"left"}, style_header={"backgroundColor":HEADER_COLOR,"fontWeight":"800","color":PRIMARY_COLOR})
            ])
        ])
    ])

def page_vault(filt):
    return html.Div([
        html.Div([html.H2("Data Intelligence Vault"), html.P("Full Granular Access to Filtered Market Data")], className="hero-banner"),
        html.Div(className="glass-card", children=[
            dbc.Button("Download Filtered CSV", id="btn-vault-csv", className="mb-4 fw-bold", style={"background":G_PRIME, "border":"none"}),
            dash_table.DataTable(data=filt.to_dict("records"), columns=[{"name": i.replace("_"," ").title(), "id": i} for i in filt.columns[:10]], page_size=15, sort_action="native", filter_action="native", style_cell={"padding":"12px","fontSize":"0.85rem"}, style_header={"backgroundColor":HEADER_COLOR,"fontWeight":"800","color":PRIMARY_COLOR})
        ])
    ])

def page_overview(filt):
    avg_score = filt['opportunity_score'].mean(); total_rev = filt['monthly_revenue_potential_inr'].mean() / 1e5
    kpi_row = dbc.Row([dbc.Col(kpi_card(f"{len(filt)}", "Zones"), md=2), dbc.Col(kpi_card(f"{int(filt['recommend_darkstore'].sum())}", "Recs"), md=2), dbc.Col(kpi_card(f"₹{total_rev:.1f}L", "Avg Rev"), md=3), dbc.Col(kpi_card(f"{avg_score:.1f}", "Avg Score"), md=2), dbc.Col(kpi_card(f"{int(filt['daily_orders'].sum()):,}", "Orders"), md=3)], className="g-4 mb-4")
    bar = px.bar(filt.sort_values("opportunity_score", ascending=False).head(15), x="opportunity_score", y="zone", orientation="h", color="zone_tier", color_discrete_map=COLOR_MAP, title="Top Zones").update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color=PRIMARY_COLOR)
    t_counts = filt["zone_tier"].value_counts().reset_index(); t_counts.columns = ["tier", "count"]
    pie = go.Figure(data=[go.Pie(labels=t_counts["tier"], values=t_counts["count"], hole=0.7, marker=dict(colors=[COLOR_MAP[t] for t in t_counts["tier"]]), textinfo='percent', showlegend=False)])
    pie.add_annotation(text=f"<b>{len(filt)}</b>", x=0.5, y=0.5, showarrow=False, font=dict(size=24, color=PRIMARY_COLOR))
    return html.Div([html.Div([html.H2("Expansion Executive Overview"), html.P("Strategic Intelligence Dashboard")], className="hero-banner"), kpi_row, dbc.Row([dbc.Col(html.Div(dcc.Graph(figure=bar), className="glass-card"), md=8), dbc.Col(html.Div(dcc.Graph(figure=pie.update_layout(title="Tier Split")), className="glass-card"), md=4)], className="g-4")])

def page_map(filt):
    fig = px.scatter_mapbox(filt, lat="latitude", lon="longitude", color="zone_tier", 
                            size="opportunity_score", hover_name="zone", 
                            color_discrete_map=COLOR_MAP, mapbox_style="open-street-map", 
                            zoom=3.8, size_max=25, opacity=0.8,
                            center={"lat": 22.5, "lon": 78.9})
    fig.update_layout(height=700, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="white")
    return html.Div([html.Div([html.H2("Geospatial Site Map"), html.P("Location Analysis & Market Coverage")], className="hero-banner"), html.Div(dcc.Graph(figure=fig), className="glass-card p-0")])

def page_compare(pinned):
    opts = [{"label": f"{r['city']} - {r['zone']}", "value": r["zone_id"]} for _, r in df.iterrows()]
    pinned_info = df[df["zone_id"].isin(pinned)] if pinned else pd.DataFrame()
    pinned_cards = [dbc.Col(dbc.Card([dbc.CardBody([html.H6(r['zone']), html.P(r['city'], className="small"), dbc.Button("Unpin", id={"type":"pin-btn","id":r["zone_id"]}, size="sm", color="link", style={"color":PRIMARY_COLOR})])], className="glass-card")) for _, r in pinned_info.iterrows()]
    return html.Div([
        html.Div([html.H2("Zone Comparator"), html.P("Dual-Entity Benchmarking")], className="hero-banner"),
        html.Div(className="glass-card mb-4", children=[html.H6("Pinned Favorites", className="mb-3 fw-bold"), dbc.Row(pinned_cards if not pinned_info.empty else [html.P("No zones pinned.", className="p-3")], className="g-2 mb-4"), dbc.Row([dbc.Col(dcc.Dropdown(id="z-a", options=opts, value=opts[0]["value"]), md=5), dbc.Col(html.H4("VS", className="text-center mt-2"), md=2), dbc.Col(dcc.Dropdown(id="z-b", options=opts, value=opts[1]["value"]), md=5)])]),
        html.Div(id="out-comp")
    ])

@app.callback(Output("out-comp","children"), [Input("z-a","value"), Input("z-b","value")], State("pinned-zones","data"))
def compare(za, zb, pinned):
    ra, rb = df[df["zone_id"]==za].iloc[0], df[df["zone_id"]==zb].iloc[0]
    get_vals = lambda r: [r["opportunity_score"], (r["daily_orders"]/3500)*100, (r["avg_order_value_inr"]/1000)*100, r["internet_penetration"]*100, r["road_connectivity_score"]*100, (r["avg_delivery_rating"]/5)*100]
    radar = go.Figure(); radar.add_trace(go.Scatterpolar(r=get_vals(ra), theta=["Score","Orders","AOV","Net","Road","Rate"], fill='toself', name=ra['zone'], line_color="#C9BEFF")); radar.add_trace(go.Scatterpolar(r=get_vals(rb), theta=["Score","Orders","AOV","Net","Road","Rate"], fill='toself', name=rb['zone'], line_color="#FFDBFD"))
    comp_row = lambda l, c, p: html.Div([html.Div(l, className="kpi-label text-center mb-1"), dbc.Row([dbc.Col(html.Div(f"{p}{ra[c]:.1f}", style={"color":G_PRIME if ra[c]>rb[c] else G_HIGH,"fontSize":"1.2rem","fontWeight":"800"}), className="text-center"), dbc.Col(html.Div(f"{p}{rb[c]:.1f}", style={"color":G_PRIME if rb[c]>ra[c] else G_HIGH,"fontSize":"1.2rem","fontWeight":"800"}), className="text-center")])], className="mb-4")
    return html.Div([dbc.Row([dbc.Col(html.Div([html.H4(ra['zone']), html.P(ra['city']), dbc.Button("Pin Zone", id={"type":"pin-btn","id":za}, size="sm", className="mb-3", style={"background":PRIMARY_COLOR,"border":"none"}), html.Hr(), *[comp_row(l, c, p) for l, c, p in [("Score","opportunity_score",""),("Orders","daily_orders",""),("AOV","avg_order_value_inr","₹"),("Net %","internet_penetration","")]]], className="glass-card"), md=6), dbc.Col(html.Div([html.H4(rb['zone']), html.P(rb['city']), dbc.Button("Pin Zone", id={"type":"pin-btn","id":zb}, size="sm", className="mb-3", style={"background":SECONDARY_COLOR,"border":"none"}), html.Hr(), *[comp_row(l, c, p) for l, c, p in [("Score","opportunity_score",""),("Orders","daily_orders",""),("AOV","avg_order_value_inr","₹"),("Net %","internet_penetration","")]]], className="glass-card"), md=6)], className="g-4 mb-4"), html.Div(className="glass-card", children=[dcc.Graph(figure=radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400))])])

def page_predictor():
    def f_in(l, i, mn, mx, s, v): return html.Div([html.Label(l, style={"fontSize":"0.85rem","fontWeight":"700"}), dbc.Input(id=i, type="number", min=mn, max=mx, step=s, value=v)], className="mb-3")
    return html.Div([html.Div([html.H2("AI Site Predictor"), html.P("Simulate Market Potential")], className="hero-banner"), html.Div(className="glass-card", children=[dbc.Row([dbc.Col([f_in("Pop Density", "in-pop", 1000, 100000, 1000, 25000), f_in("AOV", "in-order", 100, 2000, 50, 450)], md=4), dbc.Col([f_in("Orders", "in-daily", 50, 5000, 50, 800), f_in("Rent", "in-rent", 20, 500, 10, 80)], md=4), dbc.Col([html.Label("Income"), dcc.Dropdown(id="in-inc", options=[{"label":x,"value":x} for x in ["Low","Middle","Upper-Middle","High"]], value="Middle"), dbc.Button("Run AI Simulation", id="btn-run", className="w-100 mt-4", style={"background": PRIMARY_COLOR, "border": "none"})], md=4)])]), dcc.Loading(html.Div(id="out-pred", className="mt-4"), type="circle", color=PRIMARY_COLOR)])

@app.callback(Output("out-pred","children"), Input("btn-run","n_clicks"), [State(f"in-{k}", "value") for k in ["pop","order","daily","rent","inc"]])
def run_ai(n, pop, order, daily, rent, income):
    if not n: return ""
    try:
        ie = le.transform([income or "Middle"])[0]; X = pd.DataFrame([[pop, order, daily, 2, 25, 0.75, rent, 0.7, 0.45, 0.5, 1.6, 4.1, ie]], columns=scaler.feature_names_in_)
        Xs = scaler.transform(X); pred_c, pred_p, pred_s = clf.predict(Xs)[0], clf.predict_proba(Xs)[0][1], np.clip(reg.predict(Xs)[0], 0, 100)
        radial_gauge = go.Figure(go.Indicator(mode="gauge+number", value=round(pred_s, 1), number={'font': {'size': 54, 'color': '#111'}}, title={'text': "Market Viability Score", 'font': {'size': 24, 'color': PRIMARY_COLOR, 'weight': 'bold'}}, gauge={'axis': {'range': [0, 100], 'visible': False}, 'bar': {'color': G_PRIME, 'thickness': 0.8}, 'bgcolor': "rgba(99, 103, 255, 0.1)", 'steps': [{'range': [0, 50], 'color': "rgba(99, 103, 255, 0.05)"}, {'range': [50, 100], 'color': "rgba(99, 103, 255, 0.1)"}]}))
        radial_gauge.update_layout(height=400, margin=dict(l=50, r=50, t=80, b=50), paper_bgcolor="rgba(0,0,0,0)")
        status, color = ("RECOMMENDED", G_PRIME) if pred_c == 1 else ("NOT RECOMMENDED", G_HIGH)
        return dbc.Row([dbc.Col(html.Div([html.H3(status, style={"color":color,"fontWeight":"800"}), html.Hr(), html.H5(f"Confidence Level: {pred_p*100:.1f}%"), html.H5(f"Est. Monthly Revenue: ₹{(daily*order*30*0.12)/1e5:.1f}L")], className="glass-card text-center d-flex flex-column justify-content-center"), md=5), dbc.Col(html.Div(dcc.Graph(figure=radial_gauge, config={"displayModeBar":False}), className="glass-card"), md=7)], className="g-4")
    except Exception as e: return html.Div(f"Error: {e}", className="text-danger")

def page_trends(cities):
    data = trends[trends["city"].isin(cities)].sort_values("month_num")
    fig = px.line(data, x="month", y="total_orders", color="city", markers=True, color_discrete_sequence=["#00F7FF","#FF0087","#B0FFFA","#FF7DB0"]).update_layout(paper_bgcolor="white", plot_bgcolor="white")
    return html.Div([html.Div([html.H2("Market Trends")], className="hero-banner"), html.Div(dcc.Graph(figure=fig), className="glass-card")])

def page_ml(filt):
    if feat_imp.empty: return html.Div("ML metadata failed to load.")
    f_bar = px.bar(feat_imp.sort_values("importance", ascending=True), x="importance", y="feature", orientation="h", title="AI Signal Importance", color_discrete_sequence=[G_PRIME]).update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color=PRIMARY_COLOR, height=500)
    pca_fig = px.scatter(filt, x="pca_x", y="pca_y", color="zone_tier", color_discrete_map=COLOR_MAP, hover_name="zone", title="Market Segmentation (PCA)").update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color=PRIMARY_COLOR, height=500)
    return html.Div([html.Div([html.H2("ML Model Insights"), html.P("Decision Logic & Dimensional Clustering")], className="hero-banner"), dbc.Row([dbc.Col(html.Div(dcc.Graph(figure=f_bar, config={"displayModeBar":False}), className="glass-card"), md=6), dbc.Col(html.Div(dcc.Graph(figure=pca_fig, config={"displayModeBar":False}), className="glass-card"), md=6)], className="g-4")])

@app.callback(Output("download-data", "data"), [Input("btn-export", "n_clicks"), Input("btn-vault-csv", "n_clicks")], [State("f-cities", "value"), State("f-score", "value")], prevent_initial_call=True)
def export_csv(n1, n2, cities, min_score):
    filt = df[df["city"].isin(cities or ALL_CITIES) & (df["opportunity_score"] >= (min_score or 0))]
    return dcc.send_data_frame(filt.to_csv, "darkstore_iq_export.csv", index=False)

app.clientside_callback("function(n) { if(n > 0) window.print(); return 0; }", Output("btn-pdf-global", "n_clicks"), Input("btn-pdf-global", "n_clicks"))
app.clientside_callback("function(n) { if(n > 0) window.print(); return 0; }", Output("print-btn", "n_clicks"), Input("print-btn", "n_clicks"))

if __name__ == "__main__": app.run(debug=False, port=8050)
