#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DACH Nebenkostenabrechnung-, Betriebskosten- & Mietminderungs-Prüfer (DE / AT / CH)
Rechtsgrundlagen:
 - Deutschland: § 556 BGB, BetrKV, § 12 HeizkostenV, CO2KostAufG, § 536 BGB
 - Österreich: §§ 21–24 MRG, § 1096 ABGB, § 1486 ABGB
 - Schweiz: Art. 257a–257b OR, VMWG (SR 221.213.11), Art. 259d OR
Live Web-App & Generator: https://dach-digitalwerk.netlify.app/nebenkosten-check/
Copyright (c) 2026 DACH Digitalwerk (MIT License)
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple


# ==============================================================================
# 1. POSTEN-KLASSIFIZIERUNG & BLACKLIST (DE / AT / CH)
# ==============================================================================

# Nicht umlagefähige Posten nach BGB/BetrKV, MRG und OR/VMWG
NON_ALLOCATABLE_RULES = [
    {
        "category": "Verwaltungskosten",
        "keywords": [
            r"verwaltung", r"hausverwaltung", r"weg-verwaltung", r"verwalterhonorar",
            r"verwaltergebühr", r"bankgebühr", r"kontoführung", r"kontospesen",
            r"bankspesen", r"portokosten", r"porto", r"telefongebühr", r"kopierkosten",
            r"softwaregebühr", r"mieterwechsel", r"neuvermietung", r"schufa", r"bonitätsprüfung"
        ],
        "de_law": "§ 1 Abs. 2 Nr. 1 BetrKV (Verwaltungskosten sind keine Betriebskosten)",
        "at_law": "§ 22 MRG (Nur pauschalierter Höchstsatz zulässig; gesonderte Bank-/Verwaltergebühren unzulässig)",
        "ch_law": "Art. 5 Abs. 3 VMWG / Art. 257b OR (Allgemeine Verwaltungskosten mit Grundmiete abgegolten; Abrechnungspauschale max. 2–4%)",
        "description": "Kosten der kaufmännischen und technischen Hausverwaltung, Bankspesen, Software und Mieterwechselgebühren dürfen nicht als Nebenkosten abgerechnet werden.",
        "status": "UNZULAESSIG"
    },
    {
        "category": "Instandhaltung & Reparaturen",
        "keywords": [
            r"reparatur", r"instandhaltung", r"instandsetzung", r"sanierung",
            r"ersatz", r"austausch", r"erneuerung", r"rohrbruch", r"verstopfung",
            r"malerarbeit", r"anstrich", r"schloss", r"schlüsseldienst", r"kesselreparatur",
            r"dachreparatur", r"sanitärreparatur", r"armatur", r"wartung.*reparatur"
        ],
        "de_law": "§ 1 Abs. 2 Nr. 2 BetrKV (Instandhaltungs- und Instandsetzungskosten sind Vermietersache)",
        "at_law": "§ 3 MRG / § 1096 ABGB (Erhaltungsarbeiten sind Vermieterpflicht aus dem Mietzins)",
        "ch_law": "Art. 6 Abs. 1 VMWG / Art. 257b OR (Instandstellung, Erneuerung und Reparatur von Anlagen sind ausgeschlossen)",
        "description": "Reparaturen, Instandsetzung, Behebung von Abnutzungsschäden und Mängeln obliegen allein dem Vermieter und sind mit der Kaltmiete bezahlt.",
        "status": "UNZULAESSIG"
    },
    {
        "category": "Rücklagen & Finanzierungskosten",
        "keywords": [
            r"rücklage", r"instandhaltungsrücklage", r"erhaltungsbeitrag", r"reparaturfonds",
            r"liquiditätsreserve", r"zinsen", r"darlehen", r"hypothek", r"tilgung", r"afa", r"abschreibung"
        ],
        "de_law": "§ 1 Abs. 2 BetrKV (Kapitalkosten und Rücklagen gehören nicht zu Betriebskosten)",
        "at_law": "§ 31 MRG (Erhaltungs- und Verbesserungsbeitrag ist gesondert geregelt, keine Betriebskosten)",
        "ch_law": "Art. 6 Abs. 1 VMWG (Kapitalzinsen und Amortisationen dürfen nicht angerechnet werden)",
        "description": "Instandhaltungsrücklagen der WEG, Darlehenszinsen und Abschreibungen sind Vermögensaufbau des Eigentümers und unumlagefähig.",
        "status": "UNZULAESSIG"
    },
    {
        "category": "Leerstandskosten & Mietausfall",
        "keywords": [
            r"leerstand", r"mietausfall", r"mietausfallwagnis", r"leerstehend"
        ],
        "de_law": "BGH VIII ZR 159/05 (Vermieter trägt die verbrauchsunabhängigen Betriebskosten für leerstehende Wohnungen voll)",
        "at_law": "§ 17 MRG (Verteilung nach Nutzfläche; Vermieter trägt Leerstandsquote)",
        "ch_law": "BGer 4C.123/2005 (Leerstandskosten dürfen keinesfalls auf verbleibende Mieter überwälzt werden)",
        "description": "Kosten leerstehender Wohneinheiten müssen vom Vermieter selbst getragen werden und dürfen den Verteilerschlüssel anderer Mieter nicht erhöhen.",
        "status": "UNZULAESSIG"
    },
    {
        "category": "Nicht umlagefähige Versicherungen",
        "keywords": [
            r"rechtsschutz", r"mietausfallversicherung", r"vermieter-rechtsschutz",
            r"hausrat.*vermieter", r"vermögensschaden"
        ],
        "de_law": "§ 2 Nr. 13 BetrKV (Nur Sach- und Haftpflichtversicherung des Gebäudes; Rechtsschutz/Mietausfall unzulässig)",
        "at_law": "§ 21 Abs. 1 Z 6 MRG (Feuer-, Haftpflicht- und Leitungswasserschaden; keine Rechtsschutz)",
        "ch_law": "Art. 5 VMWG (Nur gebäudebezogene Sach- und Haftpflichtabgaben)",
        "description": "Rechtsschutzversicherungen des Vermieters und private Mietausfallpolicen sind keine umlagefähigen Betriebskosten.",
        "status": "UNZULAESSIG"
    },
    {
        "category": "Neuanschaffungen & Erstausstattung",
        "keywords": [
            r"kauf.*mülltonne", r"anschaffung.*container", r"neuanlage.*garten",
            r"anschaffung.*rasenmäher", r"spielplatz.*neubau", r"rauchmelder.*kauf",
            r"rauchwarnmelder.*anschaffung"
        ],
        "de_law": "BGH VIII ZR 346/15 (Erstanschaffung von Einrichtungsgegenständen oder Rauchmeldern ist Vermieteraufwand)",
        "at_law": "§ 3 MRG (Erst- und Neuinvestitionen fallen dem Hauseigentümer zur Last)",
        "ch_law": "Art. 6 VMWG (Neuanschaffungen sind wertvermehrende Investitionen, keine Nebenkosten)",
        "description": "Anschaffungskosten für Mülltonnen, Neuanlagen von Grünflächen oder der Kauf von Rauchmeldern (im Gegensatz zur jährlichen Prüfung) sind nicht umlagefähig.",
        "status": "UNZULAESSIG"
    },
    {
        "category": "Kabelanschluss / TV-Signal (Deutschland ab 01.07.2024)",
        "keywords": [
            r"kabelfernsehen", r"kabelanschluss", r"breitbandkabel", r"tv-signal", r"gemeinschaftsantenne"
        ],
        "de_law": "TKG-Novelle § 2 Nr. 15 BetrKV gestrichen zum 30.06.2024 (Nebenkostenprivileg für TV-Kabel entfallen)",
        "at_law": "§ 21 MRG (Nur bei individueller Sondervereinbarung)",
        "ch_law": "Art. 257b OR (Nur bei tatsächlicher Bereitstellung und vertraglicher Nennung)",
        "description": "In Deutschland ist die Umlage von Kabelfernsehgebühren über die Nebenkosten seit dem 01.07.2024 gesetzlich unzulässig (Ende des Nebenkostenprivilegs).",
        "status": "UNZULAESSIG_DE_AB_2024"
    },
    {
        "category": "Hausmeister / Hauswart (Prüfposten)",
        "keywords": [
            r"hausmeister", r"hauswart", r"facility management", r"hausbetreuung"
        ],
        "de_law": "§ 2 Nr. 14 BetrKV / BGH VIII ZR 27/07 (Instandhaltungs- und Verwaltungsanteile müssen zwingend herausgerechnet werden)",
        "at_law": "§ 23 MRG (Hausbesorgerarbeiten / Hausbetreuung; keine Erhaltungsarbeiten)",
        "ch_law": "Art. 5 VMWG (Reine Reinigung/Wartung ja; Reparaturarbeiten nein)",
        "description": "Führt der Hausmeister auch Reparaturen durch oder überwacht Handwerker/führt Wohnungsübergaben durch, muss dieser Instandhaltungs- und Verwaltungsanteil (üblicherweise 20–40 %) abgezogen werden.",
        "status": "PRUEFPOSTEN"
    },
    {
        "category": "Sonstige Betriebskosten (Prüfposten)",
        "keywords": [
            r"sonstige betriebskosten", r"sonstiges", r"verschiedenes", r"diverses",
            r"umlage sonstige", r"andere nebenkosten"
        ],
        "de_law": "§ 2 Nr. 17 BetrKV / BGH VIII ZR 167/03 (Pauschale Sammelposten sind unzulässig; jede Postenart muss im Mietvertrag konkret benannt sein)",
        "at_law": "§ 21 MRG (Taxativer Katalog; keine freien Sammelposten)",
        "ch_law": "Art. 257a Abs. 2 OR (Nebenkosten müssen im Mietvertrag detailliert aufgeführt sein)",
        "description": "Sammelbezeichnungen wie 'Sonstige Betriebskosten' sind unzulässig. Jede konkrete Position (z.B. Dachrinnenreinigung, Trinkwasserprüfung) muss einzeln im Mietvertrag vereinbart sein.",
        "status": "PRUEFPOSTEN"
    }
]

