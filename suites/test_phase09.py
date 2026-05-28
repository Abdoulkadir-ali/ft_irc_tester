from framework import test_case

@test_case(
    phase="PHASE 09 — Modes IRC (+i +t +k +l +o)",
    name="Consultation des modes (324)",
    expected_behavior="Le serveur répond par RPL_CHANNELMODEIS (324) contenant les modes actifs.",
    concept="MODE <canal> sans arguments interroge l'état actuel.",
    guidance="Lorsqu'un client interroge les modes d'un canal sans spécifier de changements, répondez avec le code numérique 324.",
    doc_file="docs/09_modes_irc.md",
    doc_sections=["## 5. Objectif attendu dans ce projet", "## 7.6 — `getModeString()` : la représentation textuelle"]
)
def test_mode_query(create_client, password):
    c = create_client("mq")
    c.connect()
    c.register(password)
    c.send("JOIN #mq")
    c.recv_lines(1.0)
    c.send("MODE #mq")
    r = c.wait("324")
    assert r is not None, "Le serveur n'a pas renvoyé le RPL_CHANNELMODEIS (324) attendu."

@test_case(
    phase="PHASE 09 — Modes IRC (+i +t +k +l +o)",
    name="Mode +i (Invite-only)",
    expected_behavior="Bloque les connexions de clients non invités avec le code 473.",
    concept="L'activation de +i restreint les entrées dans le canal aux invités.",
    guidance="Si le canal est en mode +i (invite-only), rejetez toute tentative de JOIN provenant d'un client qui n'a pas reçu d'invitation avec l'erreur 473.",
    doc_file="docs/09_modes_irc.md",
    doc_sections=["## 7.2 — Mode `+i/-i` : invite-only (sans paramètre)", "## 3. Tableau des modes implémentés"]
)
def test_mode_invite_only(create_client, password):
    op = create_client("iop")
    i = create_client("iint")
    
    op.connect()
    op.register(password)
    op.send("JOIN #inv")
    op.recv_lines(1.0)
    op.send("MODE #inv +i")
    op.recv_lines(1.0)

    i.connect()
    i.register(password)
    i.send("JOIN #inv")
    r = i.wait("473")
    assert r is not None, "Le client non invité a pu rejoindre ou n'a pas reçu l'erreur 473 (ERR_INVITEONLYCHAN)."

@test_case(
    phase="PHASE 09 — Modes IRC (+i +t +k +l +o)",
    name="Mode +k (Clé du canal)",
    expected_behavior="Rejette les JOIN sans clé ou avec une mauvaise clé avec le code 475.",
    concept="L'activation de +k exige un mot de passe (clé) pour rejoindre le canal.",
    guidance="Lorsque le mode +k est défini, vérifiez la clé lors de l'appel à JOIN. Si la clé est absente ou incorrecte, renvoyez l'erreur 475.",
    doc_file="docs/09_modes_irc.md",
    doc_sections=["## 7.3 — Mode `+k/-k` : clé/mot de passe (paramètre requis pour `+k`)", "## 3. Tableau des modes implémentés"]
)
def test_mode_key(create_client, password):
    op = create_client("kop2")
    u = create_client("kusr")
    
    op.connect()
    op.register(password)
    op.send("JOIN #kch2")
    op.recv_lines(1.0)
    op.send("MODE #kch2 +k pass123")
    op.recv_lines(1.0)

    u.connect()
    u.register(password)
    u.send("JOIN #kch2")
    r = u.wait("475")
    assert r is not None, "Le client a pu rejoindre sans clé ou n'a pas reçu l'erreur 475 (ERR_BADCHANNELKEY)."

@test_case(
    phase="PHASE 09 — Modes IRC (+i +t +k +l +o)",
    name="Mode +l (Limite de membres)",
    expected_behavior="Rejette les connexions si la limite d'utilisateurs est atteinte avec le code 471.",
    concept="Le mode +l limite le nombre maximum de clients admis simultanément.",
    guidance="Si le canal a atteint son quota défini par +l, refusez les nouveaux JOIN en renvoyant l'erreur 471.",
    doc_file="docs/09_modes_irc.md",
    doc_sections=["## 7.5 — Mode `+l/-l` : limite de membres (paramètre = nombre entier)", "## 3. Tableau des modes implémentés"]
)
def test_mode_limit(create_client, password):
    op = create_client("lop")
    u = create_client("lusr")
    
    op.connect()
    op.register(password)
    op.send("JOIN #lch")
    op.recv_lines(1.0)
    op.send("MODE #lch +l 1")
    op.recv_lines(1.0)

    u.connect()
    u.register(password)
    u.send("JOIN #lch")
    r = u.wait("471")
    assert r is not None, "Le client a pu rejoindre le canal plein ou n'a pas reçu l'erreur 471 (ERR_CHANNELISFULL)."

@test_case(
    phase="PHASE 09 — Modes IRC (+i +t +k +l +o)",
    name="Vérification opérateur (482)",
    expected_behavior="Rejette les modifications de modes faites par un non-opérateur avec le code 482.",
    concept="Seuls les opérateurs du canal ont le privilège de modifier les modes (ERR_CHANOPRIVSNEEDED).",
    guidance="Avant d'appliquer une modification de mode sur un canal, validez que le client émetteur est enregistré en tant qu'opérateur de ce canal. Sinon, renvoyez l'erreur 482.",
    doc_file="docs/09_modes_irc.md",
    doc_sections=["## 7.1 — Structure générale de `cmd_mode()`", "## 6. Pourquoi ces objectifs ?"]
)
def test_mode_operator_privs(create_client, password):
    op = create_client("oop")
    u = create_client("ousr")
    
    op.connect()
    op.register(password)
    op.send("JOIN #och")
    op.recv_lines(1.0)

    u.connect()
    u.register(password)
    u.send("JOIN #och")
    u.recv_lines(1.0)
    u.send("MODE #och +i")
    
    r = u.wait("482")
    assert r is not None, "Un utilisateur non-opérateur a pu changer le mode ou n'a pas reçu l'erreur 482 (ERR_CHANOPRIVSNEEDED)."
