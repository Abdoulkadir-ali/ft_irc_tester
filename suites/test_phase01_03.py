from framework import test_case

@test_case(
    phase="PHASE 01 — Réseau et Sockets",
    name="Connexion TCP",
    expected_behavior="Connexion TCP établie avec le serveur.",
    concept="socket() + bind() + listen() <-> accept() côté serveur",
    guidance="Vérifiez que le serveur écoute bien sur le port spécifié en argument et accepte les connexions TCP.",
    doc_file="docs/01_reseau_et_sockets.md",
    doc_sections=["## 3. Objectif attendu dans ce projet", "## 4. Pourquoi ces objectifs ?"]
)
def test_tcp_connection(create_client, password):
    c = create_client("p01")
    c.connect()
    c.close()

@test_case(
    phase="PHASE 03 — Multi-clients (Boucle événementielle)",
    name="Connexions simultanées",
    expected_behavior="3 clients connectés en même temps au serveur.",
    concept="Boucle événementielle non bloquante utilisant poll()",
    guidance="Assurez-vous que le serveur utilise poll() ou select() pour gérer plusieurs sockets sans bloquer sur l'un d'eux.",
    doc_file="docs/03_boucle_evenementielle.md",
    doc_sections=["## 3. Objectif attendu dans ce projet", "## 4. Pourquoi ces objectifs ?"]
)
def test_simultaneous_connections(create_client, password):
    cs = [create_client(f"m{i}") for i in range(3)]
    for x in cs:
        x.connect()
    # Close them all
    for x in cs:
        x.close()