# Umlagefähige Standard-Betriebskosten nach § 2 BetrKV / MRG / VMWG
LEGITIMATE_OPERATING_COSTS_DE = [
    "1. Grundsteuer (§ 2 Nr. 1 BetrKV)",
    "2. Wasserversorgung (§ 2 Nr. 2 BetrKV)",
    "3. Entwässerung / Abwasser (§ 2 Nr. 3 BetrKV)",
    "4. Personen- und Lastenaufzug (§ 2 Nr. 4 BetrKV – nur Wartung & Betriebsstrom, KEINE Reparaturen)",
    "5. Straßenreinigung und Müllbeseitigung (§ 2 Nr. 5 BetrKV)",
    "6. Gebäudereinigung und Ungezieferbekämpfung (§ 2 Nr. 6 BetrKV)",
    "7. Gartenpflege (§ 2 Nr. 7 BetrKV – laufende Pflege)",
    "8. Beleuchtung Treppenhaus & Außenanlagen (§ 2 Nr. 8 BetrKV)",
    "9. Schornsteinreinigung (§ 2 Nr. 9 BetrKV)",
    "10. Sach- und Haftpflichtversicherung (§ 2 Nr. 10 BetrKV – Gebäude-, Brand-, Haftpflicht)",
    "11. Hauswart / Hausmeister (§ 2 Nr. 11 BetrKV – bereinigt um Reparatur-/Verwaltungsanteile)",
    "12. Gemeinschafts-Antennen / Verteiler (§ 2 Nr. 15 BetrKV alt – Kabelprivileg seit 01.07.2024 entfallen!)",
    "13. Wäschepflege-Einrichtungen (§ 2 Nr. 16 BetrKV)",
    "14. Sonstige Betriebskosten (§ 2 Nr. 17 BetrKV – nur wenn im Mietvertrag EINZELN präzise vereinbart)"
]


# ==============================================================================
# 2. FRISTEN-PRÜFUNG (DE / AT / CH)
# ==============================================================================

def parse_iso_date(date_str: str) -> date:
    """Parst ein Datum im Format YYYY-MM-DD oder DD.MM.YYYY."""
    date_str = str(date_str).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Ungültiges Datumsformat: '{date_str}'. Erwartet YYYY-MM-DD oder DD.MM.YYYY.")


