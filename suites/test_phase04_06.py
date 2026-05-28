from framework import test_case

@test_case(
    phase="PHASE 04 — Gestion des clients (machine à états)",
    name="JOIN avant registration",
    expected_behavior="Retourne le code numérique 451 (ERR_NOTREGISTERED) si une commande est envoyée avant registration.",
    concept="Machine à états client : STATE_NEW bloque les commandes normales.",
    guidance="Assurez-vous que les clients non enregistrés ne peuvent pas envoyer de commandes comme JOIN. Le serveur doit répondre par un message d'erreur 451.",
    doc_file="docs/04_gestion_clients.md",
    doc_sections=["## 3. Les quatre états d'un client", "## 4. Objectif attendu dans ce projet"]
)
def test_join_before_registration(create_client, password):
    c = create_client("p04")
    c.connect()
    c.send("JOIN #test")
    r = c.wait("451")
    assert r is not None, "Le serveur n'a pas renvoyé le code d'erreur 451 (ERR_NOTREGISTERED) lors d'un JOIN avant registration."

@test_case(
    phase="PHASE 05+06 — Parsing et Dispatch",
    name="Commandes en minuscules",
    expected_behavior="Les commandes transmises en minuscules (ex: pass/nick/user) sont acceptées et permettent la registration.",
    concept="Parser::tokenize() normalise la commande en majuscules (Utils::toUpper).",
    guidance="Lors du parsing de la commande reçue, convertissez le nom de la commande en majuscules (insensibilité à la casse).",
    doc_file="docs/05_parsing_messages.md",
    doc_sections=["## 4. Objectif attendu dans ce projet", "## 5. Pourquoi ces objectifs ?"]
)
def test_lowercase_commands(create_client, password):
    c = create_client("p05")
    c.connect()
    c.send(f"pass {password}")
    c.send("nick p05")
    c.send("user p05 0 * :Test")
    r = c.wait(" 001 ")
    assert r is not None, "La registration a échoué car les commandes envoyées en minuscules n'ont pas été acceptées."

@test_case(
    phase="PHASE 05+06 — Parsing et Dispatch",
    name="Commande inconnue",
    expected_behavior="Retourne le code numérique 421 (ERR_UNKNOWNCOMMAND) pour une commande inconnue.",
    concept="Le dispatcher cherche la commande dans sa map. Si absente, renvoie 421.",
    guidance="Si le verbe de commande reçu n'est pas géré par le serveur (ex: 'FOOBAR'), renvoyez l'erreur 421 avec le nom de la commande.",
    doc_file="docs/06_dispatch_commandes.md",
    doc_sections=["## 3. Objectif attendu dans ce projet", "## 4. Pourquoi ces objectifs ?"]
)
def test_unknown_command(create_client, password):
    c = create_client("p06")
    c.connect()
    r_welcome = c.register(password)
    assert r_welcome is not None, "Impossible de s'enregistrer pour lancer le test de commande inconnue."
    c.send("FOOBAR x y")
    r = c.wait("421")
    assert r is not None, "Le serveur n'a pas renvoyé le code d'erreur 421 (ERR_UNKNOWNCOMMAND) suite à la commande inconnue FOOBAR."
