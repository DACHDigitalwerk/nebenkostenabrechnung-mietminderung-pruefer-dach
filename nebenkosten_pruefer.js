/**
 * DACH Nebenkostenabrechnung-, Betriebskosten- & Mietminderungs-Prüfer (DE / AT / CH)
 * Rechtsgrundlagen:
 *  - Deutschland: § 556 BGB, BetrKV, § 12 HeizkostenV, CO2KostAufG, § 536 BGB
 *  - Österreich: §§ 21–24 MRG, § 1096 ABGB, § 1486 ABGB
 *  - Schweiz: Art. 257a–257b OR, VMWG (SR 221.213.11), Art. 259d OR
 * Live Web-App: https://dach-digitalwerk.netlify.app/nebenkosten-check/
 * Copyright (c) 2026 DACH Digitalwerk (MIT License)
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.NebenkostenPruefer = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // 1. BLACKLIST & REGELWERK
  const NON_ALLOCATABLE_RULES = [
    {
      category: 'Verwaltungskosten',
      keywords: [
        'verwaltung', 'hausverwaltung', 'weg-verwaltung', 'verwalterhonorar',
        'verwaltergebühr', 'bankgebühr', 'kontoführung', 'kontospesen',
        'bankspesen', 'portokosten', 'porto', 'telefongebühr', 'kopierkosten',
        'softwaregebühr', 'mieterwechsel', 'neuvermietung', 'schufa', 'bonitätsprüfung'
      ],
      deLaw: '§ 1 Abs. 2 Nr. 1 BetrKV (Verwaltungskosten sind keine Betriebskosten)',
      atLaw: '§ 22 MRG (Nur pauschalierter Höchstsatz zulässig; gesonderte Bank-/Verwaltergebühren unzulässig)',
      chLaw: 'Art. 5 Abs. 3 VMWG / Art. 257b OR (Allgemeine Verwaltungskosten mit Grundmiete abgegolten; Abrechnungspauschale max. 2–4%)',
      description: 'Kosten der kaufmännischen und technischen Hausverwaltung, Bankspesen, Software und Mieterwechselgebühren dürfen nicht als Nebenkosten abgerechnet werden.',
      status: 'UNZULAESSIG'
    },
    {
      category: 'Instandhaltung & Reparaturen',
      keywords: [
        'reparatur', 'instandhaltung', 'instandsetzung', 'sanierung',
        'ersatz', 'austausch', 'erneuerung', 'rohrbruch', 'verstopfung',
        'malerarbeit', 'anstrich', 'schloss', 'schlüsseldienst', 'kesselreparatur',
        'dachreparatur', 'sanitärreparatur', 'armatur'
      ],
      deLaw: '§ 1 Abs. 2 Nr. 2 BetrKV (Instandhaltungs- und Instandsetzungskosten sind Vermietersache)',
      atLaw: '§ 3 MRG / § 1096 ABGB (Erhaltungsarbeiten sind Vermieterpflicht aus dem Mietzins)',
      chLaw: 'Art. 6 Abs. 1 VMWG / Art. 257b OR (Instandstellung, Erneuerung und Reparatur von Anlagen sind ausgeschlossen)',
      description: 'Reparaturen, Instandsetzung, Behebung von Abnutzungsschäden und Mängeln obliegen allein dem Vermieter und sind mit der Kaltmiete bezahlt.',
      status: 'UNZULAESSIG'
    },
    {
      category: 'Rücklagen & Finanzierungskosten',
      keywords: [
        'rücklage', 'instandhaltungsrücklage', 'erhaltungsbeitrag', 'reparaturfonds',
        'liquiditätsreserve', 'zinsen', 'darlehen', 'hypothek', 'tilgung', 'afa', 'abschreibung'
      ],
      deLaw: '§ 1 Abs. 2 BetrKV (Kapitalkosten und Rücklagen gehören nicht zu Betriebskosten)',
      atLaw: '§ 31 MRG (Erhaltungs- und Verbesserungsbeitrag gesondert geregelt)',
      chLaw: 'Art. 6 Abs. 1 VMWG (Kapitalzinsen und Amortisationen dürfen nicht angerechnet werden)',
      description: 'Instandhaltungsrücklagen der WEG, Darlehenszinsen und Abschreibungen sind Vermögensaufbau des Eigentümers und unumlagefähig.',
      status: 'UNZULAESSIG'
    },
    {
      category: 'Leerstandskosten & Mietausfall',
      keywords: ['leerstand', 'mietausfall', 'mietausfallwagnis', 'leerstehend'],
      deLaw: 'BGH VIII ZR 159/05 (Vermieter trägt verbrauchsunabhängige Betriebskosten für leerstehende Wohnungen voll)',
      atLaw: '§ 17 MRG (Verteilung nach Nutzfläche; Vermieter trägt Leerstandsquote)',
      chLaw: 'BGer 4C.123/2005 (Leerstandskosten dürfen keinesfalls auf verbleibende Mieter überwälzt werden)',
      description: 'Kosten leerstehender Wohneinheiten müssen vom Vermieter selbst getragen werden und dürfen den Verteilerschlüssel anderer Mieter nicht erhöhen.',
      status: 'UNZULAESSIG'
    },
    {
      category: 'Nicht umlagefähige Versicherungen',
      keywords: ['rechtsschutz', 'mietausfallversicherung', 'vermieter-rechtsschutz', 'vermögensschaden'],
      deLaw: '§ 2 Nr. 13 BetrKV (Nur Sach- und Haftpflichtversicherung des Gebäudes; Rechtsschutz/Mietausfall unzulässig)',
      atLaw: '§ 21 Abs. 1 Z 6 MRG (Feuer-, Haftpflicht- und Leitungswasserschaden; keine Rechtsschutz)',
      chLaw: 'Art. 5 VMWG (Nur gebäudebezogene Sach- und Haftpflichtabgaben)',
      description: 'Rechtsschutzversicherungen des Vermieters und private Mietausfallpolicen sind keine umlagefähigen Betriebskosten.',
      status: 'UNZULAESSIG'
    },
    {
      category: 'Neuanschaffungen & Erstausstattung',
      keywords: [
        'kauf mülltonne', 'anschaffung container', 'neuanlage garten',
        'anschaffung rasenmäher', 'spielplatz neubau', 'rauchmelder kauf',
        'rauchwarnmelder anschaffung'
      ],
      deLaw: 'BGH VIII ZR 346/15 (Erstanschaffung von Einrichtungsgegenständen oder Rauchmeldern ist Vermieteraufwand)',
      atLaw: '§ 3 MRG (Erst- und Neuinvestitionen fallen dem Hauseigentümer zur Last)',
      chLaw: 'Art. 6 VMWG (Neuanschaffungen sind wertvermehrende Investitionen, keine Nebenkosten)',
      description: 'Anschaffungskosten für Mülltonnen, Neuanlagen von Grünflächen oder der Kauf von Rauchmeldern sind nicht umlagefähig.',
      status: 'UNZULAESSIG'
    },
    {
      category: 'Kabelanschluss / TV-Signal (Deutschland ab 01.07.2024)',
      keywords: ['kabelfernsehen', 'kabelanschluss', 'breitbandkabel', 'tv-signal', 'gemeinschaftsantenne'],
      deLaw: 'TKG-Novelle § 2 Nr. 15 BetrKV gestrichen zum 30.06.2024 (Nebenkostenprivileg für TV-Kabel entfallen)',
      atLaw: '§ 21 MRG (Nur bei individueller Vereinbarung)',
      chLaw: 'Art. 257b OR (Nur bei tatsächlicher Bereitstellung und vertraglicher Nennung)',
      description: 'In Deutschland ist die Umlage von Kabelfernsehgebühren über die Nebenkosten seit dem 01.07.2024 gesetzlich unzulässig.',
      status: 'UNZULAESSIG_DE_AB_2024'
    },
    {
      category: 'Hausmeister / Hauswart (Prüfposten)',
      keywords: ['hausmeister', 'hauswart', 'facility management', 'hausbetreuung'],
      deLaw: '§ 2 Nr. 14 BetrKV / BGH VIII ZR 27/07 (Instandhaltungs- und Verwaltungsanteile müssen zwingend herausgerechnet werden)',
      atLaw: '§ 23 MRG (Hausbesorgerarbeiten / Hausbetreuung; keine Erhaltungsarbeiten)',
      chLaw: 'Art. 5 VMWG (Reine Reinigung/Wartung ja; Reparaturarbeiten nein)',
      description: 'Führt der Hausmeister auch Reparaturen durch oder überwacht Handwerker, muss dieser Instandhaltungs- und Verwaltungsanteil (üblicherweise 20–40 %) abgezogen werden.',
      status: 'PRUEFPOSTEN'
    },
    {
      category: 'Sonstige Betriebskosten (Prüfposten)',
      keywords: ['sonstige betriebskosten', 'sonstiges', 'verschiedenes', 'diverses', 'umlage sonstige'],
      deLaw: '§ 2 Nr. 17 BetrKV / BGH VIII ZR 167/03 (Pauschale Sammelposten unzulässig; jede Postenart muss im Mietvertrag konkret benannt sein)',
      atLaw: '§ 21 MRG (Taxativer Katalog; keine freien Sammelposten)',
      chLaw: 'Art. 257a Abs. 2 OR (Nebenkosten müssen detailliert aufgeführt sein)',
      description: 'Sammelbezeichnungen wie "Sonstige Betriebskosten" sind unzulässig. Jede konkrete Position muss einzeln vereinbart sein.',
      status: 'PRUEFPOSTEN'
    }
  ];

  // 2. MIETMINDERUNGSTABELLE
  const DEFECT_CATALOG = {
    heizung_winter_total: {
      title: 'Totalausfall Heizung im Winter (Kälteperiode)',
      typicalRate: 100,
      courtReference: 'LG Berlin GE 1993, 775 (100%); LG Hamburg WuM 1976, 10 (70%)',
      description: 'Vollständiger Ausfall der Heizungsanlage bei winterlichen Minustemperaturen.'
    },
    heizung_uebergang: {
      title: 'Heizungsausfall in der Übergangszeit (unter 18 °C)',
      typicalRate: 30,
      courtReference: 'LG Kassel WuM 1987, 271 (30%); AG Köln WuM 1980, 17 (20%)',
      description: 'Zimmertemperaturen erreichen tagsüber nicht die Mindesttemperatur von 20–22 °C.'
    },
    warmwasser_total: {
      title: 'Totalausfall der Warmwasserversorgung',
      typicalRate: 20,
      courtReference: 'AG München WuM 1986, 272 (15%); LG Berlin GE 1995, 493 (30%)',
      description: 'Kein warmes Wasser in Bad und Küche über mehrere Tage.'
    },
    schimmel_schlafzimmer: {
      title: 'Erheblicher Schimmelbefall im Schlafzimmer / Wohnzimmer',
      typicalRate: 30,
      courtReference: 'LG München I WuM 1985, 26 (30%); LG Berlin GE 2007, 786 (40%)',
      description: 'Gesundheitsgefährdender Schimmelpilzbefall an Außenwänden/Fensterlaibungen.'
    },
    schimmel_bad: {
      title: 'Schimmelbildung im Badezimmer (Fugen / Decke)',
      typicalRate: 15,
      courtReference: 'AG Köln WuM 1992, 23 (10%); AG Dortmund WuM 1985, 261 (15%)',
      description: 'Schimmelbildung trotz regelmäßiger Lüftung durch bauliche Wärmebrücken.'
    },
    baulaerm_massiv: {
      title: 'Massiver Baulärm im selben Haus / Nachbargrundstück',
      typicalRate: 25,
      courtReference: 'BGH VIII ZR 152/12; LG Hamburg ZMR 1987, 422 (25%)',
      description: 'Abbrucharbeiten, Presslufthammer oder Kernsanierung werktags ab 7 Uhr.'
    },
    aufzug_ausfall_og: {
      title: 'Ausfall des Aufzugs (ab 3. OG)',
      typicalRate: 15,
      courtReference: 'LG Bremen WuM 1989, 448 (15%); LG Hamburg WuM 1987, 345 (20%)',
      description: 'Fahrstuhldefekt über Tage/Wochen in oberen Etagen.'
    },
    wasserschaden_decke: {
      title: 'Wasserschaden mit Durchfeuchtung der Zimmerdecke',
      typicalRate: 35,
      courtReference: 'AG Nürnberg WuM 1986, 177 (30%); LG Köln WuM 1996, 265 (50%)',
      description: 'Rohrbruch in Oberwohnung führt zu tropfender Decke und Trocknungsgeräten.'
    },
    ungeziefer: {
      title: 'Ungezieferbefall (Bettwanzen, Schaben, Ratten)',
      typicalRate: 30,
      courtReference: 'LG Berlin GE 2011, 417 (30%); AG Berlin-Tiergarten MM 1988, 22 (50%)',
      description: 'Erheblicher Schädlingsbefall ohne Verschulden des Mieters.'
    },
    undichte_fenster: {
      title: 'Undichte Fenster mit Zugluft und Feuchtigkeit',
      typicalRate: 15,
      courtReference: 'AG Rheine WuM 1984, 131 (15%); LG Berlin GE 1993, 1157 (20%)',
      description: 'Starker Luftzug durch verzogene Fensterrahmen, erhebliche Wärmeverluste.'
    }
  };

  // 3. CO2 STUFENMODELL (§ 5 CO2KostAufG)
  const CO2_STUFENMODELL = [
    [12.0, 0.00, 1.00],
    [17.0, 0.10, 0.90],
    [22.0, 0.20, 0.80],
    [27.0, 0.30, 0.70],
    [32.0, 0.40, 0.60],
    [37.0, 0.50, 0.50],
    [42.0, 0.60, 0.40],
    [47.0, 0.70, 0.30],
    [52.0, 0.80, 0.20],
    [Infinity, 0.95, 0.05]
  ];

  function parseDate(dateStr) {
    if (!dateStr) return new Date();
    if (dateStr instanceof Date) return dateStr;
    const s = String(dateStr).trim();
    if (s.includes('.')) {
      const parts = s.split('.');
      return new Date(parseInt(parts[2], 10), parseInt(parts[1], 10) - 1, parseInt(parts[0], 10));
    }
    return new Date(s);
  }

  function formatDateIso(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // 4. FRISTEN-CHECK
  function checkBillingDeadlines(country = 'DE', billingPeriodEnd, billReceiptDate, additionalClaim = 0) {
    const c = String(country || 'DE').toUpperCase();
    const endDt = parseDate(billingPeriodEnd);
    const receiptDt = parseDate(billReceiptDate);
    const claim = Number(additionalClaim) || 0;

    let landlordDeadline;
    let tenantObjectionDeadline;
    let statutoryRule = '';
    let isTimely = true;
    let isClaimForfeited = false;
    let legalConsequence = '';
    let actionRecommendation = '';

    if (c === 'DE') {
      const dYear = endDt.getFullYear() + 1;
      const dMonth = endDt.getMonth();
      const lastDayOfEndMonth = new Date(dYear, dMonth + 1, 0).getDate();
      landlordDeadline = new Date(dYear, dMonth, lastDayOfEndMonth);

      const objYear = receiptDt.getFullYear() + 1;
      const objMonth = receiptDt.getMonth();
      const lastDayOfObjMonth = new Date(objYear, objMonth + 1, 0).getDate();
      const objDay = Math.min(receiptDt.getDate(), lastDayOfObjMonth);
      tenantObjectionDeadline = new Date(objYear, objMonth, objDay);

      statutoryRule = '§ 556 Abs. 3 BGB (12-Monats-Ausschlussfrist)';
      if (receiptDt > landlordDeadline) {
        isTimely = false;
        if (claim > 0) {
          isClaimForfeited = true;
          legalConsequence = 'Ausschlussfrist verstrichen: Der Vermieter kann eine Nachforderung NICHT mehr verlangen (§ 556 Abs. 3 Satz 3 BGB). Guthaben bleibt bestehen!';
          actionRecommendation = 'Nachforderung unter Hinweis auf § 556 Abs. 3 Satz 3 BGB zurückweisen.';
        } else {
          legalConsequence = 'Verspätet zugegangen. Das Guthaben des Mieters bleibt voll wirksam.';
          actionRecommendation = 'Guthabenauszahlung einfordern.';
        }
      } else {
        isTimely = true;
        legalConsequence = 'Abrechnung ging innerhalb der 12 Monate zu.';
        actionRecommendation = 'Einwendungsfrist von 12 Monaten ab Zugang beachten.';
      }
    } else if (c === 'AT') {
      landlordDeadline = new Date(endDt.getFullYear() + 1, 5, 30); // 30. Juni
      tenantObjectionDeadline = new Date(receiptDt.getFullYear() + 3, receiptDt.getMonth(), receiptDt.getDate());
      statutoryRule = '§ 21 Abs. 3 MRG / § 1486 ABGB';
      if (receiptDt > landlordDeadline) {
        isTimely = false;
        legalConsequence = 'Gesetzlicher Stichtag (30. Juni des Folgejahres) wurde überschritten.';
        actionRecommendation = 'Antrag bei Schlichtungsstelle oder Bezirksgericht nach § 37 MRG prüfen.';
      } else {
        isTimely = true;
        legalConsequence = 'Abrechnung fristgerecht nach § 21 Abs. 3 MRG.';
        actionRecommendation = 'Belegeinsicht verlangen.';
      }
    } else {
      landlordDeadline = new Date(endDt.getFullYear() + 5, endDt.getMonth(), endDt.getDate());
      tenantObjectionDeadline = new Date(receiptDt.getFullYear() + 1, receiptDt.getMonth(), receiptDt.getDate());
      statutoryRule = 'Art. 257b OR i.V.m. Art. 128 OR (5 Jahre Verjährung)';
      if (receiptDt > landlordDeadline) {
        isTimely = false;
        isClaimForfeited = true;
        legalConsequence = 'Die Forderung ist nach Art. 128 OR verjährt.';
        actionRecommendation = 'Einrede der Verjährung erheben.';
      } else {
        isTimely = true;
        legalConsequence = 'Forderung ist unverjährt.';
        actionRecommendation = 'Belegeinsicht verlangen (Art. 257b Abs. 2 OR).';
      }
    }

    return {
      country: c,
      billingPeriodEnd: formatDateIso(endDt),
      billReceiptDate: formatDateIso(receiptDt),
      additionalClaim: Number(claim.toFixed(2)),
      isClaimForfeited,
      isTimely,
      landlordDeadline: formatDateIso(landlordDeadline),
      tenantObjectionDeadline: formatDateIso(tenantObjectionDeadline),
      statutoryRule,
      legalConsequence,
      actionRecommendation
    };
  }

  // 5. POSTEN-KLASSIFIZIERUNG
  function classifyLineItem(name = '', amount = 0, country = 'DE') {
    const c = String(country || 'DE').toUpperCase();
    const cleanName = String(name).trim();
    const lower = cleanName.toLowerCase();
    const amt = Number(Number(amount || 0).toFixed(2));

    for (const rule of NON_ALLOCATABLE_RULES) {
      for (const kw of rule.keywords) {
        if (lower.includes(kw)) {
          if (rule.status === 'UNZULAESSIG_DE_AB_2024' && c !== 'DE') {
            continue;
          }
          const law = c === 'DE' ? rule.deLaw : c === 'AT' ? rule.atLaw : rule.chLaw;
          const isInvalid = rule.status === 'UNZULAESSIG' || rule.status === 'UNZULAESSIG_DE_AB_2024';
          let recommendedDeduction = amt;
          if (rule.status === 'PRUEFPOSTEN') {
            recommendedDeduction = rule.category.toLowerCase().includes('hausmeister')
              ? Number((amt * 0.25).toFixed(2))
              : amt;
          }

          return {
            itemName: cleanName,
            claimedAmount: amt,
            status: rule.status,
            isAllocatable: !isInvalid,
            category: rule.category,
            matchedKeyword: kw,
            statutorySource: law,
            reason: rule.description,
            recommendedDeduction
          };
        }
      }
    }

    return {
      itemName: cleanName,
      claimedAmount: amt,
      status: 'ZULAESSIG_GRUNDKATEGORIE',
      isAllocatable: true,
      category: 'Reguläre Betriebskosten',
      matchedKeyword: null,
      statutorySource: c === 'DE' ? '§ 2 BetrKV' : c === 'AT' ? '§ 21 MRG' : 'Art. 257b OR',
      reason: 'Entspricht dem Grunde nach einer zulässigen Betriebskostenart. Verteilerschlüssel und Belegeinsicht prüfen.',
      recommendedDeduction: 0
    };
  }

  // 6. HEIZUNG & CO2
  function checkHeatingAndCo2({
    heatingShareAmount = 0,
    isConsumptionMetered = true,
    co2KgPerSqmYear = null,
    totalCo2Costs = 0
  } = {}) {
    const amt = Number(Number(heatingShareAmount || 0).toFixed(2));
    const has15Pct = !isConsumptionMetered;
    const heatingRed = has15Pct ? Number((amt * 0.15).toFixed(2)) : 0;

    let lPct = 0;
    let tPct = 100;
    let lAmt = 0;
    let tAmt = Number(Number(totalCo2Costs || 0).toFixed(2));

    if (co2KgPerSqmYear !== null && co2KgPerSqmYear !== undefined) {
      const kg = Number(co2KgPerSqmYear);
      for (const [limit, lShare, tShare] of CO2_STUFENMODELL) {
        if (kg <= limit) {
          lPct = Number((lShare * 100).toFixed(1));
          tPct = Number((tShare * 100).toFixed(1));
          lAmt = Number((totalCo2Costs * lShare).toFixed(2));
          tAmt = Number((totalCo2Costs * tShare).toFixed(2));
          break;
        }
      }
    }

    return {
      heatingShareAmount: amt,
      isConsumptionMetered,
      has15PercentReductionRight: has15Pct,
      heatingReductionAmount: heatingRed,
      legalSource15Percent: '§ 12 Abs. 1 HeizkostenV (15% Kürzungsrecht bei fehlender verbrauchsabhängiger Abrechnung)',
      co2Evaluation: {
        co2KgPerSqmYear,
        totalCo2Costs: Number(Number(totalCo2Costs || 0).toFixed(2)),
        landlordSharePercentage: lPct,
        tenantSharePercentage: tPct,
        landlordDeductionAmount: lAmt,
        tenantRemainingAmount: tAmt,
        legalSourceCo2: '§§ 5–7 CO2KostAufG (10-Stufen-Modell)'
      },
      totalHeatingDeduction: Number((heatingRed + lAmt).toFixed(2))
    };
  }

  // 7. MIETMINDERUNG
  function calculateRentReduction({
    country = 'DE',
    monthlyWarmRent = 1000,
    defectKey = 'heizung_winter_total',
    defectDays = 10,
    daysInMonth = 30,
    customReductionRate = null
  } = {}) {
    const c = String(country || 'DE').toUpperCase();
    const warmRent = Number(monthlyWarmRent) || 0;
    const defectInfo = DEFECT_CATALOG[defectKey] || {
      title: defectKey,
      typicalRate: 20,
      courtReference: 'Einzelfallbeurteilung'
    };

    const rate = customReductionRate !== null && customReductionRate !== undefined
      ? Math.max(0, Math.min(100, Number(customReductionRate)))
      : defectInfo.typicalRate;

    const monthlyReduction = warmRent * (rate / 100);
    const effDays = Math.max(1, Math.min(daysInMonth, Number(defectDays) || 1));
    const dailyReduction = monthlyReduction / Math.max(1, daysInMonth);
    const totalReductionAmount = Number((dailyReduction * effDays).toFixed(2));

    const statutoryLaw =
      c === 'DE' ? '§ 536 BGB i.V.m. BGH VIII ZR 347/04 (Basis: Bruttowarmmiete)' :
      c === 'AT' ? '§ 1096 ABGB (Zinsbefreiung / Zinsminderung auf Bruttomiete)' :
      'Art. 259d OR (Verhältnismässige Herabsetzung)';

    return {
      country: c,
      monthlyWarmRent: Number(warmRent.toFixed(2)),
      defectKey,
      defectTitle: defectInfo.title,
      courtReference: defectInfo.courtReference,
      reductionRatePercent: rate,
      defectDays: effDays,
      daysInMonth,
      totalReductionAmount,
      dailyReductionAmount: Number(dailyReduction.toFixed(2)),
      statutoryLaw
    };
  }

  // 8. GESAMT-AUDIT
  function auditOperatingCostBill({
    country = 'DE',
    billingPeriodStart = '2024-01-01',
    billingPeriodEnd = '2024-12-31',
    billReceiptDate = '2025-10-15',
    claimedTotalCost = 1250,
    prepaidAmount = 1000,
    items = [],
    heatingShareAmount = 0,
    heatingConsumptionMetered = true,
    co2KgPerSqm = null,
    totalCo2Costs = 0,
    monthlyWarmRent = 0,
    rentReductionClaims = []
  } = {}) {
    const c = String(country || 'DE').toUpperCase();
    const origBalance = Number((claimedTotalCost - prepaidAmount).toFixed(2));
    const deadlineRes = checkBillingDeadlines(c, billingPeriodEnd, billReceiptDate, origBalance);

    let totalInvalidDeductions = 0;
    const itemAudits = (items || []).map(it => {
      const classified = classifyLineItem(it.name, it.amount, c);
      if (classified.status === 'UNZULAESSIG' || classified.status === 'UNZULAESSIG_DE_AB_2024') {
        totalInvalidDeductions += classified.recommendedDeduction;
      } else if (classified.status === 'PRUEFPOSTEN' && it.forceDeduct) {
        totalInvalidDeductions += classified.recommendedDeduction;
      }
      return classified;
    });

    const heatRes = checkHeatingAndCo2({
      heatingShareAmount,
      isConsumptionMetered: heatingConsumptionMetered,
      co2KgPerSqmYear: co2KgPerSqm,
      totalCo2Costs
    });

    let totalRentReductions = 0;
    const rentRedAudits = (rentReductionClaims || []).map(claim => {
      const red = calculateRentReduction({
        country: c,
        monthlyWarmRent,
        defectKey: claim.defectKey,
        defectDays: claim.defectDays,
        customReductionRate: claim.customRate
      });
      totalRentReductions += red.totalReductionAmount;
      return red;
    });

    const totalSavings = Number((totalInvalidDeductions + heatRes.totalHeatingDeduction + totalRentReductions).toFixed(2));
    let correctedBalance;
    let totalSavingsRealized;

    if (deadlineRes.isClaimForfeited) {
      correctedBalance = Number(Math.min(0, origBalance - totalSavings).toFixed(2));
      totalSavingsRealized = origBalance > 0 ? origBalance : totalSavings;
    } else {
      correctedBalance = Number((origBalance - totalSavings).toFixed(2));
      totalSavingsRealized = totalSavings;
    }

    const currency = c === 'CH' ? 'CHF' : 'EUR';

    return {
      country: c,
      currency,
      inputSummary: {
        billingPeriod: `${billingPeriodStart} bis ${billingPeriodEnd}`,
        receiptDate: billReceiptDate,
        claimedTotalCost: Number(Number(claimedTotalCost).toFixed(2)),
        prepaidAmount: Number(Number(prepaidAmount).toFixed(2)),
        originalClaimedBalance: origBalance
      },
      deadlineEvaluation: deadlineRes,
      itemAudits,
      invalidItemsTotalDeduction: Number(totalInvalidDeductions.toFixed(2)),
      heatingEvaluation: heatRes,
      heatingDeduction: heatRes.totalHeatingDeduction,
      rentReductionAudits: rentRedAudits,
      rentReductionTotal: Number(totalRentReductions.toFixed(2)),
      finalFinancialSummary: {
        originalClaimedBalance: origBalance,
        totalSavingsIdentified: Number(totalSavingsRealized.toFixed(2)),
        correctedFinalBalance: correctedBalance,
        resultVerdict: correctedBalance < 0
          ? `GUTHABEN von ${Math.abs(correctedBalance).toFixed(2)} ${currency}`
          : correctedBalance > 0
          ? `NACHZAHLUNG von ${correctedBalance.toFixed(2)} ${currency}`
          : `AUSGEGLICHEN (0.00 ${currency})`
      },
      liveWebTool: 'https://dach-digitalwerk.netlify.app/nebenkosten-check/'
    };
  }

  // 9. SELBSTTEST-ROUTINE
  function runSelfTests() {
    console.log('='.repeat(68));
    console.log('🧪 JS SELBSTTEST: DACH NEBENKOSTEN- & MIETMINDERUNGS-PRÜFER');
    console.log('='.repeat(68));

    // Test 1: Frist DE
    const d1 = checkBillingDeadlines('DE', '2024-12-31', '2025-10-01', 300);
    if (!d1.isTimely || d1.isClaimForfeited) throw new Error('Test 1a failed');
    const d2 = checkBillingDeadlines('DE', '2024-12-31', '2026-01-10', 300);
    if (d2.isTimely || !d2.isClaimForfeited) throw new Error('Test 1b failed');
    console.log('  ✅ Test 1 bestanden: 12-Monats-Frist § 556 Abs. 3 BGB');

    // Test 2: Unzulässige Posten
    const it1 = classifyLineItem('Hausverwaltung Jahresgebühr', 200, 'DE');
    if (it1.isAllocatable || it1.status !== 'UNZULAESSIG') throw new Error('Test 2a failed');
    const it2 = classifyLineItem('Kabelfernsehen', 120, 'DE');
    if (it2.isAllocatable) throw new Error('Test 2b failed');
    console.log('  ✅ Test 2 bestanden: Posten-Klassifizierung & Blacklist');

    // Test 3: Heizung 15%
    const h1 = checkHeatingAndCo2({ heatingShareAmount: 1000, isConsumptionMetered: false });
    if (!h1.has15PercentReductionRight || h1.heatingReductionAmount !== 150) throw new Error('Test 3 failed');
    console.log('  ✅ Test 3 bestanden: § 12 HeizkostenV (15% Kürzungsrecht)');

    // Test 4: Mietminderung
    const r1 = calculateRentReduction({ country: 'DE', monthlyWarmRent: 1200, defectKey: 'heizung_winter_total', defectDays: 10 });
    if (Math.abs(r1.totalReductionAmount - 400) > 0.05) throw new Error('Test 4 failed');
    console.log('  ✅ Test 4 bestanden: Mietminderung nach BGH auf Warmmiete');

    // Test 5: Gesamt-Audit
    const aud = auditOperatingCostBill({
      country: 'DE',
      billingPeriodStart: '2024-01-01',
      billingPeriodEnd: '2024-12-31',
      billReceiptDate: '2025-10-10',
      claimedTotalCost: 900,
      prepaidAmount: 600,
      items: [
        { name: 'Grundsteuer', amount: 150 },
        { name: 'Hausverwaltung', amount: 300 }
      ]
    });
    // Claimed balance: 300. Invalid: 300 -> corrected: 0
    if (aud.finalFinancialSummary.correctedFinalBalance !== 0) throw new Error('Test 5 failed: ' + aud.finalFinancialSummary.correctedFinalBalance);
    console.log('  ✅ Test 5 bestanden: Gesamt-Audit');

    console.log('-'.repeat(68));
    console.log('🎉 ALLE JS TESTS ERFOLGREICH BESTANDEN!');
    console.log('='.repeat(68));
    return true;
  }

  const exportObj = {
    NON_ALLOCATABLE_RULES,
    DEFECT_CATALOG,
    CO2_STUFENMODELL,
    parseDate,
    checkBillingDeadlines,
    classifyLineItem,
    checkHeatingAndCo2,
    calculateRentReduction,
    auditOperatingCostBill,
    runSelfTests
  };

  if (typeof process !== 'undefined' && process.argv && require.main === module) {
    if (process.argv.includes('--test')) {
      runSelfTests();
    } else {
      const sample = auditOperatingCostBill({
        country: 'DE',
        items: [
          { name: 'Hausverwaltung', amount: 240 },
          { name: 'Heizungsreparatur', amount: 180 },
          { name: 'Müllabfuhr', amount: 150 }
        ]
      });
      console.log(JSON.stringify(sample, null, 2));
    }
  }

  return exportObj;
});
