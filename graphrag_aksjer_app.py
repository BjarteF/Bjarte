import streamlit as st
import yfinance as yf
import networkx as nx
import matplotlib.pyplot as plt

# Selskaper og tilhørende sektorer og ESG-score
companies = {
    "Equinor": {"ticker": "EQNR.OL", "sector": "Energy Sector", "esg_score": 72},
    "DNB": {"ticker": "DNB.OL", "sector": "Finance Sector", "esg_score": 65},
    "Mowi": {"ticker": "MOWI.OL", "sector": "Seafood Sector", "esg_score": 58}
}

def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    price = info.get("regularMarketPrice", "Ukjent")
    currency = info.get("currency", "NOK")
    return price, currency

def build_graph(companies):
    G = nx.DiGraph()
    for name, data in companies.items():
        price, currency = fetch_stock_data(data["ticker"])
        G.add_node(name, type="Company", ticker=data["ticker"], price=price, currency=currency, esg=data["esg_score"])
        G.add_node(data["sector"], type="Sector")
        G.add_edge(name, data["sector"], relation="belongs_to")
        G.add_edge(name, "ESG", relation="evaluated_by")
    G.add_node("ESG", type="Metric")
    return G

def draw_graph(G):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))
    node_colors = ['skyblue' if G.nodes[n]['type'] == 'Company' else 'lightgreen' if G.nodes[n]['type'] == 'Sector' else 'orange' for n in G.nodes]
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=1500, font_size=10, arrows=True)
    edge_labels = nx.get_edge_attributes(G, 'relation')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    st.pyplot(plt)

def query_graph(G, question):
    for company in companies:
        if company.lower() in question.lower():
            relations = list(G.edges(company, data=True))
            response = f"🔍 Faktorer som påvirker {company}:\n"
            for u, v, d in relations:
                response += f"- {u} {d['relation']} {v}\n"
            return response
    return "Beklager, jeg fant ingen informasjon for det spørsmålet."

# Streamlit-grensesnitt
st.title("📈 Norske Aksjer – GraphRAG Webapp")

selected_company = st.sidebar.selectbox("Velg et selskap", list(companies.keys()))

graph = build_graph(companies)
node = graph.nodes[selected_company]
sector = next(graph.successors(selected_company))

st.subheader(f"🔹 {selected_company}")
st.write(f"**Ticker:** {node['ticker']}")
st.write(f"**Pris:** {node['price']} {node['currency']}")
st.write(f"**Sektor:** {sector}")
st.write(f"**ESG-score:** {node['esg']}")

st.subheader("📊 Kunnskapsgraf")
draw_graph(graph)

st.subheader("💬 Still et spørsmål")
user_question = st.text_input("Hva vil du vite?")
if user_question:
    answer = query_graph(graph, user_question)
    st.markdown(answer)

st.subheader("📰 Sanntidsnyheter")

news = {
    "Equinor": [
        "Morgan Stanley nedgraderer Equinor til 'Hold' og kutter kursmål til 250 kr.",
        "JPMorgan anbefaler short-posisjon i Equinor grunnet svakheter i rapporteringen.",
        "Equinor-aksjen er ned 1,30 % i dag og handles til 258,20 kr."
    ],
    "DNB": [
        "DNB rapporterer rekordutbytte og sterk kvartalsrapport.",
        "DNB vurderer ekspansjon i Norden etter økt inntjening.",
        "DNB-aksjen stiger 2,1 % etter positiv analyse fra Pareto."
    ],
    "Mowi": [
        "Mowi påvirkes av laksepriser og nye eksportregler fra EU.",
        "Mowi investerer i ny teknologi for bærekraftig oppdrett.",
        "Mowi-aksjen faller 0,8 % etter svakere lakseprisprognoser."
    ]
}

for company, headlines in news.items():
    st.markdown(f"**{company}**")
    for headline in headlines:
        st.markdown(f"- {headline}")