def check_billing_deadlines(
    country: str,
    billing_period_end: str,
    bill_receipt_date: str,
    additional_claim: float
) -> Dict[str, Any]:
    """
    Prüft Abrechnungs- und Ausschlussfristen:
    - DE (§ 556 Abs. 3 Satz 2 BGB): 12-Monats-Frist für Nachforderungen des Vermieters.
    - AT (§ 21 Abs. 3 MRG): Abrechnungslegung bis 30. Juni des Folgejahres.
    - CH (Art. 128 OR): 5-jährige Verjährung; periodische Abrechnung.
    """
    c = country.upper()
    end_dt = parse_iso_date(billing_period_end)
    receipt_dt = parse_iso_date(bill_receipt_date)

    result = {
        "country": c,
        "billingPeriodEnd": str(end_dt),
        "billReceiptDate": str(receipt_dt),
        "additionalClaim": round(additional_claim, 2),
        "isClaimForfeited": False,
        "isTimely": True,
        "landlordDeadline": "",
        "tenantObjectionDeadline": "",
        "statutoryRule": "",
        "legalConsequence": "",
        "actionRecommendation": ""
    }

    if c == "DE":
        # § 556 Abs. 3 Satz 2 BGB: Ablauf des 12. Monats nach Ende des Abrechnungszeitraums.
        # Beispiel: Ende 31.12.2024 -> Fristende 31.12.2025
        deadline_year = end_dt.year + 1
        deadline_month = end_dt.month
        # Letzter Tag des Monats im Folgejahr
        if deadline_month == 12:
            landlord_deadline = date(deadline_year, 12, 31)
        else:
            # Erster Tag des Folgemonats minus 1 Tag
            import calendar
            last_day = calendar.monthrange(deadline_year, deadline_month)[1]
            landlord_deadline = date(deadline_year, deadline_month, last_day)

        # Mieter-Einwendungsfrist: 12 Monate nach Zugang (§ 556 Abs. 3 Satz 5 BGB)
        obj_year = receipt_dt.year + 1
        obj_month = receipt_dt.month
        import calendar
        last_day_obj = min(receipt_dt.day, calendar.monthrange(obj_year, obj_month)[1])
        tenant_objection_deadline = date(obj_year, obj_month, last_day_obj)

        result["landlordDeadline"] = str(landlord_deadline)
        result["tenantObjectionDeadline"] = str(tenant_objection_deadline)
        result["statutoryRule"] = "§ 556 Abs. 3 BGB (12-Monats-Ausschlussfrist)"

        if receipt_dt > landlord_deadline:
            result["isTimely"] = False
            if additional_claim > 0:
                result["isClaimForfeited"] = True
                result["legalConsequence"] = (
                    "Ausschlussfrist verstrichen: Der Vermieter kann eine Nachforderung NICHT mehr verlangen "
                    "(§ 556 Abs. 3 Satz 3 BGB). Ein etwaiges Guthaben des Mieters bleibt jedoch in voller Höhe bestehen!"
                )
                result["actionRecommendation"] = (
                    "Zahlung der Nachforderung mit Verweis auf § 556 Abs. 3 Satz 3 BGB verweigern. "
                    "Guthaben unverzüglich einfordern."
                )
            else:
                result["legalConsequence"] = (
                    "Abrechnung verspätet zugegangen. Das ausgewiesene Mieterguthaben bleibt voll wirksam."
                )
                result["actionRecommendation"] = "Guthaben vom Vermieter zur Auszahlung anfordern."
        else:
            result["isTimely"] = True
            result["legalConsequence"] = "Die Abrechnung ging dem Mieter fristgerecht innerhalb der 12 Monate zu."
            result["actionRecommendation"] = (
                f"Prüfung der einzelnen Posten vornehmen. Einwendungen müssen spätestens bis zum "
                f"{tenant_objection_deadline.strftime('%d.%m.%Y')} beim Vermieter eingehen."
            )

    elif c == "AT":
        # § 21 Abs. 3 MRG: Abrechnung für vorangegangenes Kalenderjahr bis zum 30. Juni des Folgejahres
        landlord_deadline = date(end_dt.year + 1, 6, 30)
        tenant_objection_deadline = date(receipt_dt.year + 3, receipt_dt.month, receipt_dt.day)

        result["landlordDeadline"] = str(landlord_deadline)
        result["tenantObjectionDeadline"] = str(tenant_objection_deadline)
        result["statutoryRule"] = "§ 21 Abs. 3 MRG / § 1486 ABGB"

        if receipt_dt > landlord_deadline:
            result["isTimely"] = False
            result["legalConsequence"] = (
                "Die Abrechnung wurde nicht bis zum gesetzlichen Stichtag (30. Juni des Folgejahres) gelegt. "
                "Nachforderungen können präkludiert sein; Antrag bei Schlichtungsstelle nach § 37 MRG möglich."
            )
            result["actionRecommendation"] = (
                "Abrechnung bei der Schlichtungsstelle oder Bezirksgericht auf ordnungsgemäße Legung überprüfen lassen."
            )
        else:
            result["isTimely"] = True
            result["legalConsequence"] = "Abrechnung innerhalb der Frist des § 21 Abs. 3 MRG zugegangen."
            result["actionRecommendation"] = "Belegeinsicht verlangen und einzelne Positionen auf MRG-Konformität prüfen."

    elif c == "CH":
        # Art. 128 OR: 5-jährige Verjährungsfrist
        landlord_deadline = date(end_dt.year + 5, end_dt.month, end_dt.day)
        tenant_objection_deadline = date(receipt_dt.year + 1, receipt_dt.month, receipt_dt.day)

        result["landlordDeadline"] = str(landlord_deadline)
        result["tenantObjectionDeadline"] = str(tenant_objection_deadline)
        result["statutoryRule"] = "Art. 257b OR i.V.m. Art. 128 OR (5 Jahre Verjährung)"

        if receipt_dt > landlord_deadline:
            result["isTimely"] = False
            result["isClaimForfeited"] = True
            result["legalConsequence"] = "Die Forderung ist nach Art. 128 OR verjährt."
            result["actionRecommendation"] = "Einrede der Verjährung erheben."
        else:
            result["isTimely"] = True
            result["legalConsequence"] = "Forderung ist unverjährt. Es besteht Anspruch auf Belegeinsicht (Art. 257b Abs. 2 OR)."
            result["actionRecommendation"] = (
                "Belegeinsicht (Rechnungen, Verträge) bei der Verwaltung verlangen. "
                "Prüfen, ob alle Posten ausdrücklich im Mietvertrag vereinbart sind (Art. 257a Abs. 2 OR)."
            )

    return result


# ==============================================================================
# 3. POSTEN-PRÜFER (ERKENNUNG UNZULÄSSIGER KOSTEN)
# ==============================================================================

def classify_line_item(name: str, amount: float, country: str = "DE") -> Dict[str, Any]:
    """
    Analysiert eine einzelne Abrechnungsposition auf Rechtmäßigkeit und Umlagefähigkeit.
    """
    c = country.upper()
    name_clean = name.strip()
    name_lower = name_clean.lower()
    amt = round(amount, 2)

    for rule in NON_ALLOCATABLE_RULES:
        for kw in rule["keywords"]:
            if re.search(r"\b" + kw + r"\b", name_lower, re.IGNORECASE) or kw in name_lower:
                law = rule["de_law"] if c == "DE" else rule["at_law"] if c == "AT" else rule["ch_law"]
                is_invalid = rule["status"] in ("UNZULAESSIG", "UNZULAESSIG_DE_AB_2024")
                
                # Wenn Kabelanschluss in Deutschland ab 2024
                if rule["status"] == "UNZULAESSIG_DE_AB_2024" and c != "DE":
                    continue

                # Empfohlener Abzugsbetrag
                recommended_deduction = amt
                if rule["status"] == "PRUEFPOSTEN":
                    if "hausmeister" in rule["category"].lower():
                        # Pauschaler Abzug von 25% Instandhaltungs-/Verwaltungsanteil empfohlen
                        recommended_deduction = round(amt * 0.25, 2)
                    else:
                        recommended_deduction = amt

                return {
                    "itemName": name_clean,
                    "claimedAmount": amt,
                    "status": rule["status"],
                    "isAllocatable": not is_invalid,
                    "category": rule["category"],
                    "matchedKeyword": kw,
                    "statutorySource": law,
                    "reason": rule["description"],
                    "recommendedDeduction": recommended_deduction
                }

    # Kein Treffer in der Blacklist -> vorläufig regulär
    return {
        "itemName": name_clean,
        "claimedAmount": amt,
        "status": "ZULAESSIG_GRUNDKATEGORIE",
        "isAllocatable": True,
        "category": "Reguläre Betriebskosten",
        "matchedKeyword": None,
        "statutorySource": "§ 2 BetrKV" if c == "DE" else "§ 21 MRG" if c == "AT" else "Art. 257b OR",
        "reason": "Entspricht dem Grunde nach einer zulässigen Betriebskostenart. Verteilerschlüssel und Belegeinsicht prüfen.",
        "recommendedDeduction": 0.0
    }


