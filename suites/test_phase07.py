from framework import test_case

@test_case(
    phase="PHASE 07 — Registration (PASS / NICK / USER / CAP)",
    name="Registration réussie",
    expected_behavior="Le serveur envoie le message de bienvenue 001 RPL_WELCOME.",
    concept="tryRegister() valide que PASS_OK, NICK et USER sont tous complétés.",
    guidance="Assurez-vous que l'état du client transite vers connecté et envoie 001 RPL_WELCOME dès que PASS, NICK et USER sont configurés.",
    doc_file="docs/07_registration.md",
    doc_sections=["## 3. La séquence de registration", "## 4. Objectif attendu dans ce projet"]
)
def test_successful_registration(create_client, password):
    c = create_client("alice")
    c.connect()
    r = c.register(password)
    assert r is not None and " 001 " in r, "Pas de réponse 001 RPL_WELCOME reçue lors d'une registration valide."

@test_case(
    phase="PHASE 07 — Registration (PASS / NICK / USER / CAP)",
    name="Mauvais mot de passe",
    expected_behavior="Retourne le code numérique 464 ERR_PASSWDMISMATCH.",
    concept="cmd_pass() valide le mot de passe reçu par rapport à celui fourni au démarrage.",
    guidance="Vérifiez le mot de passe dès la commande PASS. Si le mot de passe est incorrect, renvoyez l'erreur 464 et fermez la connexion.",
    doc_file="docs/07_registration.md",
    doc_sections=["## 6.1 — `cmd_pass()` : vérification du mot de passe", "## 4. Objectif attendu dans ce projet"]
)
def test_bad_password(create_client, password):
    c = create_client("hacker")
    c.connect()
    c.register("MAUVAIS_MDP")
    c.recv_lines(0.5)
    # Check if 464 is anywhere in the received lines
    has_464 = any("464" in line for line in c.lines)
    assert has_464, "Le serveur n'a pas renvoyé le code d'erreur 464 (ERR_PASSWDMISMATCH) après un mauvais mot de passe."

@test_case(
    phase="PHASE 07 — Registration (PASS / NICK / USER / CAP)",
    name="Nick déjà pris",
    expected_behavior="Retourne le code numérique 433 ERR_NICKNAMEINUSE.",
    concept="Unicité du nickname (recherche par pseudo dans la liste des clients).",
    guidance="Si le pseudo proposé par la commande NICK est déjà utilisé par un autre client connecté, renvoyez l'erreur 433.",
    doc_file="docs/07_registration.md",
    doc_sections=["## 6.2 — `cmd_nick()` : choisir ou changer de pseudonyme", "## 4. Objectif attendu dans ce projet"]
)
def test_duplicate_nickname(create_client, password):
    c1 = create_client("dup")
    c1.connect()
    r1 = c1.register(password)
    assert r1 is not None, "Impossible d'enregistrer le premier client 'dup'."

    c2 = create_client("dup")
    c2.connect()
    c2.send(f"PASS {password}")
    c2.send("NICK dup")
    r2 = c2.wait("433")
    assert r2 is not None, "Le serveur n'a pas renvoyé l'erreur 433 (ERR_NICKNAMEINUSE) lors d'une tentative d'usurpation de pseudo."

@test_case(
    phase="PHASE 07 — Registration (PASS / NICK / USER / CAP)",
    name="Nick invalide",
    expected_behavior="Retourne le code numérique 432 ERR_ERRONEUSNICKNAME.",
    concept="Validation syntaxique du nickname (ne commence pas par un chiffre, etc.).",
    guidance="Vérifiez la validité du pseudo lors de l'appel à NICK. S'il contient des caractères invalides ou s'il commence par un chiffre, renvoyez l'erreur 432.",
    doc_file="docs/07_registration.md",
    doc_sections=["## 6.3 — Validation des nicks : `Utils::isValidNick()`", "## 4. Objectif attendu dans ce projet"]
)
def test_invalid_nickname(create_client, password):
    c = create_client("v")
    c.connect()
    c.send(f"PASS {password}")
    c.send("NICK 123bad")
    r = c.wait("432")
    assert r is not None, "Le serveur n'a pas renvoyé l'erreur 432 (ERR_ERRONEUSNICKNAME) pour le pseudo invalide '123bad'."

@test_case(
    phase="PHASE 07 — Registration (PASS / NICK / USER / CAP)",
    name="Négociation CAP LS",
    expected_behavior="Le serveur répond à CAP LS sans bloquer.",
    concept="Support minimaliste des capacités pour éviter le blocage des clients modernes.",
    guidance="Les clients modernes envoient CAP LS au début de la connexion. Le serveur doit y répondre (ex: 'CAP * LS :') au lieu de l'ignorer ou de planter.",
    doc_file="docs/07_registration.md",
    doc_sections=["## 6.6 — `cmd_cap()` : compatibilité IRCv3", "## 4. Objectif attendu dans ce projet"]
)
def test_cap_negotiation(create_client, password):
    c = create_client("cap")
    c.connect()
    c.send("CAP LS")
    r = c.wait("CAP", 1.0)
    assert r is not None, "Le serveur n'a pas répondu à la commande CAP LS."
