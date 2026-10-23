# Nebenkostenabrechnung- & Mietminderungs-Prüfer DACH (DE / AT / CH) 🇩🇪 🇦🇹 🇨🇭

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![DACH Mietrecht](https://img.shields.io/badge/Mietrecht-§_556_BGB_|_BetrKV_|_§§_21--24_MRG_|_Art._257a_OR-emerald.svg)](https://dach-digitalwerk.netlify.app/nebenkosten-check/)
[![Live Web-App](https://img.shields.io/badge/Web_App-100%25_Kostenlos_&_Lokal_im_Browser-indigo.svg)](https://dach-digitalwerk.netlify.app/nebenkosten-check/)
[![HeizkostenV](https://img.shields.io/badge/HeizkostenV-§_12_Kürzungsrecht_15%25_&_CO2KostAufG-amber.svg)](https://dach-digitalwerk.netlify.app/nebenkosten-check/)
[![Mietminderung 2026](https://img.shields.io/badge/Mietminderung-BGH_st._Rspr._Warmmiete-crimson.svg)](https://dach-digitalwerk.netlify.app/nebenkosten-check/)

> ⚖️ **Open-Source Prüf-Engine, Fehlererkennung & Widerspruchs-Generator für Nebenkosten- und Betriebskostenabrechnungen sowie Mietminderungsansprüche im gesamten DACH-Raum (Deutschland, Österreich, Schweiz).**  
> Entwickelt für Mieter, Mietervereine, Vermieter, Hausverwaltungen und Legal-Tech-Plattformen – 100 % clientseitig, ohne Server-Upload, DSGVO- und revDSG-konform.

---

### 🌐 Interaktiver Online-Rechner & Widerspruchs-Generator (Sofort im Browser nutzen)

**Überprüfen Sie Ihre Nebenkostenabrechnung in unter 3 Minuten auf unzulässige Posten, Fristversäumnisse und Kürzungsrechte:**  
👉 **[https://dach-digitalwerk.netlify.app/nebenkosten-check/](https://dach-digitalwerk.netlify.app/nebenkosten-check/)**

*(Weitere kostenlose DACH Legal- & Finanztolls: **[Abfindungs- & Kündigungsfrist-Rechner](https://dach-digitalwerk.netlify.app/abfindung-kuendigung/)** | **[Arbeitszeugnis Geheimcode-Decoder](https://dach-digitalwerk.netlify.app/arbeitszeugnis/)** | **[Swiss QR-Rechnung & XRechnung Suite](https://dach-digitalwerk.netlify.app/qr-suite/)** | **[Finanz- & Gehaltsrechner](https://dach-digitalwerk.netlify.app/rechner/)**)*

---

## Inhaltsverzeichnis
1. [Hintergrund: Warum über 50 % aller Nebenkostenabrechnungen fehlerhaft sind](#1-hintergrund-warum-über-50--aller-nebenkostenabrechnungen-fehlerhaft-sind)
2. [Umlagefähige vs. Nicht Umlagefähige Nebenkosten (Die große DACH-Vergleichstabelle)](#2-umlagefähige-vs-nicht-umlagefähige-nebenkosten-die-große-dach-vergleichstabelle)
3. [Die Blacklist unzulässiger Kostenarten (Verwaltung, Instandhaltung, Leerstand, Kabel-TV)](#3-die-blacklist-unzulässiger-kostenarten)
4. [Gesetzliche Abrechnungs- und Ausschlussfristen: § 556 Abs. 3 BGB, § 21 MRG & Art. 128 OR](#4-gesetzliche-abrechnungs--und-ausschlussfristen)
5. [Heizkostenverordnung: 15 % Kürzungsrecht (§ 12 HeizkostenV) & CO2-Kostenaufteilung](#5-heizkostenverordnung-15--kürzungsrecht--co2-kostenaufteilung)
6. [Mietminderungstabelle 2026: Quoten & taggenaue Berechnung nach BGH](#6-mietminderungstabelle-2026-quoten--taggenaue-berechnung-nach-bgh)
7. [Muster-Widerspruchsschreiben gegen die Nebenkostenabrechnung](#7-muster-widerspruchsschreiben-gegen-die-nebenkostenabrechnung)
8. [CLI- & Bibliotheks-Nutzung (Python & JavaScript)](#8-cli---bibliotheks-nutzung-python--javascript)
9. [Lizenz & DACH Digitalwerk Ökosystem](#9-lizenz--dach-digitalwerk-ökosystem)

---

## 1. Hintergrund: Warum über 50 % aller Nebenkostenabrechnungen fehlerhaft sind

Statistiken der Mieterbünde in Deutschland, Österreich und der Schweiz belegen übereinstimmend: **Jede zweite bis dritte Nebenkostenabrechnung enthält formelle oder inhaltliche Fehler**.

Zu den häufigsten Ursachen zählen:
* **Einschmuggeln von Instandhaltungs- und Reparaturkosten:** Der Vermieter überwälzt Handwerkerrechnungen für defekte Ventile, Rohrreparaturen oder Dachsanierungen unbemerkt in Sammelposten.
* **Unzulässige Verwaltungskosten:** Gebühren für Hausverwaltung, Bankspesen, Kontoführung oder Porto werden auf Mieter abgewälzt, obwohl sie gesetzlich mit der Grundmiete abgegolten sind.
* **Verstrichene Ausschlussfristen:** Abrechnungen gehen dem Mieter erst nach Ablauf der gesetzlichen 12-Monats-Frist zu (§ 556 Abs. 3 Satz 2 BGB). In diesem Fall ist die Nachforderung **kraft Gesetzes ausgeschlossen**!
* **Fehlendes Kürzungsrecht bei Heizkosten:** Wird nicht verbrauchsabhängig abgerechnet, hat der Mieter nach **§ 12 HeizkostenV ein 15-prozentiges Kürzungsrecht**.
* **Ende des Nebenkostenprivilegs für Kabelfernsehen (Deutschland ab 01.07.2024):** Sammelverträge für Breitbandkabel dürfen nicht mehr über die Betriebskosten abgerechnet werden.

---

## 2. Umlagefähige vs. Nicht Umlagefähige Nebenkosten (Die große DACH-Vergleichstabelle)

| Kostenart | 🇩🇪 Deutschland (§ 2 BetrKV) | 🇦🇹 Österreich (§§ 21–24 MRG) | 🇨🇭 Schweiz (Art. 257a/b OR, VMWG) | Typischer Fehler / Rechtsprechung |
| :--- | :---: | :---: | :---: | :--- |
| **Grundsteuer / Öffentliche Abgaben** | ✅ Umlagefähig (§ 2 Nr. 1) | ✅ Umlagefähig (§ 21 Abs. 1 Z 1) | ✅ Umlagefähig (Art. 257b OR) | Nur reine Grundsteuer, keine Erschließungsbeiträge |
| **Kaltwasser & Abwasser** | ✅ Umlagefähig (§ 2 Nr. 2 & 3) | ✅ Umlagefähig (§ 21 Abs. 1 Z 1) | ✅ Umlagefähig (Art. 5 VMWG) | Zählermiete ja, Geräteaustausch nein |
| **Aufzug / Lift** | ⚠️ Eingeschränkt (§ 2 Nr. 4) | ⚠️ Eingeschränkt (§ 24 MRG) | ⚠️ Eingeschränkt (Art. 5 VMWG) | **Nur Wartung & Betriebsstrom** – keine Reparaturen oder Ersatzteile! |
| **Straßenreinigung & Müll** | ✅ Umlagefähig (§ 2 Nr. 5) | ✅ Umlagefähig (§ 21 Abs. 1 Z 2) | ✅ Umlagefähig (Art. 5 VMWG) | Mülltonnenanschaffung ist Vermietersache |
| **Gebäudereinigung** | ✅ Umlagefähig (§ 2 Nr. 6) | ✅ Umlagefähig (§ 21 Abs. 1 Z 5) | ✅ Umlagefähig (Art. 5 VMWG) | Nur laufende Treppenhausreinigung |
| **Gartenpflege** | ⚠️ Eingeschränkt (§ 2 Nr. 7) | ⚠️ Eingeschränkt (§ 21 MRG) | ⚠️ Eingeschränkt | Laufende Pflege ja; Baumfällung wegen Alter oder Neuanlage unzulässig |
| **Hausbeleuchtung (Strom)** | ✅ Umlagefähig (§ 2 Nr. 8) | ✅ Umlagefähig (§ 21 Abs. 1 Z 3) | ✅ Umlagefähig (Art. 5 VMWG) | Nur Allgemeinstrom (Treppenhaus, Außen, Keller) |
| **Schornsteinfeger** | ✅ Umlagefähig (§ 2 Nr. 9) | ✅ Umlagefähig (§ 21 Abs. 1 Z 4) | ✅ Umlagefähig (Art. 5 VMWG) | Kehrgebühren und Immissionsmessung |
| **Sach- & Haftpflichtversicherung** | ⚠️ Eingeschränkt (§ 2 Nr. 10) | ⚠️ Eingeschränkt (§ 21 Abs. 1 Z 6) | ⚠️ Eingeschränkt | Gebäudebrand-, Haftpflicht-, Leitungswasser ja – **Rechtsschutz/Mietausfall unzulässig!** |
| **Hausmeister / Hauswart** | ⚠️ Prüfposten (§ 2 Nr. 11) | ⚠️ Prüfposten (§ 23 MRG) | ⚠️ Prüfposten (Art. 5 VMWG) | **Instandhaltungs- & Reparaturanteil (20–40 %) muss abgezogen werden!** |
| **Kabelanschluss / TV** | ❌ **UNZULÄSSIG** (seit 01.07.2024) | ⚠️ Nur mit Sondervereinbarung | ⚠️ Nur bei Vereinbarung | Wegfall des Nebenkostenprivilegs im TKG (Deutschland) |
| **Hausverwaltungshonorar** | ❌ **UNZULÄSSIG** (§ 1 Abs. 2 Nr. 1) | ⚠️ Nur Pauschalsatz (§ 22 MRG) | ❌ Grundsatz: Grundmiete | Kaufmännische Verwaltung ist keine Betriebskostenart |
| **Reparaturen & Instandhaltung** | ❌ **UNZULÄSSIG** (§ 1 Abs. 2 Nr. 2) | ❌ **UNZULÄSSIG** (§ 3 MRG) | ❌ **UNZULÄSSIG** (Art. 6 VMWG) | Reparaturen obliegen ausnahmslos dem Vermieter |
| **Instandhaltungsrücklage** | ❌ **UNZULÄSSIG** (§ 1 Abs. 2) | ❌ Kein Betriebskostenposten | ❌ **UNZULÄSSIG** (Art. 6 VMWG) | Vermögensbildung des Eigentümers |
| **Leerstandskosten** | ❌ **UNZULÄSSIG** (BGH VIII ZR 159/05) | ❌ **UNZULÄSSIG** (§ 17 MRG) | ❌ **UNZULÄSSIG** (BGer 4C.123/2005) | Vermieter muss Leerstandsanteile selbst tragen |

---

## 3. Die Blacklist unzulässiger Kostenarten

Wenn einer der folgenden Begriffe auf Ihrer Abrechnung erscheint, liegt in der Regel ein Kürzungs- bzw. Rückforderungsanspruch vor:

### 🚫 1. Verwaltungskosten (§ 1 Abs. 2 Nr. 1 BetrKV / Art. 257b OR)
* Hausverwaltungshonorar, Verwaltergebühr, WEG-Verwaltervergütung
* Kontoführungsgebühren, Bankspesen, Zinsen, Kreditkosten
* Telefon-, Porto- und Kopierkosten des Vermieters
* Kosten für Mieterwechsel, Wohnungsabnahme, Schufa-/Bonitätsprüfung
* Softwarelizenzen der Hausverwaltung

### 🚫 2. Instandhaltungs- und Reparaturkosten (§ 1 Abs. 2 Nr. 2 BetrKV / § 3 MRG / Art. 6 VMWG)
* Heizungsreparatur, Austausch Brenner, Pumpenreparatur (nur reine Wartung ist umlagefähig!)
* Dachreparaturen, Dachrinnenerneuerung, Fassadensanierung
* Behebung von Rohrbrüchen, Kanalreparaturen, Entstopfung verstopfter Fallrohre
* Reparatur von Klingel-, Sprech- oder Türschließanlagen
* Malerarbeiten und Schönheitsreparaturen bei Mieterwechsel

### 🚫 3. Rücklagen & Kapitalbildung
* Zuführung zur Instandhaltungsrücklage (WEG)
* Reparaturfonds, Erhaltungsbeiträge
* Tilgungsraten und Zinsen auf Hypothekendarlehen
* Abschreibungen (AfA) auf Gebäude oder Anlagen

### 🚫 4. Kosten leerstehender Wohnungen
* Stehen Wohnungen im Gebäude leer, darf der Vermieter die verbrauchsunabhängigen Fixkosten (z.B. Grundsteuer, Versicherungen, Müllgrundgebühr) **nicht auf die verbleibenden Mieter umlegen**.
* Die Verteilung muss stets nach der **gesamten Wohn- und Nutzfläche des Objekts** erfolgen (BGH Urteil vom 31.05.2006 – VIII ZR 159/05).

---

## 4. Gesetzliche Abrechnungs- und Ausschlussfristen

### 🇩🇪 Deutschland: § 556 Abs. 3 BGB
* **Abrechnungsfrist des Vermieters:** Die Abrechnung muss dem Mieter **spätestens bis zum Ablauf des zwölften Monats nach Ende des Abrechnungszeitraums** zugehen (§ 556 Abs. 3 Satz 2 BGB).
  * *Beispiel:* Abrechnungszeitraum 01.01.2024 bis 31.12.2024 $\rightarrow$ Fristende: **31.12.2025 (23:59 Uhr)**.
* **Rechtsfolge bei Verspätung (§ 556 Abs. 3 Satz 3 BGB):**  
  **Nachforderungen des Vermieters sind unwiederbringlich ausgeschlossen!**  
  *(Ausnahme: Der Vermieter hat die Verspätung nachweislich nicht selbst zu vertreten, z.B. verspäteter städtischer Grundsteuerbescheid).*
* **Wichtig:** Ein **Guthaben des Mieters verfällt nicht** und bleibt in voller Höhe einklagbar!
* **Einwendungsfrist des Mieters (§ 556 Abs. 3 Satz 5 BGB):**  
  Der Mieter muss Einwendungen gegen die Abrechnung **spätestens bis zum Ablauf des zwölften Monats nach Zugang** der Abrechnung schriftlich geltend machen.

### 🇦🇹 Österreich: § 21 Abs. 3 MRG / § 1486 ABGB
* Im Vollanwendungsbereich des Mietrechtsgesetzes (MRG) ist die Betriebskostenabrechnung für das vorangegangene Kalenderjahr **bis spätestens zum 30. Juni des Folgejahres** zu legen und den Mietern zur Einsicht aufzulegen.
* Ansprüche verjähren nach den allgemeinen mietrechtlichen Bestimmungen innerhalb von 3 Jahren (§ 1486 Z 4 ABGB). Bei Streitigkeiten entscheidet vorrangig die Schlichtungsstelle (§ 37 MRG).

### 🇨🇭 Schweiz: Art. 257a–257b OR / Art. 128 OR
* Nebenkosten sind nur geschuldet, wenn sie im Mietvertrag **ausdrücklich und präzise vereinbart** wurden (Art. 257a Abs. 2 OR). Pauschale Klauseln genügen nicht.
* Abrechnungsforderungen verjähren nach **5 Jahren** (Art. 128 Ziff. 1 OR). Der Mieter hat jederzeit Anspruch auf Einsicht in sämtliche Originalbelege (Art. 257b Abs. 2 OR).

---

## 5. Heizkostenverordnung: 15 % Kürzungsrecht & CO2-Kostenaufteilung

### 15 % Kürzungsrecht nach § 12 HeizkostenV (Deutschland)
Wird in einem Gebäude mit zentraler Heizungsanlage entgegen den Vorschriften der Heizkostenverordnung:
1. Nicht verbrauchsabhängig abgerechnet (z.B. 100 % nach Wohnfläche statt 50–70 % nach erfasstem Verbrauch), oder
2. Funktionieren die Heizkostenverteiler / Wärmemengenzähler über längere Zeit nicht,

**hat der Mieter das gesetzliche Recht, den auf ihn entfallenden Anteil an den Heiz- und Warmwasserkosten um 15 % zu kürzen (§ 12 Abs. 1 HeizkostenV)!**

---

### CO2-Kostenaufteilung für Wohngebäude (CO2KostAufG seit 2023)
Seit dem 01.01.2023 werden die CO2-Kosten für Brennstoffe anhand eines gesetzlichen **10-Stufen-Modells** abhängig vom spezifischen CO2-Ausstoß des Gebäudes aufgeteilt:

| Stufe | Kohlendioxidausstoß des Gebäudes ($kg\, CO_2 / m^2 / a$) | Anteil Vermieter | Anteil Mieter |
| :---: | :--- | :---: | :---: |
| **1** | $< 12$ (energieeffizient / Neubau) | **0 %** | 100 % |
| **2** | $12 \text{ bis } < 17$ | **10 %** | 90 % |
| **3** | $17 \text{ bis } < 22$ | **20 %** | 80 % |
| **4** | $22 \text{ bis } < 27$ | **30 %** | 70 % |
| **5** | $27 \text{ bis } < 32$ | **40 %** | 60 % |
| **6** | $32 \text{ bis } < 37$ | **50 %** | 50 % |
| **7** | $37 \text{ bis } < 42$ | **60 %** | 40 % |
| **8** | $42 \text{ bis } < 47$ | **70 %** | 30 % |
| **9** | $47 \text{ bis } < 52$ | **80 %** | 20 % |
| **10** | $\ge 52$ (unsaniert / energetisch mangelhaft) | **95 %** | 5 % |

*Weist der Vermieter die CO2-Kosten nicht gesondert aus oder teilt er sie nicht nach dem Stufenmodell auf, kann der Mieter seinen Heizkostenanteil um weitere **5 % nach § 12 Abs. 2 HeizkostenV** kürzen!*

---

## 6. Mietminderungstabelle 2026: Quoten & taggenaue Berechnung nach BGH

### Gesetzliche Grundlage (§ 536 BGB / § 1096 ABGB / Art. 259d OR)
* Die Mietminderung tritt **kraft Gesetzes** ein, sobald die Tauglichkeit der Mietsache zum vertragsgemäßen Gebrauch gemindert ist.
* **BGH-Urteil vom 06.04.2005 (VIII ZR 347/04 & XII ZR 225/03):**  
  **Die Bemessungsgrundlage für die Mietminderung ist stets die Bruttowarmmiete** (Grundmiete zuzüglich aller Nebenkostenvorauszahlungen und Heizkostenvorauszahlungen)!

$$\text{Minderungsbetrag} = \text{Bruttowarmmiete} \times \frac{\text{Minderungsquote in } \%}{100} \times \frac{\text{Tage des Mangels}}{\text{Monatstage}}$$

### Ausgewählte Quoten der Rechtsprechung:

| Mangel an der Mietsache | Typische Minderungsquote | Gerichtsurteil / Fundstelle |
| :--- | :---: | :--- |
| **Totalausfall der Heizung im Winter (Minusgrade)** | **70 % – 100 %** | LG Berlin GE 1993, 775 (100%); LG Hamburg WuM 1976, 10 (70%) |
| **Heizungsausfall in der Übergangszeit (unter 18 °C)** | **20 % – 30 %** | LG Kassel WuM 1987, 271 (30%); AG Köln WuM 1980, 17 (20%) |
| **Vollständiger Ausfall der Warmwasserversorgung** | **15 % – 30 %** | LG Berlin GE 1995, 493 (30%); AG München WuM 1986, 272 (15%) |
| **Erheblicher Schimmelbefall im Schlafzimmer/Wohnzimmer** | **20 % – 40 %** | LG Berlin GE 2007, 786 (40%); LG München I WuM 1985, 26 (30%) |
| **Schimmelpilzbildung im Badezimmer** | **10 % – 15 %** | AG Köln WuM 1992, 23 (10%); AG Dortmund WuM 1985, 261 (15%) |
| **Massiver Baulärm im Haus / Neubau nebenan** | **15 % – 35 %** | BGH VIII ZR 152/12; LG Hamburg ZMR 1987, 422 (25%) |
| **Totalausfall des Aufzugs (ab 3. Obergeschoss)** | **10 % – 20 %** | LG Hamburg WuM 1987, 345 (20%); LG Bremen WuM 1989, 448 (15%) |
| **Wasserschaden mit tropfender Decke & Trocknungsgeräten** | **30 % – 50 %** | LG Köln WuM 1996, 265 (50%); AG Nürnberg WuM 1986, 177 (30%) |
| **Schädlingsbefall (Kakerlaken, Bettwanzen, Ratten)** | **25 % – 50 %** | AG Berlin-Tiergarten MM 1988, 22 (50%); LG Berlin GE 2011, 417 (30%) |
| **Undichte Fenster mit starker Zugluft / Nässeeintritt** | **10 % – 20 %** | LG Berlin GE 1993, 1157 (20%); AG Rheine WuM 1984, 131 (15%) |

---

## 7. Muster-Widerspruchsschreiben gegen die Nebenkostenabrechnung

```text
Max Mustermann
Musterstraße 12, 10115 Berlin

An die
Hausverwaltung Muster GmbH
Immobilienstraße 45
10117 Berlin

Datum: 23. Oktober 2026

BETREFF: Widerspruch gegen die Nebenkostenabrechnung für das Abrechnungsjahr 2024
Mietvertrag vom: [Datum] | Mietobjekt: Musterstraße 12, 10115 Berlin (3. OG rechts)

Sehr geehrte Damen und Herren,

ich habe Ihre Nebenkostenabrechnung für den Zeitraum vom 01.01.2024 bis 31.12.2024 mit Datum vom 15.10.2025 erhalten, in welcher Sie eine Nachforderung von 250,00 EUR geltend machen.

Nach rechtlicher und buchhalterischer Prüfung widerspreche ich der Abrechnung aus folgenden Gründen:

1. Nicht umlagefähige Verwaltungskosten (§ 1 Abs. 2 Nr. 1 BetrKV):
   In der Abrechnung führen Sie die Position "Hausverwaltung" mit 250,00 EUR auf. Verwaltungskosten gehören nach ständiger Rechtsprechung des BGH nicht zu den Betriebskosten und sind mit der Kaltmiete abgegolten.

2. Instandhaltungs- und Reparaturkosten (§ 1 Abs. 2 Nr. 2 BetrKV):
   Die Position "Reparatur Klingelanlage" in Höhe von 180,00 EUR stellt eine Instandsetzungsmaßnahme dar, die ausschließlich dem Vermieter zur Last fällt.

3. Unzulässige Umlage Kabelfernsehen (Wegfall Nebenkostenprivileg):
   Die Umlage von Kabelgebühren in Höhe von 140,00 EUR ist seit der TKG-Novelle zum 01.07.2024 gesetzlich unzulässig.

Hieraus ergibt sich ein unberechtigter Gesamtabzug von 570,00 EUR. 
Unter Verrechnung mit der von Ihnen behaupteten Nachforderung errechnet sich zu meinen Gunsten ein:

👉 KORRIGIERTES GUTHABEN VON 320,00 EUR.

Ich fordere Sie hiermit höflich auf, den Guthabenbetrag von 320,00 EUR innerhalb von 14 Tagen, spätestens bis zum [Datum in 14 Tagen], auf mein unten genanntes Bankkonto zu überweisen.

Gleichzeitig mache ich von meinem gesetzlichen Belegeinsichtsrecht nach § 259 BGB Gebrauch und bitte um Mitteilung von drei Terminvorschlägen zur Einsichtnahme in die Originalbelege in Ihren Geschäftsräumen.

Mit freundlichen Grüßen,

[Unterschrift]
Max Mustermann
```

---

## 8. CLI- & Bibliotheks-Nutzung (Python & JavaScript)

### Python CLI & Library (`nebenkosten_pruefer.py`)

```bash
# Selbsttest ausführen
python nebenkosten_pruefer.py --test

# Schnelle Prüfung einer Abrechnung
python nebenkosten_pruefer.py \
  --country DE \
  --start 2024-01-01 \
  --end 2024-12-31 \
  --receipt 2025-10-15 \
  --total-cost 1250.0 \
  --prepaid 1000.0 \
  --letter
```

#### Verwendung als Python-Bibliothek:
```python
from nebenkosten_pruefer import audit_operating_cost_bill, check_billing_deadlines

# Fristprüfung nach § 556 BGB
res_deadline = check_billing_deadlines(
    country="DE",
    billing_period_end="2024-12-31",
    bill_receipt_date="2026-01-05",  # Nach 12-Monats-Frist!
    additional_claim=450.0
)

print(res_deadline["isClaimForfeited"])  # True -> Nachforderung verfallen!
```

---

### JavaScript / Node.js ES-Modul (`nebenkosten_pruefer.js`)

```javascript
const { auditOperatingCostBill, checkBillingDeadlines, calculateRentReduction } = require('./nebenkosten_pruefer.js');

// Abrechnung prüfen
const audit = auditOperatingCostBill({
  country: 'DE',
  billingPeriodStart: '2024-01-01',
  billingPeriodEnd: '2024-12-31',
  billReceiptDate: '2025-10-15',
  claimedTotalCost: 1500,
  prepaidAmount: 1100,
  items: [
    { name: 'Grundsteuer', amount: 150 },
    { name: 'Hausverwaltung', amount: 250 },     // Nicht umlagefähig!
    { name: 'Sanitär Reparatur', amount: 200 }    // Nicht umlagefähig!
  ]
});

console.log(audit.finalFinancialSummary.resultVerdict);
// -> GUTHABEN von 50.00 EUR (statt Nachforderung von 400 EUR!)
```

---

## 9. Lizenz & DACH Digitalwerk Ökosystem

Dieses Projekt ist unter der **[MIT-Lizenz](LICENSE)** lizenziert – freie Nutzung für private Mieter, Anwaltskanzleien und kommerzielle Softwareanwendungen.

### 🔗 Weitere kostenlose Legal-Tech Tools von DACH Digitalwerk:
* 🏢 **[Nebenkosten- & Mietminderungs-Check (Live Web-App)](https://dach-digitalwerk.netlify.app/nebenkosten-check/)**
* 💼 **[Abfindungs-, Kündigungsfrist- & Urlaubsabgeltungs-Rechner](https://dach-digitalwerk.netlify.app/abfindung-kuendigung/)**
* 📄 **[Arbeitszeugnis Geheimcode-Decoder & Noten-Scanner](https://dach-digitalwerk.netlify.app/arbeitszeugnis/)**
* 🇨🇭 **[Swiss QR-Rechnung & XRechnung 3.0 Generator Suite](https://dach-digitalwerk.netlify.app/qr-suite/)**
* 🧮 **[Interaktive DACH Finanz- & Steuerrechner Suite](https://dach-digitalwerk.netlify.app/rechner/)**