# ==============================================================================
# 4. HEIZKOSTENVERORDNUNG & CO2-AUFTEILUNG
# ==============================================================================

# CO2KostAufG Stufenmodell für Wohngebäude (§ 5 CO2KostAufG)
CO2_STUFENMODELL = [
    (12.0, 0.00, 1.00),   # <= 12 kg CO2: Vermieter 0%, Mieter 100%
    (17.0, 0.10, 0.90),   # 12 - 17: Vermieter 10%, Mieter 90%
    (22.0, 0.20, 0.80),   # 17 - 22: Vermieter 20%, Mieter 80%
    (27.0, 0.30, 0.70),   # 22 - 27: Vermieter 30%, Mieter 70%
    (32.0, 0.40, 0.60),   # 27 - 32: Vermieter 40%, Mieter 60%
    (37.0, 0.50, 0.50),   # 32 - 37: Vermieter 50%, Mieter 50%
    (42.0, 0.60, 0.40),   # 37 - 42: Vermieter 60%, Mieter 40%
    (47.0, 0.70, 0.30),   # 42 - 47: Vermieter 70%, Mieter 30%
    (52.0, 0.80, 0.20),   # 47 - 52: Vermieter 80%, Mieter 20%
    (float("inf"), 0.95, 0.05) # > 52 kg CO2: Vermieter 95%, Mieter 5%
]

def check_heating_and_co2(
    heating_share_amount: float,
    is_consumption_metered: bool = True,
    co2_kg_per_sqm_year: Optional[float] = None,
    total_co2_costs: float = 0.0
) -> Dict[str, Any]:
    """
    Prüft das 15%-Kürzungsrecht nach § 12 HeizkostenV und die CO2-Kostenaufteilung nach CO2KostAufG.
    """
    amt = round(heating_share_amount, 2)
    has_15pct_reduction = not is_consumption_metered
    reduction_15pct_amount = round(amt * 0.15, 2) if has_15pct_reduction else 0.0

    landlord_co2_pct = 0.0
    tenant_co2_pct = 100.0
    landlord_co2_amount = 0.0
    tenant_co2_amount = round(total_co2_costs, 2)

    if co2_kg_per_sqm_year is not None:
        for limit, l_share, t_share in CO2_STUFENMODELL:
            if co2_kg_per_sqm_year <= limit:
                landlord_co2_pct = round(l_share * 100, 1)
                tenant_co2_pct = round(t_share * 100, 1)
                landlord_co2_amount = round(total_co2_costs * l_share, 2)
                tenant_co2_amount = round(total_co2_costs * t_share, 2)
                break

    return {
        "heatingShareAmount": amt,
        "isConsumptionMetered": is_consumption_metered,
        "has15PercentReductionRight": has_15pct_reduction,
        "heatingReductionAmount": reduction_15pct_amount,
        "legalSource15Percent": "§ 12 Abs. 1 HeizkostenV (15% Kürzungsrecht bei fehlender oder nicht verbrauchsabhängiger Abrechnung)",
        "co2Evaluation": {
            "co2KgPerSqmYear": co2_kg_per_sqm_year,
            "totalCo2Costs": round(total_co2_costs, 2),
            "landlordSharePercentage": landlord_co2_pct,
            "tenantSharePercentage": tenant_co2_pct,
            "landlordDeductionAmount": landlord_co2_amount,
            "tenantRemainingAmount": tenant_co2_amount,
            "legalSourceCo2": "§§ 5–7 CO2-Kostenaufteilungsgesetz (CO2KostAufG 10-Stufen-Modell)"
        },
        "totalHeatingDeduction": round(reduction_15pct_amount + landlord_co2_amount, 2)
    }


# ==============================================================================
# 5. MIETMINDERUNGSTABELLE & BERECHNUNG (DE / AT / CH)
# ==============================================================================

# Anerkannte Gerichtsurteile zur Mietminderung (BGH / OLG / LG)
DEFECT_CATALOG = {
    "heizung_winter_total": {
        "title": "Totalausfall Heizung im Winter (Kälteperiode)",
        "rate_range": (70.0, 100.0),
        "typical_rate": 100.0,
        "court_reference": "LG Berlin GE 1993, 775 (100%); LG Hamburg WuM 1976, 10 (70%)",
        "description": "Vollständiger Ausfall der Heizungsanlage bei winterlichen Minustemperaturen."
    },
    "heizung_uebergang": {
        "title": "Heizungsausfall in der Übergangszeit (unter 18 °C)",
        "rate_range": (20.0, 50.0),
        "typical_rate": 30.0,
        "court_reference": "LG Kassel WuM 1987, 271 (30%); AG Köln WuM 1980, 17 (20%)",
        "description": "Zimmertemperaturen erreichen tagsüber nicht die Mindesttemperatur von 20–22 °C."
    },
    "warmwasser_total": {
        "title": "Totalausfall der Warmwasserversorgung",
        "rate_range": (15.0, 30.0),
        "typical_rate": 20.0,
        "court_reference": "AG München WuM 1986, 272 (15%); LG Berlin GE 1995, 493 (30%)",
        "description": "Kein warmes Wasser in Bad und Küche über mehrere Tage."
    },
    "schimmel_schlafzimmer": {
        "title": "Erheblicher Schimmelbefall im Schlafzimmer / Wohnzimmer",
        "rate_range": (20.0, 50.0),
        "typical_rate": 30.0,
        "court_reference": "LG München I WuM 1985, 26 (30%); LG Berlin GE 2007, 786 (40%)",
        "description": "Gesundheitsgefährdender Schimmelpilzbefall an Außenwänden/Fensterlaibungen."
    },
    "schimmel_bad": {
        "title": "Schimmelbildung im Badezimmer (Fugen / Decke)",
        "rate_range": (10.0, 20.0),
        "typical_rate": 15.0,
        "court_reference": "AG Köln WuM 1992, 23 (10%); AG Dortmund WuM 1985, 261 (15%)",
        "description": "Schimmelbildung trotz regelmäßiger Lüftung durch bauliche Wärmebrücken."
    },
    "baulaerm_massiv": {
        "title": "Massiver Baulärm im selben Haus / Nachbargrundstück",
        "rate_range": (15.0, 35.0),
        "typical_rate": 25.0,
        "court_reference": "BGH VIII ZR 152/12; LG Hamburg ZMR 1987, 422 (25%)",
        "description": "Abbrucharbeiten, Presslufthammer oder Kernsanierung werktags ab 7 Uhr."
    },
    "aufzug_ausfall_og": {
        "title": "Ausfall des Aufzugs (ab 3. OG)",
        "rate_range": (10.0, 20.0),
        "typical_rate": 15.0,
        "court_reference": "LG Bremen WuM 1989, 448 (15%); LG Hamburg WuM 1987, 345 (20%)",
        "description": "Fahrstuhldefekt über Tage/Wochen in oberen Etagen (insbes. für Senioren unzumutbar)."
    },
    "wasserschaden_decke": {
        "title": "Wasserschaden mit Durchfeuchtung der Zimmerdecke",
        "rate_range": (20.0, 50.0),
        "typical_rate": 35.0,
        "court_reference": "AG Nürnberg WuM 1986, 177 (30%); LG Köln WuM 1996, 265 (50%)",
        "description": "Rohrbruch in Oberwohnung führt zu tropfender Decke und Trocknungsgeräten."
    },
    "ungeziefer": {
        "title": "Ungezieferbefall (Bettwanzen, Schaben, Ratten)",
        "rate_range": (20.0, 60.0),
        "typical_rate": 30.0,
        "court_reference": "LG Berlin GE 2011, 417 (30%); AG Berlin-Tiergarten MM 1988, 22 (50%)",
        "description": "Erheblicher Schädlingsbefall ohne Verschulden des Mieters."
    },
    "undichte_fenster": {
        "title": "Undichte Fenster mit Zugluft und Feuchtigkeit",
        "rate_range": (10.0, 25.0),
        "typical_rate": 15.0,
        "court_reference": "AG Rheine WuM 1984, 131 (15%); LG Berlin GE 1993, 1157 (20%)",
        "description": "Starker Luftzug durch verzogene Fensterrahmen, erhebliche Wärmeverluste."
    }
}


