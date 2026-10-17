/* Høringer – Gjøvikregionen
   Leser data/horinger.json og data/status.json, filtrerer, sorterer og viser høringene.
   Ingen eksterne avhengigheter. Datoer og «dager igjen» regnes i norsk tid. */
(function () {
  "use strict";

  var MANEDER = ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august",
    "september", "oktober", "november", "desember"];
  var KORTE_MANEDER = ["jan.", "feb.", "mars", "apr.", "mai", "juni", "juli", "aug.",
    "sep.", "okt.", "nov.", "des."];
  var STANDARD_PRIO = ["1", "2"];

  var tilstand = { horinger: [], status: null, iDag: null };

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
    return p.day + ". " + MANEDER[+p.month - 1] + " " + p.year + " kl. " + p.hour + "." + p.minute;
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
    if (!v.utlopte && h.dager !== null && h.dager < 0) return false;
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
    var tittel = el("h2", null, [el("a", { href: h.lenke, tekst: h.tittel })]);
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

    var apne = tilstand.horinger.filter(function (h) { return h.dager === null || h.dager >= 0; }).length;
    var antall = document.getElementById("antall");
    antall.textContent = utvalg.length === 1
      ? "Viser 1 høring"
      : "Viser " + utvalg.length + " høringer";
    antall.textContent += " (" + apne + " åpne totalt)";
    document.getElementById("tom").hidden = utvalg.length > 0;
    document.getElementById("eksport").disabled = utvalg.length === 0;
  }

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
    if (/robots/i.test(f)) return "Nettstedet tillater ikke automatisk innhenting av denne siden.";
    if (/timeout|timed out|tidsavbrudd/i.test(f)) return "Nettstedet svarte ikke i tide.";
    if (kode && kode[1] === "403") return "Nettstedet avviste innhentingen (feilkode 403).";
    if (kode) return "Nettstedet svarte med en feil (feilkode " + kode[1] + ").";
    if (/connection|resolve|ssl/i.test(f)) return "Fikk ikke kontakt med nettstedet.";
    return "Innhentingen feilet.";
  }

  function tegnStatus(status) {
    var tbody = document.querySelector("#status-tabell tbody");
    var inaktiveListe = document.getElementById("inaktive-liste");
    tbody.textContent = "";
    inaktiveListe.textContent = "";
    var kilder = (status && status.kilder) || [];
    var aktive = kilder.filter(function (k) { return k.status !== "ikke overvåket"; });
    var inaktive = kilder.filter(function (k) { return k.status === "ikke overvåket"; });
    var feil = aktive.filter(function (k) { return k.status === "feil"; }).length;

    aktive.forEach(function (k) {
      var ok = k.status === "ok";
      var statusCelle = el("td", null, [el("span", { klasse: "merke " + (ok ? "ok" : "feil"), tekst: ok ? "Hentet" : "Feil" })]);
      if (!ok) statusCelle.appendChild(el("span", { klasse: "feiltekst", tekst: feilforklaring(k.feil) }));
      var apne = tilstand.horinger.filter(function (h) {
        return h.kilde === k.kilde && (h.dager === null || h.dager >= 0);
      }).length;
      tbody.appendChild(el("tr", null, [
        el("th", { scope: "row", tekst: k.kilde }),
        statusCelle,
        el("td", { klasse: "tall", tekst: ok ? String(apne) : "–" })
      ]));
    });
    inaktive.forEach(function (k) { inaktiveListe.appendChild(el("li", { tekst: k.kilde })); });
    document.getElementById("antall-inaktive").textContent = String(inaktive.length);
    document.getElementById("inaktive").hidden = inaktive.length === 0;

    var ingress = aktive.length + " kilder overvåkes automatisk.";
    if (feil) ingress += " " + feil + (feil === 1 ? " kilde" : " kilder") + " kunne ikke hentes ved siste oppdatering, og høringene derfra mangler i listen.";
    if (status && status.generert) ingress += " Sist oppdatert " + norskTidspunkt(status.generert) + ".";
    document.getElementById("status-ingress").textContent = ingress;
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

  function nullstill() {
    settFiltre({ q: "", kategori: "", niva: "", prio: STANDARD_PRIO.slice(), utlopte: false });
    tegn();
    document.getElementById("sok").focus();
  }

  function start() {
    tilstand.iDag = dagensDato();
    var f = skjema();
    f.addEventListener("input", tegn);
    f.addEventListener("change", tegn);
    f.addEventListener("submit", function (e) { e.preventDefault(); });
    document.getElementById("nullstill").addEventListener("click", nullstill);
    document.getElementById("nullstill-tom").addEventListener("click", nullstill);
    document.getElementById("eksport").addEventListener("click", lastNedCsv);
    if (window.matchMedia("(max-width: 52rem)").matches) document.getElementById("filtre-boks").open = false;

    Promise.allSettled([hentJson("data/horinger.json"), hentJson("data/status.json")]).then(function (svar) {
      var oppdatert = document.getElementById("oppdatert");
      if (svar[0].status !== "fulfilled") {
        oppdatert.textContent = "";
        visFeil("Klarte ikke å hente høringene. Last siden på nytt om litt. Vedvarer feilen, si fra til Gjøvikregionen Utvikling.");
        document.getElementById("eksport").disabled = true;
        document.getElementById("antall").textContent = "";
      } else {
        var data = svar[0].value;
        tilstand.horinger = (data.horinger || []).map(function (h) {
          h.frist = h.frist ? String(h.frist).slice(0, 10) : null;
          h.dager = h.frist ? dagerMellom(tilstand.iDag, h.frist) : null;
          return h;
        });
        oppdatert.textContent = data.generert ? "Oppdatert " + norskTidspunkt(data.generert) + "." : "";
        fyllValg("kategori", unike("kategori"));
        fyllValg("niva", unike("niva"));
        settFiltre(filtreFraAdresse());
        tegn();
      }
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
