"""Editorial review of OneSpace FAQ and guided onboarding in Spanish, French and German.
All answer dates, membership rules and product constraints follow English source copy.
"""
FAQ_ROWS = [
  [
    "What is OneSpace?",
    "¿Qué es OneSpace?",
    "Qu’est-ce que OneSpace ?",
    "Was ist OneSpace?"
  ],
  [
    "A private app for two people in a relationship: a shared calendar, lists, reminders, trips, occasions, letters, little gestures, counters, places and memories in one place.",
    "Una app privada para dos personas que comparten su vida: calendario, listas, recordatorios, viajes, fechas especiales, cartas, detalles de cariño, contadores de días, lugares y recuerdos en un solo espacio.",
    "Une application privée pour deux personnes en couple : calendrier partagé, listes, rappels, voyages, occasions spéciales, lettres, petites attentions, compteurs de jours, lieux et souvenirs réunis au même endroit.",
    "Eine private App für zwei Menschen in einer Beziehung: gemeinsamer Kalender, Listen, Erinnerungen, Reisen, besondere Anlässe, Briefe, kleine Liebesgesten, Tageszähler, Orte und gemeinsame Erinnerungen."
  ],
  [
    "How do I get it?",
    "¿Cómo puedo probar OneSpace?",
    "Comment essayer OneSpace ?",
    "Wie kann ich OneSpace ausprobieren?"
  ],
  [
    "OneSpace is in an early test on Android.",
    "OneSpace está en fase de pruebas iniciales para Android.",
    "OneSpace est en phase de test sur Android.",
    "OneSpace befindet sich in der Android-Testphase."
  ],
  [
    ", confirm your email, and we will invite couples in small groups. iPhone is coming next.",
    ", confirma tu correo y enviaremos invitaciones a grupos pequeños de parejas. La versión para iPhone llegará más adelante.",
    ", confirmez votre adresse e-mail et nous inviterons progressivement de petits groupes de couples. La version iPhone est prévue ensuite.",
    ", bestätige deine E-Mail-Adresse und wir laden nach und nach kleine Gruppen von Paaren ein. Die iPhone-Version ist als Nächstes geplant."
  ],
  [
    "How do I invite my partner?",
    "¿Cómo invito a mi pareja?",
    "Comment inviter mon ou ma partenaire ?",
    "Wie lade ich meine Partnerperson ein?"
  ],
  [
    "After creating your space, share your invite code or its QR code. Your partner signs up and taps “Scan your partner’s QR code”. A space holds exactly two people.",
    "Cuando crees tu espacio, comparte el código de invitación o su código QR. Tu pareja puede registrarse y pulsar «Escanear el código QR de tu pareja». Cada espacio admite exactamente dos personas.",
    "Après avoir créé votre espace, partagez le code d’invitation ou son QR code. Votre partenaire s’inscrit puis choisit « Scanner le QR code de votre partenaire ». Un espace accueille exactement deux personnes.",
    "Erstelle euren Bereich und teile den Einladungscode oder den QR-Code. Deine Partnerperson meldet sich an und tippt auf „QR-Code des Partners scannen“. Ein Bereich ist für genau zwei Personen gedacht."
  ],
  [
    "Is it free?",
    "¿Es gratis?",
    "Est-ce gratuit ?",
    "Ist OneSpace kostenlos?"
  ],
  [
    "Yes, during the early test. If that ever changes, we will tell you clearly and in advance.",
    "Sí, durante las pruebas iniciales. Si esto cambia, te lo comunicaremos claramente y con antelación.",
    "Oui, pendant la phase de test. Si cela change, nous vous en informerons clairement et à l’avance.",
    "Ja, während der frühen Testphase. Sollte sich daran etwas ändern, informieren wir euch rechtzeitig und verständlich."
  ],
  [
    "What is the Founding 500?",
    "¿Qué son los primeros 500 miembros fundadores?",
    "Que signifie « Les 500 membres fondateurs » ?",
    "Was sind die ersten 500 Gründungsmitglieder?"
  ],
  [
    "The first 250 couples — 500 people — who join and confirm their email become Founder Members. You get the app first, a direct line to the team and a say in what we build.",
    "Las primeras 250 parejas (500 personas) que se inscriban y confirmen su correo serán miembros fundadores. Tendrán acceso anticipado a la app, contacto directo con el equipo y voz en las funciones futuras.",
    "Les 250 premiers couples (500 personnes) qui s’inscrivent et confirment leur e-mail deviennent membres fondateurs. Ils accèdent à l’application en avant-première, échangent directement avec l’équipe et participent aux choix des prochaines fonctionnalités.",
    "Die ersten 250 Paare (500 Personen), die sich anmelden und ihre E-Mail-Adresse bestätigen, werden Gründungsmitglieder. Sie erhalten frühzeitigen Zugang zur App, direkten Kontakt zum Team und können die weitere Entwicklung mitgestalten."
  ],
  [
    "Do we both need to sign up?",
    "¿Tenemos que registrarnos los dos?",
    "Devons-nous nous inscrire tous les deux ?",
    "Müssen wir uns beide anmelden?"
  ],
  [
    "One of you is enough to claim a place. After confirming, you get an invite link for your partner — they join under the same Founder number.",
    "Basta con que una persona reserve la plaza. Tras confirmar el correo, recibirá un enlace para invitar a su pareja, que compartirá el mismo número de miembros fundadores.",
    "Une seule personne peut réserver la place du couple. Après confirmation de son e-mail, elle reçoit un lien d’invitation pour son ou sa partenaire ; vous partagerez le même numéro fondateur.",
    "Es reicht, wenn sich eine Person anmeldet. Nach der E-Mail-Bestätigung erhält sie einen Einladungslink für die andere Person. Beide teilen sich dieselbe Gründungsnummer."
  ],
  [
    "When does our Founder number come?",
    "¿Cuándo recibiremos nuestro número de miembros fundadores?",
    "Quand recevons-nous notre numéro fondateur ?",
    "Wann bekommen wir unsere Gründungsnummer?"
  ],
  [
    "When you click the link in the confirmation email from founders@onespace.live. Numbers go in the order emails are confirmed.",
    "Cuando confirmes tu correo mediante el enlace enviado desde founders@onespace.live. Los números se asignan por orden de confirmación.",
    "Après avoir cliqué sur le lien de confirmation envoyé depuis founders@onespace.live. Les numéros sont attribués dans l’ordre des confirmations.",
    "Sobald du auf den Bestätigungslink in der E-Mail von founders@onespace.live klickst. Die Nummern werden in der Reihenfolge der Bestätigungen vergeben."
  ],
  [
    "The confirmation email didn’t arrive.",
    "No recibí el correo de confirmación.",
    "Je n’ai pas reçu l’e-mail de confirmation.",
    "Die Bestätigungs-E-Mail ist nicht angekommen."
  ],
  [
    "Check spam or Promotions for founders@onespace.live. Still nothing after 10 minutes? Sign up again with the same email and we will send a fresh link.",
    "Revisa Spam y Promociones y busca mensajes de founders@onespace.live. Si después de 10 minutos no ha llegado, vuelve a registrarte con el mismo correo y te enviaremos otro enlace.",
    "Vérifiez vos courriers indésirables et l’onglet Promotions pour trouver un message de founders@onespace.live. Si rien n’arrive après 10 minutes, réinscrivez-vous avec la même adresse : un nouveau lien vous sera envoyé.",
    "Prüfe den Spam- oder Werbeordner auf eine Nachricht von founders@onespace.live. Ist nach 10 Minuten nichts angekommen, melde dich mit derselben E-Mail-Adresse erneut an. Wir senden einen neuen Link."
  ],
  [
    "What do Founder Members get?",
    "¿Qué ventajas tienen los miembros fundadores?",
    "Quels sont les avantages des membres fondateurs ?",
    "Welche Vorteile haben Gründungsmitglieder?"
  ],
  [
    "Early access, a direct line to the team and a say in what we build. Founder benefits will be announced before any pricing is introduced.",
    "Acceso anticipado, contacto directo con el equipo y la posibilidad de influir en el desarrollo. Las ventajas adicionales se anunciarán antes de establecer los precios.",
    "Un accès anticipé, un contact direct avec l’équipe et la possibilité de contribuer au développement. Les avantages supplémentaires seront annoncés avant l’introduction de tarifs.",
    "Frühzeitiger Zugang, direkter Kontakt zum Team und die Möglichkeit, neue Funktionen mitzugestalten. Weitere Vorteile geben wir bekannt, bevor wir Preise einführen."
  ],
  [
    "Can I stop the emails?",
    "¿Puedo dejar de recibir correos?",
    "Puis-je arrêter de recevoir des e-mails ?",
    "Kann ich die E-Mails abbestellen?"
  ],
  [
    "Yes — every email has an Unsubscribe link, and your Founder number stays yours.",
    "Sí. Cada correo incluye un enlace para darte de baja. Conservarás tu número de miembro fundador.",
    "Oui. Chaque e-mail contient un lien de désinscription. Vous conservez votre numéro fondateur.",
    "Ja. Jede E-Mail enthält einen Link zum Abbestellen. Deine Gründungsnummer bleibt bestehen."
  ],
  [
    "Does it work for couples who live together?",
    "¿Sirve también para parejas que viven juntas?",
    "L’application convient-elle aux couples qui vivent ensemble ?",
    "Funktioniert OneSpace auch für Paare, die zusammenleben?"
  ],
  [
    "Yes. Choose “Together” and Today focuses on your home and shared plans. Distance-only messages are never sent.",
    "Sí. Selecciona «Viviendo juntos» y «Hoy» mostrará lo relativo al hogar y sus planes comunes. No se enviarán avisos específicos de la distancia.",
    "Oui. Choisissez « Vivre ensemble » : l’onglet « Aujourd’hui » mettra en avant votre foyer et vos projets communs, sans notifications réservées aux couples à distance.",
    "Ja. Wählt „Zusammenleben“, damit unter „Heute“ euer Zuhause und gemeinsame Pläne im Mittelpunkt stehen. Hinweise, die nur für Fernbeziehungen gedacht sind, werden nicht gesendet."
  ],
  [
    "Can I keep something from my partner?",
    "¿Puedo guardar algo solo para mí?",
    "Puis-je garder certains éléments privés ?",
    "Kann ich etwas nur für mich speichern?"
  ],
  [
    "Yes — mark items “Only me”, for example a surprise gift or occasion.",
    "Sí. Marca el elemento como «Solo yo», por ejemplo, si estás preparando un regalo sorpresa.",
    "Oui. Choisissez « Moi uniquement », par exemple pour préparer une surprise.",
    "Ja. Markiere Einträge als „Nur ich“, etwa wenn du eine Überraschung planst."
  ],
  [
    "Does it sync with my phone calendar?",
    "¿Se sincroniza con el calendario del teléfono?",
    "Peut-on synchroniser le calendrier du téléphone ?",
    "Kann ich meinen Smartphone-Kalender verbinden?"
  ],
  [
    "You can send OneSpace events one way to your phone calendar (Google, Samsung or iPhone calendar). Changes in your phone calendar do not come back.",
    "Puedes enviar eventos de OneSpace al calendario de tu teléfono (Google, Samsung o iPhone). La sincronización es unidireccional: los cambios realizados en el calendario del teléfono no vuelven a OneSpace.",
    "Vous pouvez envoyer les événements OneSpace vers le calendrier de votre téléphone (Google, Samsung ou iPhone). La synchronisation fonctionne dans un seul sens : les changements apportés au calendrier du téléphone ne reviennent pas dans OneSpace.",
    "Du kannst OneSpace-Termine an deinen Smartphone-Kalender übertragen (Google, Samsung oder iPhone). Die Synchronisierung erfolgt nur in eine Richtung: Änderungen im Smartphone-Kalender werden nicht an OneSpace zurückübertragen."
  ],
  [
    "Can I write my own love notes?",
    "¿Puedo escribir mis propios mensajes de cariño?",
    "Puis-je écrire mes propres mots doux ?",
    "Kann ich eigene Liebesnachrichten schreiben?"
  ],
  [
    "Yes. Every gesture can carry your own words, and you can set a private reminder to send a little love.",
    "Sí. Puedes personalizar cada gesto con tus propias palabras y programar un recordatorio privado para enviar un detalle de cariño.",
    "Oui. Vous pouvez accompagner chaque attention de vos propres mots et programmer un rappel privé pour envoyer un message tendre.",
    "Ja. Du kannst jede Liebesgeste mit eigenen Worten versehen und dir eine private Erinnerung einrichten, um deinem Lieblingsmenschen eine Freude zu machen."
  ],
  [
    "Which languages are supported?",
    "¿Qué idiomas admite la app?",
    "Quelles langues l’application prend-elle en charge ?",
    "Welche Sprachen unterstützt die App?"
  ],
  [
    "English and Arabic (right to left). Each of you picks your own.",
    "Inglés y árabe (con escritura de derecha a izquierda). Cada uno puede elegir el idioma de su app por separado.",
    "L’anglais et l’arabe (écriture de droite à gauche). Chaque partenaire peut choisir sa propre langue.",
    "Englisch und Arabisch (mit Rechts-nach-links-Schrift). Beide können ihre Sprache unabhängig voneinander wählen."
  ],
  [
    "Who can see our space?",
    "¿Quién puede ver nuestro espacio?",
    "Qui peut voir notre espace ?",
    "Wer kann unseren Bereich sehen?"
  ],
  [
    "Only the two members. Photos and documents are stored privately and opened with short-lived links.",
    "Solo los dos miembros. Las fotos y documentos se guardan de forma privada y se abren mediante enlaces temporales.",
    "Seuls les deux membres. Les photos et documents sont stockés de manière privée et accessibles au moyen de liens temporaires.",
    "Nur die beiden Mitglieder. Fotos und Dokumente werden privat gespeichert und über zeitlich begrenzte Links geöffnet."
  ],
  [
    "How do I export or delete my data?",
    "¿Cómo exporto o elimino mis datos?",
    "Comment exporter ou supprimer mes données ?",
    "Wie kann ich meine Daten exportieren oder löschen?"
  ],
  [
    "In the app: Me → Your data and account. Locked out? Use",
    "En la app: «Yo» → «Tus datos y cuenta». Si no puedes iniciar sesión, utiliza",
    "Dans l’application : « Moi » → « Vos données et votre compte ». Si vous ne pouvez pas vous connecter, utilisez",
    "In der App unter „Ich“ → „Deine Daten und dein Konto“. Wenn du dich nicht anmelden kannst, nutze"
  ],
  [
    "What happens if we break up?",
    "¿Qué ocurre si dejamos de estar juntos?",
    "Que se passe-t-il si nous nous séparons ?",
    "Was passiert, wenn wir uns trennen?"
  ],
  [
    "Either of you can leave the space at any time from Me. You can export first.",
    "Cualquiera de los dos puede abandonar el espacio desde «Yo» en cualquier momento. Antes puedes exportar tus datos.",
    "Chacun peut quitter l’espace à tout moment depuis « Moi ». Vous pouvez d’abord exporter vos données.",
    "Jede Person kann den gemeinsamen Bereich jederzeit unter „Ich“ verlassen. Vorher können die eigenen Daten exportiert werden."
  ],
  [
    "I can’t sign in.",
    "No puedo iniciar sesión.",
    "Je n’arrive pas à me connecter.",
    "Ich kann mich nicht anmelden."
  ],
  [
    "Use “Forgot password” on the sign-in screen, or",
    "Utiliza «¿Olvidaste tu contraseña?» en la pantalla de acceso o",
    "Utilisez « Mot de passe oublié » sur l’écran de connexion, ou",
    "Nutze auf dem Anmeldebildschirm „Passwort vergessen“ oder"
  ],
  [
    "How do I report a bug?",
    "¿Cómo notifico un problema técnico?",
    "Comment signaler un problème technique ?",
    "Wie melde ich einen technischen Fehler?"
  ],
  [
    "In the app: Me → Help and support → Report a technical issue (it can add a screenshot and the details we need). Or use the",
    "En la app: «Yo» → «Ayuda y soporte» → «Informar de un problema técnico». Puedes adjuntar una captura y los datos necesarios. También puedes usar el",
    "Dans l’application : « Moi » → « Aide et assistance » → « Signaler un problème technique ». Vous pouvez joindre une capture d’écran et les renseignements utiles. Vous pouvez aussi utiliser le",
    "In der App: „Ich“ → „Hilfe und Support“ → „Technisches Problem melden“. Dabei kannst du einen Screenshot und wichtige Angaben beifügen. Alternativ kannst du das"
  ],
  [
    "Is there an iPhone app?",
    "¿Habrá una app para iPhone?",
    "Une version iPhone est-elle prévue ?",
    "Ist eine iPhone-App geplant?"
  ],
  [
    "It is being prepared for TestFlight. Join early access and choose iPhone — we will invite you when it is ready.",
    "Estamos preparando una versión para TestFlight. Regístrate para el acceso anticipado y selecciona iPhone. Te invitaremos cuando esté lista.",
    "Nous préparons une version destinée à TestFlight. Inscrivez-vous à l’accès anticipé en choisissant iPhone ; vous recevrez une invitation lorsqu’elle sera prête.",
    "Eine TestFlight-Version ist in Vorbereitung. Melde dich für den Frühzugang an und wähle iPhone. Wir laden dich ein, sobald die Version bereit ist."
  ]
]
FAQ_EDITORIAL = {locale: {row[0]:row[i+1] for row in FAQ_ROWS} for i,locale in enumerate(("es","fr","de"))}
