"""Editorial mega-menu strings: quiet, clear navigation in all five website languages."""
MENU_WORDS = {
  "Explore the app": {
    "ar": "اكتشف التطبيق",
    "es": "Descubre la app",
    "fr": "Découvrir l’application",
    "de": "App entdecken"
  },
  "Everything, in one shared space": {
    "ar": "كل تفاصيل حياتكما في مساحة واحدة",
    "es": "Todo, en un espacio compartido",
    "fr": "Tout, dans un espace commun",
    "de": "Alles an einem gemeinsamen Ort"
  },
  "Planning together": {
    "ar": "خططا معًا",
    "es": "Organizarse juntos",
    "fr": "S’organiser à deux",
    "de": "Gemeinsam planen"
  },
  "Staying connected": {
    "ar": "ابقيا قريبين",
    "es": "Mantenerse cerca",
    "fr": "Rester proches",
    "de": "In Verbindung bleiben"
  },
  "Everyday essentials": {
    "ar": "تفاصيل الحياة اليومية",
    "es": "El día a día",
    "fr": "Le quotidien",
    "de": "Der gemeinsame Alltag"
  },
  "See all features": {
    "ar": "عرض كل المزايا",
    "es": "Ver todas las funciones",
    "fr": "Voir toutes les fonctionnalités",
    "de": "Alle Funktionen ansehen"
  },
  "Built for both of you": {
    "ar": "مصمم لحياتكما معًا",
    "es": "Pensado para los dos",
    "fr": "Conçu pour vous deux",
    "de": "Für euch beide gemacht"
  },
  "Near or far, stay in sync": {
    "ar": "قريبين أو بعيدين، ابقيا على تواصل",
    "es": "Cerca o lejos, siempre conectados",
    "fr": "Près ou loin, restez en lien",
    "de": "Ob nah oder fern – bleibt verbunden"
  },
  "Find your rhythm": {
    "ar": "اختارا ما يناسب حياتكما",
    "es": "Encuentren su ritmo",
    "fr": "Trouvez votre rythme",
    "de": "Findet euren Rhythmus"
  },
  "Learn OneSpace": {
    "ar": "تعرّف على OneSpace",
    "es": "Aprende a usar OneSpace",
    "fr": "Découvrir OneSpace",
    "de": "OneSpace kennenlernen"
  },
  "Help, ideas and updates": {
    "ar": "مساعدة وأفكار وتحديثات",
    "es": "Ayuda, ideas y novedades",
    "fr": "Aide, idées et actualités",
    "de": "Hilfe, Ideen und Neuigkeiten"
  },
  "Get started": {
    "ar": "ابدأ الآن",
    "es": "Primeros pasos",
    "fr": "Bien démarrer",
    "de": "Erste Schritte"
  },
  "More to explore": {
    "ar": "استكشف المزيد",
    "es": "Más para descubrir",
    "fr": "Pour aller plus loin",
    "de": "Mehr entdecken"
  },
  "Explore the guides": {
    "ar": "استكشف الأدلة",
    "es": "Explorar las guías",
    "fr": "Découvrir les guides",
    "de": "Ratgeber entdecken"
  }
}
MENU_EDITORIAL = {lang:{key:row[lang] for key,row in MENU_WORDS.items()} for lang in ("es","fr","de")}
