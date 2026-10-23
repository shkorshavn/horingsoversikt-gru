/* Høringer – Gjøvikregionen
   Leser data/horinger.json og data/status.json, filtrerer, sorterer og viser høringene.
   data/arkiv.json (utløpte høringer) hentes først når brukeren vil se dem.
   Ingen eksterne avhengigheter. Datoer og «dager igjen» regnes i norsk tid. */
(function () {
  "use strict";

  var MANEDER = ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august",
    "september", "oktober", "november", "desember"];
  var KORTE_MANEDER = ["jan.", "feb.", "mars", "apr.", "mai", "juni", "juli", "aug.",
    "sep.", "okt.", "nov.", "des."];
  var STANDARD_PRIO = ["1", "2"];
  var ARKIV_DAGER = 30;      // utløpte høringer vises så lenge
  var UTDATERT_DAGER = 10;   // advarsel når oversikten er eldre enn dette

  var tilstand = { horinger: [], arkiv: null, arkivFeilet: false, status: null, iDag: null };

  // ---------- Datoer ----------

  /** Dagens dato i norsk tid som "ÅÅÅÅ-MM-DD". Testene kan overstyre med window.HORINGER_I_DAG. */
  function dagensDato() {
    if (window.HORINGER_I_DAG) return window.HORINGER_I_DAG;
    return new Intl.DateTimeFormat("en-CA", {
      timeZone: "Europe/Oslo", year: "numeric", month: "2-digit", day: "2-digit"
    }).format(new Date());
  }

  function deler(iso) {
    var d = String(iso).slice(0, 10).split("-");
    return { ar: +d[0], maned: +d[1], dag: +d[2] };
  }

  /** Antall hele dager fra «fra» til «til» (begge ÅÅÅÅ-MM-DD). */
  function dagerMellom(fra, til) {
    var a = deler(fra), b = deler(til);
    return Math.round((Date.UTC(b.ar, b.maned - 1, b.dag) - Date.UTC(a.ar, a.maned - 1, a.dag)) / 864e5);
  }

  function norskDato(iso) {
    var d = deler(iso);
    return d.dag + ". " + MANEDER[d.maned - 1] + " " + d.ar;
  }

  /** Tidspunkt fra ISO med tidssone, vist i norsk tid: «16. oktober 2026 kl. 17.14». */
  function norskTidspunkt(iso) {
    var t = new Date(iso);
    if (isNaN(t)) return "";
    var p = {};
    new Intl.DateTimeFormat("en-GB", {
      timeZone: "Europe/Oslo", year: "numeric", month: "numeric", day: "numeric",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23"
    }).formatToParts(t).forEach(function (x) { p[x.type] = x.value; });
    return +p.day + ". " + MANEDER[+p.month - 1] + " " + p.year + " kl. " + p.hour + "." + p.minute;
  }

  /** Datoen (ÅÅÅÅ-MM-DD) et tidspunkt med tidssone faller på i norsk tid. */
  function osloDato(iso) {
    var t = new Date(iso);
    if (isNaN(t)) return null;
    return new Intl.DateTimeFormat("en-CA", {
      timeZone: "Europe/Oslo", year: "numeric", month: "2-digit", day: "2-digit"
    }).format(t);
  }

  /** Fristklasse etter antall dager igjen: under 14, 14–30, over 30. */
  function fristklasse(dager) {
    if (dager === null) return "ukjent";
    if (dager < 0) return "utlopt";
    if (dager < 14) return "snart";
    if (dager <= 30) return "middels";
    return "godtid";
  }

  function dagerTekst(dager) {
    if (dager === null) return "Frist ikke oppgitt";
    if (dager < 0) return "Fristen er ute";
    if (dager === 0) return "Frist i dag";
    if (dager === 1) return "1 dag igjen";
    return dager + " dager igjen";
  }

  // ---------- Filtre og adresse ----------

  function skjema() { return document.getElementById("filterskjema"); }

  function lesFiltre() {
    var f = skjema();
    var prio = Array.prototype.filter.call(f.querySelectorAll('input[name="prio"]'), function (x) {
      return x.checked;
    }).map(function (x) { return x.value; });
    return {
      q: f.q.value.trim(),
      kategori: f.kategori.value,
      niva: f.niva.value,
      prio: prio,
      utlopte: f.utlopte.checked
    };
  }

  function settFiltre(v) {
    var f = skjema();
    f.q.value = v.q || "";
    f.kategori.value = v.kategori || "";
    f.niva.value = v.niva || "";
    Array.prototype.forEach.call(f.querySelectorAll('input[name="prio"]'), function (x) {
      x.checked = v.prio.indexOf(x.value) !== -1;
    });
    f.utlopte.checked = !!v.utlopte;
  }

  function filtreFraAdresse() {
    var s = new URLSearchParams(window.location.search);
    return {
      q: s.get("q") || "",
      kategori: s.get("kategori") || "",
      niva: s.get("niva") || "",
      prio: s.has("prio") ? s.get("prio").split(",").filter(Boolean) : STANDARD_PRIO.slice(),
      utlopte: s.get("utlopte") === "1"
    };
  }

  function skrivAdresse(v) {
    var s = new URLSearchParams();
    if (v.q) s.set("q", v.q);
    if (v.kategori) s.set("kategori", v.kategori);
    if (v.niva) s.set("niva", v.niva);
    if (v.prio.join(",") !== STANDARD_PRIO.join(",")) s.set("prio", v.prio.join(","));
    if (v.utlopte) s.set("utlopte", "1");
    var q = s.toString();
    history.replaceState(null, "", window.location.pathname + (q ? "?" + q : ""));
  }

  function normaliser(t) { return String(t || "").toLocaleLowerCase("nb"); }

  function passer(h, v) {
    if (v.kategori && h.kategori !== v.kategori) return false;
    if (v.niva && h.niva !== v.niva) return false;
    if (v.prio.indexOf(String(h.prioritet)) === -1) return false;
    if (h.dager !== null && h.dager < 0 && (!v.utlopte || h.dager < -ARKIV_DAGER)) return false;
    if (v.q) {
      var tekst = normaliser([h.tittel, h.instans, h.ingress, h.kilde, h.frist_tekst, h.kategori].join(" "));
      var ord = normaliser(v.q).split(/\s+/);
      for (var i = 0; i < ord.length; i++) if (tekst.indexOf(ord[i]) === -1) return false;
    }
    return true;
  }

  function sorter(a, b) {
    if (a.frist === null && b.frist !== null) return 1;
    if (b.frist === null && a.frist !== null) return -1;
    if (a.frist !== b.frist) return a.frist < b.frist ? -1 : 1;
    return a.tittel.localeCompare(b.tittel, "nb");
  }

  // ---------- Tegning ----------

  function el(navn, attr, barn) {
    var e = document.createElement(navn);
    if (attr) Object.keys(attr).forEach(function (k) {
      if (k === "tekst") e.textContent = attr[k];
      else if (k === "klasse") e.className = attr[k];
      else e.setAttribute(k, attr[k]);
    });
    (barn || []).forEach(function (b) { if (b) e.appendChild(b); });
    return e;
  }

  function fristblokk(h) {
    var klasse = fristklasse(h.dager);
    var blokk = el("div", { klasse: "frist " + klasse });
    if (h.frist) {
      var d = deler(h.frist);
      var arTekst = d.ar !== deler(tilstand.iDag).ar ? " " + d.ar : "";
      blokk.appendChild(el("span", { klasse: "skjult", tekst: "Frist " + norskDato(h.frist) + ". " }));
      blokk.appendChild(el("span", { klasse: "dag", "aria-hidden": "true", tekst: String(d.dag) }));
      blokk.appendChild(el("span", { klasse: "maned", "aria-hidden": "true", tekst: KORTE_MANEDER[d.maned - 1] + arTekst }));
    }
    blokk.appendChild(el("span", { klasse: "igjen", tekst: dagerTekst(h.dager) }));
    return blokk;
  }

  function hoeringsrad(h) {
    // Bare vanlige nettadresser blir lenker (beskytter mot f.eks. «javascript:» i dataene).
    var trygg = /^https?:\/\//i.test(String(h.lenke || ""));
    var tittel = el("h2", null, [
      trygg ? el("a", { href: h.lenke, tekst: h.tittel }) : el("span", { tekst: h.tittel }),
      h.ny ? document.createTextNode(" ") : null,
      h.ny ? el("span", { klasse: "ny-merke", tekst: "Ny" }) : null
    ]);
    var detaljer = el("p", { klasse: "detaljer" }, [
      h.kategori ? el("span", { klasse: "tema", tekst: h.kategori }) : null,
      h.frist_tekst ? el("span", { tekst: h.frist_tekst }) : null,
      h.kilde && String(h.instans).indexOf(h.kilde) !== 0 ? el("span", { tekst: "Kilde: " + h.kilde }) : null
    ]);
    var innhold = el("div", { klasse: "innhold" }, [
      tittel,
      el("p", { klasse: "instans", tekst: h.instans }),
      h.ingress ? el("p", { klasse: "beskrivelse", tekst: h.ingress }) : null,
      detaljer
    ]);
    return el("li", { klasse: "hoering", "data-id": h.id, "data-frist": h.frist || "" }, [fristblokk(h), innhold]);
  }

  function synlige() {
    var v = lesFiltre();
    return tilstand.horinger.filter(function (h) { return passer(h, v); }).sort(sorter);
  }

  function tegn() {
    var v = lesFiltre();
    skrivAdresse(v);
    var liste = document.getElementById("liste");
    var utvalg = synlige();
    liste.textContent = "";
    utvalg.forEach(function (h) { liste.appendChild(hoeringsrad(h)); });

    var apne = tilstand.horinger.filter(erApen).length;
    var nye = tilstand.horinger.filter(function (h) { return erApen(h) && h.ny; }).length;
    var antall = document.getElementById("antall");
    antall.textContent = utvalg.length === 1
      ? "Viser 1 høring"
      : "Viser " + utvalg.length + " høringer";
    antall.textContent += " (" + apne + " åpne totalt" + (nye ? ", " + nye + (nye === 1 ? " ny" : " nye") + " siste uke" : "") + ")";
    if (v.utlopte && tilstand.arkivFeilet) antall.textContent += ". Høringer med utløpt frist kunne ikke hentes.";
    document.getElementById("tom").hidden = utvalg.length > 0;
    document.getElementById("eksport").disabled = utvalg.length === 0;
  }

  function erApen(h) { return h.dager === null || h.dager >= 0; }

  function fyllValg(id, verdier) {
    var s = document.getElementById(id);
    verdier.forEach(function (v) { s.appendChild(el("option", { value: v, tekst: v })); });
  }

  function unike(felt) {
    var sett = {};
    tilstand.horinger.forEach(function (h) { if (h[felt]) sett[h[felt]] = true; });
    return Object.keys(sett).sort(function (a, b) { return a.localeCompare(b, "nb"); });
  }

  /** Gjør tekniske feilmeldinger om til en kort forklaring. */
  function feilforklaring(feil) {
    var f = String(feil || "");
    var kode = f.match(/\b(4\d\d|5\d\d)\b/);
    if (/SperretAvRobots|sperret i robots/i.test(f)) return "Nettstedet tillater ikke automatisk innhenting av denne siden.";
    if (/timeout|timed out|tidsavbrudd/i.test(f)) return "Nettstedet svarte ikke i tide.";
    if (/connection|resolve|ssl|unreachable/i.test(f)) return "Fikk ikke kontakt med nettstedet.";
    if (kode && kode[1] === "403") return "Nettstedet avviste innhentingen (feilkode 403).";
    if (kode) return "Nettstedet svarte med en feil (feilkode " + kode[1] + ").";
    return "Innhentingen feilet.";
  }

  /** Statuscellen for én kilde: merke og en kort forklaring. */
  function statusCelle(k) {
    var celle = el("td");
    var tekst = null, merke;
    if (k.status === "ok") merke = el("span", { klasse: "merke ok", tekst: "Hentet" });
    else if (k.status === "ikke hentet") {
      merke = el("span", { klasse: "merke venter", tekst: "Ikke hentet ennå" });
    } else if (k.status === "utdatert") {
      merke = el("span", { klasse: "merke utdatert", tekst: "Utdatert" });
      tekst = "Ikke hentet på mer enn en uke. Høringene kan være utdaterte.";
    } else {
      merke = el("span", { klasse: "merke feil", tekst: "Feil" });
      tekst = feilforklaring(k.feil) + (k.sist_ok
        ? " Viser høringene fra " + norskTidspunkt(k.sist_ok) + "."
        : " Høringene herfra mangler i listen.");
    }
    celle.appendChild(merke);
    if (tekst) celle.appendChild(el("span", { klasse: "feiltekst", tekst: tekst }));
    // På smal skjerm skjules kolonnen «Sist hentet», og tidspunktet vises her i stedet.
    if (k.sist_ok) celle.appendChild(el("span", { klasse: "statustekst bare-smal", tekst: "Sist hentet " + norskTidspunkt(k.sist_ok) }));
    if (k.kjoring === "pc" && k.status !== "ok") {
      celle.appendChild(el("span", { klasse: "statustekst", tekst: "Hentes fra en PC hos Gjøvikregionen Utvikling, som må være på." }));
    }
    return celle;
  }

  function tegnStatus(status) {
    var tbody = document.querySelector("#status-tabell tbody");
    var inaktiveListe = document.getElementById("inaktive-liste");
    tbody.textContent = "";
    inaktiveListe.textContent = "";
    var kilder = (status && status.kilder) || [];
    var aktive = kilder.filter(function (k) { return k.status !== "ikke overvåket"; });
    var inaktive = kilder.filter(function (k) { return k.status === "ikke overvåket"; });
    var feil = aktive.filter(function (k) { return k.status === "feil" || k.status === "utdatert"; }).length;

    aktive.forEach(function (k) {
      var harData = k.status === "ok" || !!k.sist_ok;
      var apne = tilstand.horinger.filter(function (h) { return h.kilde === k.kilde && erApen(h); }).length;
      tbody.appendChild(el("tr", null, [
        el("th", { scope: "row", tekst: k.kilde }),
        statusCelle(k),
        el("td", { klasse: "kol-tid", tekst: k.sist_ok ? norskTidspunkt(k.sist_ok) : "–" }),
        el("td", { klasse: "tall", tekst: harData ? String(apne) : "–" })
      ]));
    });
    inaktive.forEach(function (k) { inaktiveListe.appendChild(el("li", { tekst: k.kilde })); });
    document.getElementById("antall-inaktive").textContent = String(inaktive.length);
    document.getElementById("inaktive").hidden = inaktive.length === 0;

    var ingress = aktive.length + " kilder overvåkes automatisk.";
    if (feil) ingress += " " + feil + (feil === 1 ? " kilde" : " kilder") + " kunne ikke hentes ved siste oppdatering. Se forklaringen i tabellen.";
    if (status && status.generert) ingress += " Sist oppdatert " + norskTidspunkt(status.generert) + ".";
    document.getElementById("status-ingress").textContent = ingress;
  }

  /** Advarsel øverst når oversikten ikke er oppdatert på lenge. */
  function sjekkAlder(generert) {
    var boks = document.getElementById("advarsel");
    var dato = generert ? osloDato(generert) : null;
    var alder = dato ? dagerMellom(dato, tilstand.iDag) : null;
    boks.hidden = !(alder !== null && alder > UTDATERT_DAGER);
    if (!boks.hidden) {
      boks.textContent = "Oversikten er ikke oppdatert på " + alder + " dager. Nye høringer kan mangle, og frister kan være endret.";
    }
  }

  // ---------- CSV ----------

  function csvFelt(v) {
    var s = v === null || v === undefined ? "" : String(v);
    return /[";\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }

  function lagCsv(utvalg) {
    var rader = [["Frist", "Dager igjen", "Høringsinstans", "Tittel", "Tema", "Avsender", "Prioritet", "Frist slik kilden skriver den", "Lenke"]];
    utvalg.forEach(function (h) {
      rader.push([h.frist ? norskDato(h.frist) : "", h.dager === null ? "" : h.dager, h.instans,
        h.tittel, h.kategori, h.niva, h.prioritet, h.frist_tekst, h.lenke]);
    });
    return "﻿" + rader.map(function (r) { return r.map(csvFelt).join(";"); }).join("\r\n") + "\r\n";
  }

  function lastNedCsv() {
    var innhold = lagCsv(synlige());
    var blob = new Blob([innhold], { type: "text/csv;charset=utf-8" });
    var a = el("a", { href: URL.createObjectURL(blob), download: "horinger-gjovikregionen-" + tilstand.iDag + ".csv" });
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }

  // ---------- Oppstart ----------

  function visFeil(tekst) {
    var f = document.getElementById("feil");
    f.textContent = "";
    f.appendChild(el("p", { tekst: tekst }));
    f.hidden = false;
  }

  function hentJson(sti) {
    return fetch(sti, { cache: "no-cache" }).then(function (svar) {
      if (!svar.ok) throw new Error(sti + " svarte " + svar.status);
      return svar.json();
    });
  }

  function medDager(h) {
    h.frist = h.frist ? String(h.frist).slice(0, 10) : null;
    h.dager = h.frist ? dagerMellom(tilstand.iDag, h.frist) : null;
    return h;
  }

  /** Henter arkivet med utløpte høringer første gang de skal vises. */
  function hentArkiv() {
    if (tilstand.arkiv !== null || tilstand.arkivFeilet) return Promise.resolve();
    return hentJson("data/arkiv.json").then(function (data) {
      var finnes = {};
      tilstand.horinger.forEach(function (h) { finnes[h.id] = true; });
      tilstand.arkiv = (data.horinger || []).map(medDager).filter(function (h) {
        return !finnes[h.id] && h.dager !== null && h.dager < 0 && h.dager >= -ARKIV_DAGER;
      });
      tilstand.horinger = tilstand.horinger.concat(tilstand.arkiv);
    }).catch(function () { tilstand.arkivFeilet = true; }).then(function () {
      document.documentElement.setAttribute("data-arkiv", tilstand.arkivFeilet ? "feil" : "1");
    });
  }

  function oppdater() {
    if (lesFiltre().utlopte && tilstand.arkiv === null && !tilstand.arkivFeilet) {
      tegn();
      hentArkiv().then(tegn);
    } else {
      tegn();
    }
  }

  function nullstill() {
    settFiltre({ q: "", kategori: "", niva: "", prio: STANDARD_PRIO.slice(), utlopte: false });
    tegn();
    document.getElementById("sok").focus();
  }

  function start() {
    tilstand.iDag = dagensDato();
    var f = skjema();
    f.addEventListener("input", oppdater);
    f.addEventListener("change", oppdater);
    f.addEventListener("submit", function (e) { e.preventDefault(); });
    document.getElementById("nullstill").addEventListener("click", nullstill);
    document.getElementById("nullstill-tom").addEventListener("click", nullstill);
    document.getElementById("eksport").addEventListener("click", lastNedCsv);
    // Filtrene kan foldes sammen bare på smal skjerm. På bred skjerm står de alltid åpne.
    var smal = window.matchMedia("(max-width: 52rem)");
    var boks = document.getElementById("filtre-boks");
    if (smal.matches) boks.open = false;
    boks.querySelector("summary").addEventListener("click", function (e) {
      if (!smal.matches) e.preventDefault();
    });
    smal.addEventListener("change", function () { if (!smal.matches) boks.open = true; });

    Promise.allSettled([hentJson("data/horinger.json"), hentJson("data/status.json")]).then(function (svar) {
      var oppdatert = document.getElementById("oppdatert");
      if (svar[0].status !== "fulfilled") {
        oppdatert.textContent = "";
        visFeil("Klarte ikke å hente høringene. Last siden på nytt om litt. Vedvarer feilen, si fra til Gjøvikregionen Utvikling.");
        document.getElementById("eksport").disabled = true;
        document.getElementById("antall").textContent = "";
      } else {
        var data = svar[0].value;
        tilstand.horinger = (data.horinger || []).map(medDager);
        oppdatert.textContent = data.generert ? "Oppdatert " + norskTidspunkt(data.generert) + "." : "";
        sjekkAlder(data.generert);
        fyllValg("kategori", unike("kategori"));
        fyllValg("niva", unike("niva"));
        settFiltre(filtreFraAdresse());
      }
      var utlopte = svar[0].status === "fulfilled" && lesFiltre().utlopte;
      return (utlopte ? hentArkiv() : Promise.resolve()).then(function () { return svar; });
    }).then(function (svar) {
      if (svar[0].status === "fulfilled") tegn();
      if (svar[1].status === "fulfilled") {
        tegnStatus(svar[1].value);
      } else {
        document.getElementById("status-ingress").textContent = "Status for kildene er ikke tilgjengelig.";
        document.getElementById("status-tabell").hidden = true;
        document.getElementById("inaktive").hidden = true;
      }
      document.documentElement.setAttribute("data-klar", "1");
    });
  }

  // Gjøres tilgjengelig for testene.
  window.Horinger = { feilforklaring: feilforklaring, fristklasse: fristklasse, dagerMellom: dagerMellom, lagCsv: lagCsv, norskDato: norskDato };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
