from framework import test_case

@test_case(
    phase="PHASE 11 — Réponses numériques (format RFC 2812)",
    name="Format 001 RPL_WELCOME",
    expected_behavior="Le format de la réponse 001 respecte la RFC (':serveur 001 nick :texte').",
    concept="Reply::numeric() construit la réponse standardisée avec préfixe et destinataire.",
    guidance="Assurez-vous que les réponses numériques respectent la structure : ':nom_serveur NUMERO_RETOUR pseudo :message'.",
    doc_file="docs/11_reponses_numeriques.md",
    doc_sections=["## 3. Format d'une réponse numérique", "## 6.1 — Messages de bienvenue (001–004)"]
)
def test_numeric_reply_format(create_client, password):
    c = create_client("fmt")
    c.connect()
    r = c.register(password)
    assert r is not None, "La registration a échoué, impossible de vérifier le format 001."
    
    # Check that we received 001 and format it
    l001 = next((line for line in c.lines if " 001 " in line), None)
    assert l001 is not None, "Pas de réponse 001 RPL_WELCOME trouvée."
    
    parts = l001.split(" ")
    assert parts[0].startswith(":"), f"La réponse doit commencer par ':' (obtenu: {parts[0]})."
    assert parts[1] == "001", f"Le code numérique doit être 001 (obtenu: {parts[1]})."
    assert parts[2] == "fmt", f"Le destinataire de la réponse doit être le pseudo 'fmt' (obtenu: {parts[2]})."

@test_case(
    phase="PHASE 11 — Réponses numériques (format RFC 2812)",
    name="Nick '*' avant registration",
    expected_behavior="L'erreur de mot de passe utilise le pseudo '*' dans la réponse numérique.",
    concept="Reply::nick_or_star() utilise '*' si le pseudo n'est pas encore défini.",
    guidance="Tant que le client n'est pas totalement enregistré et n'a pas de pseudo valide, toutes les erreurs numériques doivent utiliser '*' à la place du pseudo.",
    doc_file="docs/11_reponses_numeriques.md",
    doc_sections=["## 5. Pourquoi ces objectifs ?", "## 6.4 — Erreurs de nick (43x)"]
)
def test_star_nick_before_registration(create_client, password):
    c = create_client("st")
    c.connect()
    c.send("PASS MAUVAIS_MDP")
    c.recv_lines(1.0)
    
    l464 = next((line for line in c.lines if "464" in line), None)
    assert l464 is not None, "Pas d'erreur 464 (ERR_PASSWDMISMATCH) renvoyée pour mot de passe incorrect."
    
    parts = l464.split(" ")
    assert len(parts) >= 3, f"La réponse numérique 464 est mal formatée: '{l464}'"
    assert parts[2] == "*", f"Le pseudo pré-registration doit être '*' (obtenu: '{parts[2]}' dans '{l464}')."
