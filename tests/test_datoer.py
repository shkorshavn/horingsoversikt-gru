from datetime import date

import pytest

from horinger.datoer import (
    finn_frist,
    neste_forekomst,
    tolk_dato,
    tolk_iso,
    tolk_ms_dato,
    tolk_punktumdato,
    tolk_tekstdato,
)


@pytest.mark.parametrize(
    "tekst, forventet",
    [
        ("Høringsfrist: 09.01.2027", date(2027, 1, 9)),
        ("2.9.2026", date(2026, 9, 2)),
        ("Referanse: 26-80489-6", None),
        ("31.02.2026", None),
    ],
)
def test_punktumdato(tekst, forventet):
    assert tolk_punktumdato(tekst) == forventet


@pytest.mark.parametrize(
    "tekst, forventet",
    [
        ("9. november 2026", date(2026, 11, 9)),
        ("mandag 12. oktober 2026", date(2026, 10, 12)),
        ("Høringsfristen er 30.september 2026", date(2026, 9, 30)),
        ("1. Desember 2026", date(2026, 12, 1)),
    ],
)
def test_tekstdato_med_ar(tekst, forventet):
    assert tolk_tekstdato(tekst) == forventet


def test_tekstdato_uten_ar_bruker_neste_forekomst():
    ref = date(2026, 9, 18)
    assert tolk_tekstdato("16. oktober kl. 23:59", ref) == date(2026, 10, 16)


def test_tekstdato_uten_ar_over_arsskiftet():
    ref = date(2026, 11, 20)
    assert tolk_tekstdato("Høyringsfrist 15. januar", ref) == date(2027, 1, 15)


def test_tekstdato_uten_ar_og_uten_referanse_gir_none():
    assert tolk_tekstdato("16. oktober") is None


def test_neste_forekomst_samme_dag():
    assert neste_forekomst(16, 10, date(2026, 10, 16)) == date(2026, 10, 16)


def test_tolk_dato_tar_forste_dato():
    assert tolk_dato("fra 13. april 2026 til 15.05.2026") == date(2026, 4, 13)
    assert tolk_dato("fra 01.04.2026 til 15. mai 2026") == date(2026, 4, 1)


@pytest.mark.parametrize(
    "tekst, forventet",
    [
        (
            "Planprogrammet er første fase av arbeidet. Høringsfrist er 11. november 2026.",
            date(2026, 11, 11),
        ),
        ("Frist for innspill er 9. oktober 2026", date(2026, 10, 9)),
        ("Send merknader innen 3. juli 2026 til Nye Veier", date(2026, 7, 3)),
        ("Publisert 01.09.2026. Høringsfrist: 05.01.2027", date(2027, 1, 5)),
        ("Ingen dato her", None),
    ],
)
def test_finn_frist(tekst, forventet):
    assert finn_frist(tekst) == forventet


def test_ms_dato_gir_norsk_tid():
    # 2026-10-11 21:59 UTC = 23:59 norsk sommertid
    tid = tolk_ms_dato("/Date(1791755940000+0200)/")
    assert tid.date() == date(2026, 10, 11)
    assert (tid.hour, tid.minute) == (23, 59)


def test_ms_dato_tom_verdi():
    assert tolk_ms_dato("/Date(-62135596800000)/") is None
    assert tolk_ms_dato(None) is None


def test_iso_uten_tidssone_er_norsk_tid():
    tid = tolk_iso("2026-11-06T23:59:59")
    assert tid.date() == date(2026, 11, 6)
    assert tid.utcoffset().total_seconds() == 3600


def test_iso_ugyldig():
    assert tolk_iso("ikke en dato") is None
    assert tolk_iso("0001-01-01T00:00:00") is None
