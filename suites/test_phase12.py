from framework import test_case

@test_case(
    phase="PHASE 12 — Bot IRC intégré (socketpair)",
    name="Présence du Bot (IRCBot)",
    expected_behavior="Le WHOIS sur 'IRCBot' renvoie les codes numériques 311, 319 ou 318.",
    concept="Bot::init() utilisant socketpair() pour créer un faux client connecté.",
    guidance="Au lancement, le serveur doit créer une instance de Bot connectée en interne via socketpair(), visible comme un utilisateur normal (IRCBot) et répondant au WHOIS.",
    doc_file="docs/12_bot.md",
    doc_sections=["## 4. Objectif attendu dans ce projet", "## 6.1 — `Bot::init()` : créer la paire de sockets et s'enregistrer"]
)
def test_bot_presence(create_client, password):
    c = create_client("bt")
    c.connect()
    c.register(password)
    c.send("WHOIS IRCBot")
    ls = c.recv_lines(1.5)
    
    has_bot_whois = any("IRCBot" in l and any(x in l for x in ["311", "319", "318"]) for l in ls)
    assert has_bot_whois, "Le WHOIS sur 'IRCBot' n'a pas renvoyé les réponses attendues (311, 318, 319)."

@test_case(
    phase="PHASE 12 — Bot IRC intégré (socketpair)",
    name="Bot Ping-Pong",
    expected_behavior="Le bot réagit au message '!ping' en envoyant 'PONG!'.",
    concept="Bot::processLine() écoute sur le socket et répond aux commandes du canal.",
    guidance="Assurez-vous que le bot écoute les messages du canal (ex: #general) et répond par 'PONG!' lorsqu'il détecte la commande '!ping'.",
    doc_file="docs/12_bot.md",
    doc_sections=["## 6.5 — `Bot::handlePrivmsg()` : répondre aux commandes", "## 7. Schéma de flux complet"]
)
def test_bot_ping_pong(create_client, password):
    c = create_client("ping_t")
    c.connect()
    c.register(password)
    c.send("JOIN #general")
    c.recv_lines(1.0)
    c.send("PRIVMSG #general :!ping")
    ls = c.recv_lines(2.0)
    
    has_pong = any("PONG" in l and "IRCBot" in l for l in ls)
    assert has_pong, "Le bot n'a pas répondu 'PONG!' dans le canal suite à la commande '!ping'."