def calculate_rent_reduction(
    country: str,
    monthly_warm_rent: float,
    defect_key: str,
    defect_days: int,
    days_in_month: int = 30,
    custom_reduction_rate: Optional[float] = None
) -> Dict[str, Any]:
    """
    Berechnet die taggenaue Mietminderung nach § 536 BGB (DE), § 1096 ABGB (AT) oder Art. 259d OR (CH).
    BGH ständige Rechtsprechung (BGH VIII ZR 347/04): Bemessungsgrundlage ist die Bruttowarmmiete!
    """
    c = country.upper()
    warm_rent = round(monthly_warm_rent, 2)
    defect_info = DEFECT_CATALOG.get(defect_key, {
        "title": defect_key,
        "rate_range": (10.0, 30.0),
        "typical_rate": 20.0,
        "court_reference": "Individuelle Einzelfallbeurteilung",
        "description": "Individuell geltend gemachter Mangel"
    })

    rate = custom_reduction_rate if custom_reduction_rate is not None else defect_info["typical_rate"]
    rate = max(0.0, min(100.0, rate))
    
    # BGH: Quote auf Bruttowarmmiete
    monthly_reduction = warm_rent * (rate / 100.0)
    
    # Tagesgenaue Umrechnung
    effective_days = max(1, min(days_in_month, defect_days))
    daily_reduction = monthly_reduction / max(1, days_in_month)
    total_reduction_amount = round(daily_reduction * effective_days, 2)

    statutory_law = (
        "§ 536 BGB i.V.m. BGH VIII ZR 347/04 (Berechnung auf Basis der Bruttowarmmiete)"
        if c == "DE" else
        "§ 1096 ABGB (Zinsbefreiung / Zinsminderung auf Bruttomiete)"
        if c == "AT" else
        "Art. 259d OR (Verhältnismässige Herabsetzung des Mietzinses)"
    )

    return {
        "country": c,
        "monthlyWarmRent": warm_rent,
        "defectKey": defect_key,
        "defectTitle": defect_info["title"],
        "courtReference": defect_info.get("court_reference", "§ 536 BGB"),
        "reductionRatePercent": rate,
        "defectDays": effective_days,
        "daysInMonth": days_in_month,
        "totalReductionAmount": total_reduction_amount,
        "dailyReductionAmount": round(daily_reduction, 2),
        "statutoryLaw": statutory_law,
        "noticeAdvice": (
            "Wichtig: Der Minderungsanspruch entsteht kraft Gesetzes ab Mängelanzeige (§ 536c BGB). "
            "Zahlung der Miete sollte stets schriftlich 'unter Vorbehalt der Rückforderung' erklärt werden!"
        )
    }


# ==============================================================================
# 6. GESAMT-AUDIT & WIDERSPRUCHS-GENERATOR
# ==============================================================================

