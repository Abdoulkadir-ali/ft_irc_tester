from framework import test_case

@test_case(
    phase="PHASE 08 — Canaux (JOIN / PART / TOPIC / KICK)",
    name="Réponses de JOIN",
    expected_behavior="Le serveur renvoie l'écho de JOIN, le RPL_NAMREPLY (353) et le RPL_ENDOFNAMES (366).",
    concept="cmd_join() envoie le message JOIN ainsi que la liste des membres.",
    guidance="Quand un client rejoint un canal, vous devez lui envoyer un écho du JOIN, puis la liste des membres connectés sur ce canal (code 353) et la fin de liste (code 366).",
    doc_file="docs/08_canaux.md",
    doc_sections=["## 4. Objectif attendu dans ce projet", "## 6.3 — `cmd_join()` : rejoindre un channel"]
)
def test_join_channel_responses(create_client, password):
    c = create_client("j1")
    c.connect()
    c.register(password)
    c.send("JOIN #ph08")
    ls = c.recv_lines(1.5)
    
    j = any("JOIN" in l and "#ph08" in l for l in ls)
    n = any("353" in l for l in ls)
    e = any("366" in l for l in ls)
    
    assert j, "Pas d'écho JOIN reçu par le client."
    assert n, "Pas de RPL_NAMREPLY (353) reçu lors du JOIN."
    assert e, "Pas de RPL_ENDOFNAMES (366) reçu lors du JOIN."

@test_case(
    phase="PHASE 08 — Canaux (JOIN / PART / TOPIC / KICK)",
    name="Notification de JOIN (broadcast)",
    expected_behavior="Les membres du canal reçoivent une notification quand un nouveau client le rejoint.",
    concept="broadcast() de l'événement JOIN à tous les membres du canal.",
    guidance="Lorsqu'un utilisateur rejoint un canal existant, tous les utilisateurs déjà présents dans ce canal doivent recevoir un message indiquant son arrivée.",
    doc_file="docs/08_canaux.md",
    doc_sections=["## 6.1 — `Channel::broadcast()` : envoyer à tous les membres", "## 5. Pourquoi ces objectifs ?"]
)
def test_join_broadcast(create_client, password):
    a = create_client("vis_a")
    a.connect()
    a.register(password)
    a.send("JOIN #vis")
    a.recv_lines(1.0)

    b = create_client("vis_b")
    b.connect()
    b.register(password)
    b.send("JOIN #vis")
    b.recv_lines(1.0)

    ls = a.recv_lines(1.5)
    has_join = any("vis_b" in l and "JOIN" in l for l in ls)
    assert has_join, "Le premier client (vis_a) n'a pas reçu la notification de l'arrivée de vis_b."

@test_case(
    phase="PHASE 08 — Canaux (JOIN / PART / TOPIC / KICK)",
    name="Modification du TOPIC",
    expected_behavior="Le topic est modifié et la notification est diffusée.",
    concept="cmd_topic() permet à l'opérateur de modifier le topic et le notifie.",
    guidance="Lorsqu'un opérateur change le TOPIC d'un canal, le serveur doit modifier l'attribut du canal et envoyer la notification à tous les membres.",
    doc_file="docs/08_canaux.md",
    doc_sections=["## 6.5 — `cmd_topic()` : lire ou modifier le sujet", "## 4. Objectif attendu dans ce projet"]
)
def test_topic_change(create_client, password):
    c = create_client("top")
    c.connect()
    c.register(password)
    c.send("JOIN #topch")
    c.recv_lines(1.0)
    c.send("TOPIC #topch :Sujet test")
    r = c.wait("TOPIC")
    assert r is not None and "Sujet test" in r, "Le changement de TOPIC n'a pas été notifié en retour."

@test_case(
    phase="PHASE 08 — Canaux (JOIN / PART / TOPIC / KICK)",
    name="Commande KICK",
    expected_behavior="L'opérateur expulse un membre et la victime reçoit la notification de KICK.",
    concept="cmd_kick() valide les privilèges, retire le client du canal et diffuse l'expulsion.",
    guidance="Vérifiez que seul un opérateur du canal peut KICK. La cible doit être retirée de la liste des membres du canal et recevoir la notification de son exclusion.",
    doc_file="docs/08_canaux.md",
    doc_sections=["## 6.6 — `cmd_kick()` : expulser un membre", "## 4. Objectif attendu dans ce projet"]
)
def test_kick_member(create_client, password):
    op = create_client("kop")
    vic = create_client("kvic")
    
    op.connect()
    op.register(password)
    op.send("JOIN #kch")
    op.recv_lines(1.0)

    vic.connect()
    vic.register(password)
    vic.send("JOIN #kch")
    vic.recv_lines(1.0)

    op.send("KICK #kch kvic :Out")
    r = vic.wait("KICK", 2.0)
    assert r is not None and "kvic" in r, "Le client exclu (kvic) n'a pas reçu sa notification KICK."
