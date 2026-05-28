from framework import test_case

@test_case(
    phase="PHASE 10 — Messagerie (PRIVMSG / NOTICE)",
    name="PRIVMSG dans un canal",
    expected_behavior="Les autres membres du canal reçoivent le message, mais pas l'émetteur.",
    concept="broadcast(msg, client_exclu) pour éviter le doublon d'envoi.",
    guidance="Lorsqu'un message PRIVMSG est envoyé à un canal, diffusez-le à tous ses membres en excluant explicitement l'expéditeur de la diffusion.",
    doc_file="docs/10_messagerie.md",
    doc_sections=["## 5. Pourquoi ces objectifs ?", "## 6.2 — Envoi dans un channel"]
)
def test_privmsg_channel(create_client, password):
    a = create_client("ma")
    b = create_client("mb")
    
    a.connect()
    a.register(password)
    a.send("JOIN #msg")
    a.recv_lines(1.0)

    b.connect()
    b.register(password)
    b.send("JOIN #msg")
    b.recv_lines(1.0)

    a.send("PRIVMSG #msg :Bonjour")
    lb = b.recv_lines(1.5)
    la = a.recv_lines(0.5)
    
    bg = any("Bonjour" in l for l in lb)
    ad = any("Bonjour" in l and "PRIVMSG" in l for l in la)
    
    assert bg, "Le destinataire (Bob) n'a pas reçu le message envoyé sur le canal."
    assert not ad, "L'expéditeur (Alice) a reçu son propre message en écho."

@test_case(
    phase="PHASE 10 — Messagerie (PRIVMSG / NOTICE)",
    name="PRIVMSG direct (privé)",
    expected_behavior="Le message est directement délivré au destinataire spécifié.",
    concept="Recherche de client par nickname et écriture directe sur son socket.",
    guidance="Si le destinataire est un pseudo, recherchez-le dans votre base de clients connectés et écrivez le message directement sur son descripteur.",
    doc_file="docs/10_messagerie.md",
    doc_sections=["## 6.3 — Envoi direct à un utilisateur", "## 4. Objectif attendu dans ce projet"]
)
def test_privmsg_direct(create_client, password):
    a = create_client("dma")
    b = create_client("dmb")
    
    a.connect()
    a.register(password)
    b.connect()
    b.register(password)
    
    a.recv_lines(0.5)
    b.recv_lines(0.5)
    
    a.send("PRIVMSG dmb :Secret")
    lb = b.recv_lines(1.5)
    
    has_msg = any("Secret" in l for l in lb)
    assert has_msg, "Le message direct n'a pas été reçu par le destinataire (dmb)."

@test_case(
    phase="PHASE 10 — Messagerie (PRIVMSG / NOTICE)",
    name="PRIVMSG cible inexistante",
    expected_behavior="Retourne le code numérique 401 ERR_NOSUCHNICK.",
    concept="validation de l'existence de la cible (canal ou client).",
    guidance="Si la cible du PRIVMSG n'existe pas, répondez au client par l'erreur 401.",
    doc_file="docs/10_messagerie.md",
    doc_sections=["## 6.1 — `cmd_privmsg()` : vue d'ensemble", "## 4. Objectif attendu dans ce projet"]
)
def test_privmsg_nonexistent(create_client, password):
    c = create_client("e401")
    c.connect()
    c.register(password)
    c.send("PRIVMSG fantome :test")
    r = c.wait("401")
    assert r is not None, "Le serveur n'a pas renvoyé l'erreur 401 (ERR_NOSUCHNICK) pour une cible inexistante."

@test_case(
    phase="PHASE 10 — Messagerie (PRIVMSG / NOTICE)",
    name="NOTICE cible inexistante (silence)",
    expected_behavior="Le serveur ne produit aucune erreur en retour et reste silencieux.",
    concept="La commande NOTICE ne doit jamais générer d'erreurs automatiques.",
    guidance="La commande NOTICE fonctionne comme PRIVMSG mais les erreurs comme ERR_NOSUCHNICK (401) doivent être ignorées silencieusement pour éviter les boucles infinies de messages.",
    doc_file="docs/10_messagerie.md",
    doc_sections=["## 6.5 — `cmd_notice()` : version silencieuse", "## 5. Pourquoi NOTICE ne génère-t-il jamais d'erreur ?"]
)
def test_notice_silence(create_client, password):
    c = create_client("not")
    c.connect()
    c.register(password)
    c.send("NOTICE fantome :bonjour")
    ls = c.recv_lines(1.0)
    has_401 = any("401" in l for l in ls)
    assert not has_401, "Le serveur a généré une erreur 401 pour un NOTICE destiné à une cible inexistante, violant la RFC."