def audit_operating_cost_bill(
    country: str,
    billing_period_start: str,
    billing_period_end: str,
    bill_receipt_date: str,
    claimed_total_cost: float,
    prepaid_amount: float,
    items: List[Dict[str, Any]],
    heating_share_amount: float = 0.0,
    heating_consumption_metered: bool = True,
    co2_kg_per_sqm: Optional[float] = None,
    total_co2_costs: float = 0.0,
    monthly_warm_rent: float = 0.0,
    rent_reduction_claims: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Führt einen vollständigen automatisierten Audit einer Nebenkostenabrechnung durch:
    1. Fristenprüfung (12-Monats-Ausschlussfrist)
    2. Posten-Klassifizierung und Aufdeckung nicht umlagefähiger Posten
    3. Heizkostenkürzung (§ 12 HeizkostenV & CO2KostAufG)
    4. Anrechnung von Mietminderungsansprüchen
    5. Berechnung des korrigierten Endbetrags (Ersparnis vs. Nachforderung)
    """
    c = country.upper()
    original_balance = round(claimed_total_cost - prepaid_amount, 2)
    
    # 1. Frist
    deadline_res = check_billing_deadlines(c, billing_period_end, bill_receipt_date, original_balance)

    # 2. Posten prüfen
    item_results = []
    total_invalid_deductions = 0.0
    for it in items:
        name = it.get("name", "Unbekannter Posten")
        amt = float(it.get("amount", 0.0))
        classified = classify_line_item(name, amt, country=c)
        item_results.append(classified)
        if classified["status"] in ("UNZULAESSIG", "UNZULAESSIG_DE_AB_2024"):
            total_invalid_deductions += classified["recommendedDeduction"]
        elif classified["status"] == "PRUEFPOSTEN" and it.get("force_deduct", False):
            total_invalid_deductions += classified["recommendedDeduction"]

    # 3. Heizung & CO2
    heating_res = check_heating_and_co2(
        heating_share_amount=heating_share_amount,
        is_consumption_metered=heating_consumption_metered,
        co2_kg_per_sqm_year=co2_kg_per_sqm,
        total_co2_costs=total_co2_costs
    )
    total_heating_deduction = heating_res["totalHeatingDeduction"]

    # 4. Mietminderung
    total_rent_reductions = 0.0
    rent_red_results = []
    if rent_reduction_claims and monthly_warm_rent > 0:
        for claim in rent_reduction_claims:
            d_key = claim.get("defect_key", "heizung_winter_total")
            d_days = int(claim.get("defect_days", 10))
            d_rate = claim.get("custom_rate")
            calc_red = calculate_rent_reduction(
                c, monthly_warm_rent, d_key, d_days, custom_reduction_rate=d_rate
            )
            rent_red_results.append(calc_red)
            total_rent_reductions += calc_red["totalReductionAmount"]

    # 5. Gesamtergebnis
    total_savings_potential = round(
        total_invalid_deductions + total_heating_deduction + total_rent_reductions, 2
    )

    if deadline_res["isClaimForfeited"]:
        # Frist versäumt: Nachforderung entfällt vollständig!
        corrected_balance = round(min(0.0, original_balance - total_savings_potential), 2)
        total_savings_realized = original_balance if original_balance > 0 else total_savings_potential
    else:
        corrected_balance = round(original_balance - total_savings_potential, 2)
        total_savings_realized = total_savings_potential

    currency = "CHF" if c == "CH" else "EUR"

    return {
        "country": c,
        "currency": currency,
        "inputSummary": {
            "billingPeriod": f"{billing_period_start} bis {billing_period_end}",
            "receiptDate": bill_receipt_date,
            "claimedTotalCost": round(claimed_total_cost, 2),
            "prepaidAmount": round(prepaid_amount, 2),
            "originalClaimedBalance": original_balance
        },
        "deadlineEvaluation": deadline_res,
        "itemAudits": item_results,
        "invalidItemsTotalDeduction": round(total_invalid_deductions, 2),
        "heatingEvaluation": heating_res,
        "heatingDeduction": round(total_heating_deduction, 2),
        "rentReductionAudits": rent_red_results,
        "rentReductionTotal": round(total_rent_reductions, 2),
        "finalFinancialSummary": {
            "originalClaimedBalance": original_balance,
            "totalSavingsIdentified": round(total_savings_realized, 2),
            "correctedFinalBalance": corrected_balance,
            "resultVerdict": (
                f"GUTHABEN von {abs(corrected_balance):.2f} {currency}"
                if corrected_balance < 0 else
                f"NACHZAHLUNG von {corrected_balance:.2f} {currency}"
                if corrected_balance > 0 else
                f"AUSGEGLICHEN (0.00 {currency})"
            )
        },
        "liveWebTool": "https://dach-digitalwerk.netlify.app/nebenkosten-check/"
    }


def generate_objection_letter(audit_result: Dict[str, Any], tenant_name: str, landlord_name: str) -> str:
    """
    Erstellt ein rechtssicheres, individualisiertes Widerspruchsschreiben als Textvorlage.
    """
    c = audit_result["country"]
    cur = audit_result["currency"]
    inp = audit_result["inputSummary"]
    fin = audit_result["finalFinancialSummary"]
    dl = audit_result["deadlineEvaluation"]

    today_str = date.today().strftime("%d.%m.%Y")
    orig_bal = inp["originalClaimedBalance"]
    orig_text = f"Nachforderung von {orig_bal:.2f} {cur}" if orig_bal >= 0 else f"Guthaben von {abs(orig_bal):.2f} {cur}"

    letter = [
        f"Absender: {tenant_name}",
        f"Empfänger: {landlord_name}",
        f"Datum: {today_str}\n",
        f"BETREFF: Widerspruch gegen die Betriebskostenabrechnung für den Zeitraum {inp['billingPeriod']}",
        f"Mietobjekt: Mietwohnung / Gewerbeeinheit",
        f"Rechtslage: {'§ 556 BGB / BetrKV / § 12 HeizkostenV' if c == 'DE' else '§§ 21–24 MRG' if c == 'AT' else 'Art. 257a–257b OR / VMWG'}\n",
        f"Sehr geehrte(r) {landlord_name},\n",
        f"ich habe Ihre Nebenkostenabrechnung für den Abrechnungszeitraum {inp['billingPeriod']} erhalten.",
        f"Darin weisen Sie eine {orig_text} aus.\n",
        "Nach sorgfältiger rechtlicher und rechnerischer Überprüfung muss ich der Abrechnung in mehreren Punkten widersprechen:\n"
    ]

    # Fristversäumnis
    if dl["isClaimForfeited"]:
        letter.append(
            f"1. VERFRISTUNG DER NACHFORDRUNG ({dl['statutoryRule']}):\n"
            f"   Die Abrechnung ging mir erst am {inp['receiptDate']} zu. Die gesetzliche Frist zur Mitteilung "
            f"   endete jedoch bereits am {dl['landlordDeadline']}. Gemäß {dl['statutoryRule']} ist die Geltendmachung "
            f"   einer Nachforderung damit ausgeschlossen.\n"
        )

    # Nicht umlagefähige Posten
    invalid_items = [it for it in audit_result["itemAudits"] if it["status"] in ("UNZULAESSIG", "UNZULAESSIG_DE_AB_2024") or (it["status"] == "PRUEFPOSTEN" and it["recommendedDeduction"] > 0)]
    if invalid_items:
        letter.append("2. UNZULÄSSIGE / NICHT UMLAGEFÄHIGE POSITIONEN:\n   Folgende Kostenarten dürfen nicht auf den Mieter umgelegt werden:")
        for it in invalid_items:
            letter.append(
                f"   - {it['itemName']}: {it['claimedAmount']:.2f} {cur} -> Abzug: {it['recommendedDeduction']:.2f} {cur} ({it['statutorySource']})"
            )
        letter.append(f"   Zwischensumme unzulässiger Abzüge: {audit_result['invalidItemsTotalDeduction']:.2f} {cur}\n")

    # Heizkostenkürzung
    heat = audit_result["heatingEvaluation"]
    if heat["has15PercentReductionRight"]:
        letter.append(
            f"3. KÜRZUNGSRECHT NACH § 12 HEIZKOSTENV (15 %):\n"
            f"   Da die Heiz- und Warmwasserkosten nicht ordnungsgemäß verbrauchsabhängig erfasst und abgerechnet wurden, "
            f"   mache ich hiermit von meinem Kürzungsrecht in Höhe von 15 % Gebrauch: Abzug {heat['heatingReductionAmount']:.2f} {cur}.\n"
        )
    if heat["co2Evaluation"]["landlordDeductionAmount"] > 0:
        letter.append(
            f"4. CO2-KOSTENAUFTEILUNG NACH CO2KOSTAUFG:\n"
            f"   Nach dem Stufenmodell entfällt auf den Vermieter ein Anteil von {heat['co2Evaluation']['landlordSharePercentage']} % "
            f"   an den CO2-Kosten (Abzug: {heat['co2Evaluation']['landlordDeductionAmount']:.2f} {cur}).\n"
        )

    # Mietminderung
    if audit_result["rentReductionAudits"]:
        letter.append("5. MIETMINDERUNG WEGEN WOHNUNGSMÄNGELN:")
        for r_red in audit_result["rentReductionAudits"]:
            letter.append(
                f"   - {r_red['defectTitle']} ({r_red['defectDays']} Tage): Abzug {r_red['totalReductionAmount']:.2f} {cur} ({r_red['statutoryLaw']})"
            )
        letter.append(f"   Summe Mietminderungsanspruch: {audit_result['rentReductionTotal']:.2f} {cur}\n")

    # Korrigierter Saldo
    corr_bal = fin["correctedFinalBalance"]
    letter.append(
        f"KORRIGIERTER SALDO:\n"
        f"Unter Berücksichtigung aller vorgenannten Punkte ergibt sich ein korrigierter Saldo von:\n"
        f"👉 {fin['resultVerdict']}\n"
    )

    if corr_bal < 0:
        letter.append(
            f"Ich fordere Sie hiermit höflich auf, das bestehende Guthaben in Höhe von {abs(corr_bal):.2f} {cur} "
            f"binnen 14 Tagen bis zum {(date.today()).strftime('%d.%m.%Y')} auf mein bekanntes Bankkonto zu überweisen."
        )
    else:
        letter.append(
            f"Die geforderte Nachforderung wird in der ursprünglichen Höhe zurückgewiesen. "
            f"Ich bitte um Zusendung einer korrigierten Abrechnung sowie um Gelegenheit zur Einsichtnahme "
            f"in die Originalbelege gemäß {'§ 259 BGB' if c == 'DE' else '§ 21 Abs. 3 MRG' if c == 'AT' else 'Art. 257b Abs. 2 OR'}."
        )

    letter.append("\nMit freundlichen Grüßen,\n\n" + tenant_name)
    return "\n".join(letter)


# ==============================================================================
# 7. CLI & SELBSTTEST
# ==============================================================================

def run_self_tests() -> bool:
    """Führt eine umfassende Testsuite für alle gesetzlichen Berechnungsfunktionen aus."""
    print("=" * 68)
    print("🧪 STARTE SELBSTTEST: DACH NEBENKOSTEN- & MIETMINDERUNGS-PRÜFER")
    print("=" * 68)

    # Test 1: Fristprüfung Deutschland fristgerecht vs verspätet
    res_de_timely = check_billing_deadlines("DE", "2024-12-31", "2025-11-15", 350.0)
    assert res_de_timely["isTimely"] is True, "Test 1a fehlgeschlagen: sollte fristgerecht sein"
    assert res_de_timely["isClaimForfeited"] is False, "Test 1b fehlgeschlagen"

    res_de_late = check_billing_deadlines("DE", "2024-12-31", "2026-01-05", 420.0)
    assert res_de_late["isTimely"] is False, "Test 1c fehlgeschlagen: sollte verspätet sein"
    assert res_de_late["isClaimForfeited"] is True, "Test 1d: Nachforderung muss verfallen sein"
    print("  ✅ Test 1 bestanden: 12-Monats-Frist § 556 Abs. 3 BGB (Frist vs. Verfall)")

    # Test 2: Erkennung unzulässiger Posten (Verwaltung, Instandhaltung, Rücklage, Leerstand)
    res_verw = classify_line_item("Hausverwaltung Jahresgebühr", 240.0, "DE")
    assert res_verw["isAllocatable"] is False, "Test 2a: Verwaltung muss unzulässig sein"
    assert res_verw["category"] == "Verwaltungskosten"

    res_rep = classify_line_item("Sanitär Reparatur undichte Rohre", 310.0, "DE")
    assert res_rep["isAllocatable"] is False, "Test 2b: Reparatur muss unzulässig sein"

    res_rueck = classify_line_item("Zuführung Instandhaltungsrücklage", 500.0, "DE")
    assert res_rueck["isAllocatable"] is False, "Test 2c: Rücklage muss unzulässig sein"

    res_kabel = classify_line_item("Kabelfernsehen Breitbandnetz", 120.0, "DE")
    assert res_kabel["isAllocatable"] is False, "Test 2d: Kabelfernsehen in DE ab 2024 unzulässig"

    res_reg = classify_line_item("Müllabfuhr und Straßenreinigung", 180.0, "DE")
    assert res_reg["isAllocatable"] is True, "Test 2e: Müllabfuhr muss zulässig sein"
    print("  ✅ Test 2 bestanden: Erkennung nicht umlagefähiger Posten (§ 1 BetrKV / BGH)")

    # Test 3: HeizkostenV 15% Kürzungsrecht & CO2-Stufenmodell
    res_heat = check_heating_and_co2(
        heating_share_amount=1200.0,
        is_consumption_metered=False,
        co2_kg_per_sqm_year=35.0,
        total_co2_costs=200.0
    )
    assert res_heat["has15PercentReductionRight"] is True, "Test 3a: 15% Recht muss aktiv sein"
    assert res_heat["heatingReductionAmount"] == 180.0, "Test 3b: 15% von 1200 muss 180.0 sein"
    assert res_heat["co2Evaluation"]["landlordSharePercentage"] == 50.0, "Test 3c: Stufe 35 kg CO2 muss 50% Vermieter sein"
    assert res_heat["co2Evaluation"]["landlordDeductionAmount"] == 100.0, "Test 3d: 50% von 200 = 100"
    print("  ✅ Test 3 bestanden: § 12 HeizkostenV (15 % Kürzung) + CO2KostAufG Stufenmodell")

    # Test 4: Mietminderung BGH auf Bruttowarmmiete
    res_rent = calculate_rent_reduction(
        country="DE",
        monthly_warm_rent=1200.0,
        defect_key="heizung_winter_total",
        defect_days=10,
        days_in_month=30
    )
    # 1200 * 100% * (10 / 30) = 400.00
    assert abs(res_rent["totalReductionAmount"] - 400.0) < 0.05, f"Test 4a fehlgeschlagen: {res_rent['totalReductionAmount']}"
    print("  ✅ Test 4 bestanden: Mietminderung nach BGH (Bruttowarmmiete & tagesgenaue Minderung)")

    # Test 5: Gesamt-Audit mit Ersparnis & Widerspruchsbrief
    sample_items = [
        {"name": "Grundsteuer", "amount": 150.0},
        {"name": "Hausverwaltung", "amount": 220.0},
        {"name": "Dachreparatur anteilig", "amount": 350.0},
        {"name": "Gebäudereinigung", "amount": 100.0}
    ]
    audit_res = audit_operating_cost_bill(
        country="DE",
        billing_period_start="2024-01-01",
        billing_period_end="2024-12-31",
        bill_receipt_date="2025-10-01",
        claimed_total_cost=820.0,
        prepaid_amount=600.0,
        items=sample_items,
        heating_share_amount=0.0,
        heating_consumption_metered=True
    )
    # Claimed balance: 820 - 600 = +220.0
    # Invalid deductions: 220 (Verwaltung) + 350 (Dachreparatur) = 570.0
    # Corrected balance: 220 - 570 = -350.0 (GUTHABEN von 350 EUR!)
    assert audit_res["finalFinancialSummary"]["originalClaimedBalance"] == 220.0, "Test 5a fehlgeschlagen"
    assert audit_res["invalidItemsTotalDeduction"] == 570.0, "Test 5b fehlgeschlagen"
    assert audit_res["finalFinancialSummary"]["correctedFinalBalance"] == -350.0, "Test 5c fehlgeschlagen"
    
    letter = generate_objection_letter(audit_res, "Max Mustermann", "Hausverwaltung Schmidt GmbH")
    assert "Widerspruch gegen die Betriebskostenabrechnung" in letter, "Test 5d fehlgeschlagen"
    assert "Dachreparatur" in letter, "Test 5e fehlgeschlagen"
    print("  ✅ Test 5 bestanden: Gesamt-Audit & Widerspruchsschreiben-Generierung")

    print("-" * 68)
    print("🎉 ALLE 5 TESTMODULE ERFOLGREICH BESTANDEN!")
    print("=" * 68)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="DACH Nebenkostenabrechnung- & Mietminderungs-Prüfer (DE / AT / CH)"
    )
    parser.add_argument("--test", action="store_true", help="Führt den automatisierten Selbsttest aus")
    parser.add_argument("--country", choices=["DE", "AT", "CH"], default="DE", help="Landeskennung (Standard: DE)")
    parser.add_argument("--start", default="2024-01-01", help="Beginn des Abrechnungszeitraums (YYYY-MM-DD)")
    parser.add_argument("--end", default="2024-12-31", help="Ende des Abrechnungszeitraums (YYYY-MM-DD)")
    parser.add_argument("--receipt", default="2025-10-15", help="Datum des Zugangs beim Mieter (YYYY-MM-DD)")
    parser.add_argument("--total-cost", type=float, default=1250.0, help="Gesamtkosten laut Abrechnung (EUR/CHF)")
    parser.add_argument("--prepaid", type=float, default=1000.0, help="Vorausgezahlte Nebenkosten (EUR/CHF)")
    parser.add_argument("--heating-share", type=float, default=500.0, help="Heizkostenanteil des Mieters")
    parser.add_argument("--unmetered-heating", action="store_true", help="Nicht verbrauchsabhängig abgerechnet (15%% Kürzungsrecht)")
    parser.add_argument("--co2-kg", type=float, default=None, help="Spezifischer CO2-Ausstoß des Gebäudes in kg/m²/Jahr")
    parser.add_argument("--co2-total-cost", type=float, default=0.0, help="Gesamte CO2-Kosten der Heizung")
    parser.add_argument("--warm-rent", type=float, default=1100.0, help="Monatliche Bruttowarmmiete für Mietminderung")
    parser.add_argument("--defect", choices=list(DEFECT_CATALOG.keys()), default=None, help="Mangel aus Mietminderungstabelle")
    parser.add_argument("--defect-days", type=int, default=10, help="Dauer des Mangels in Tagen")
    parser.add_argument("--items-json", type=str, default=None, help="JSON-String der Abrechnungsposten")
    parser.add_argument("--json", action="store_true", help="Ausgabe im JSON-Format")
    parser.add_argument("--letter", action="store_true", help="Erstellt das fertige Widerspruchsschreiben")
    parser.add_argument("--tenant", default="Max Mustermann", help="Name des Mieters")
    parser.add_argument("--landlord", default="Hausverwaltung Muster GmbH", help="Name des Vermieters")

    args = parser.parse_args()

    if args.test:
        success = run_self_tests()
        sys.exit(0 if success else 1)

    items = []
    if args.items_json:
        try:
            items = json.loads(args.items_json)
        except Exception as e:
            print(f"Fehler beim Parsen von --items-json: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Standard-Beispielposten für Demonstration
        items = [
            {"name": "Grundsteuer", "amount": 160.0},
            {"name": "Hausverwaltung", "amount": 250.0},
            {"name": "Reparatur Klingelanlage", "amount": 180.0},
            {"name": "Gartenpflege", "amount": 120.0},
            {"name": "Kabelanschluss Breitband", "amount": 140.0}
        ]

    rent_claims = []
    if args.defect:
        rent_claims.append({
            "defect_key": args.defect,
            "defect_days": args.defect_days
        })

    audit_res = audit_operating_cost_bill(
        country=args.country,
        billing_period_start=args.start,
        billing_period_end=args.end,
        bill_receipt_date=args.receipt,
        claimed_total_cost=args.total_cost,
        prepaid_amount=args.prepaid,
        items=items,
        heating_share_amount=args.heating_share,
        heating_consumption_metered=not args.unmetered_heating,
        co2_kg_per_sqm=args.co2_kg,
        total_co2_costs=args.co2_total_cost,
        monthly_warm_rent=args.warm_rent,
        rent_reduction_claims=rent_claims
    )

    if args.json:
        print(json.dumps(audit_res, indent=2, ensure_ascii=False))
        return

    cur = audit_res["currency"]
    inp = audit_res["inputSummary"]
    fin = audit_res["finalFinancialSummary"]
    dl = audit_res["deadlineEvaluation"]

    print("=" * 72)
    print(f" 🔍 DACH NEBENKOSTEN- & MIETMINDERUNGS-PRÜFER ({audit_res['country']})")
    print("=" * 72)
    print(f"Abrechnungszeitraum       : {inp['billingPeriod']}")
    print(f"Zugang beim Mieter        : {inp['receiptDate']}")
    print(f"Frist-Status              : {'✅ Fristgerecht' if dl['isTimely'] else '❌ VERSPÄTET / VERWIRKT'}")
    print(f"Gesetzliche Frist         : {dl['landlordDeadline']} ({dl['statutoryRule']})")
    print("-" * 72)
    print(f"Geforderte Gesamtkosten   : {inp['claimedTotalCost']:.2f} {cur}")
    print(f"Geleistete Vorauszahlung  : {inp['prepaidAmount']:.2f} {cur}")
    print(f"Ursprüngliche Forderung   : {inp['originalClaimedBalance']:.2f} {cur}")
    print("-" * 72)
    print(f"Erkannte unzulässige Posten : -{audit_res['invalidItemsTotalDeduction']:.2f} {cur}")
    if audit_res['heatingDeduction'] > 0:
        print(f"Heizkosten / CO2-Kürzung    : -{audit_res['heatingDeduction']:.2f} {cur}")
    if audit_res['rentReductionTotal'] > 0:
        print(f"Mietminderung Mängel        : -{audit_res['rentReductionTotal']:.2f} {cur}")
    print(f"Gesamtes Einsparpotenzial   : {fin['totalSavingsIdentified']:.2f} {cur}")
    print("=" * 72)
    print(f"👉 KORRIGIERTES ERGEBNIS    : {fin['resultVerdict']}")
    print("=" * 72)
    print(f"🌐 Interaktiver Online-Check : {audit_res['liveWebTool']}")
    print("-" * 72)

    if args.letter:
        print("\n" + "=" * 72)
        print("📝 GENERIERTES WIDERSPRUCHSSCHREIBEN (VORLAGE)")
        print("=" * 72)
        letter = generate_objection_letter(audit_res, args.tenant, args.landlord)
        print(letter)
        print("=" * 72)


if __name__ == "__main__":
    main()
