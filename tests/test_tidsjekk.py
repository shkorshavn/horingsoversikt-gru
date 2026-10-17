from datetime import UTC, datetime, timedelta

from horinger.tidsjekk import main, skal_kjore

SOMMER_MANDAG = datetime(2026, 10, 19, 8, 3, tzinfo=UTC)  # mandag, UTC+2
VINTER_MANDAG = datetime(2026, 11, 2, 9, 4, tzinfo=UTC)  # mandag, UTC+1


def test_sommertid_kjorer_kl_8_utc():
    assert skal_kjore("schedule", "0 8 * * 1", SOMMER_MANDAG)[0]
    assert not skal_kjore("schedule", "0 9 * * 1", SOMMER_MANDAG.replace(hour=9))[0]


def test_vintertid_kjorer_kl_9_utc():
    assert skal_kjore("schedule", "0 9 * * 1", VINTER_MANDAG)[0]
    assert not skal_kjore("schedule", "0 8 * * 1", VINTER_MANDAG.replace(hour=8))[0]


def test_overgang_til_vintertid():
    # Sommertiden slutter søndag 25. oktober 2026. Mandagen etter er det UTC+1.
    mandag = datetime(2026, 10, 26, 8, 0, tzinfo=UTC)
    assert not skal_kjore("schedule", "0 8 * * 1", mandag)[0]
    assert skal_kjore("schedule", "0 9 * * 1", mandag.replace(hour=9))[0]


def test_forsinket_kjoring_bruker_tidsplanen():
    # Kjøringen fra «0 8» kan starte for sent, f.eks. 09.20 UTC. Den skal likevel kjøre.
    forsinket = SOMMER_MANDAG.replace(hour=9, minute=20)
    assert skal_kjore("schedule", "0 8 * * 1", forsinket)[0]


def test_manuell_kjoring_alltid():
    assert skal_kjore("workflow_dispatch", "", SOMMER_MANDAG)[0]


def test_ukjent_tidsplan():
    assert not skal_kjore("schedule", "*/5 * * * *", SOMMER_MANDAG)[0]


def test_krev_fersk_hopper_over_ekstraforsok():
    tirsdag = SOMMER_MANDAG + timedelta(days=1)
    nylig = SOMMER_MANDAG
    gammel = SOMMER_MANDAG - timedelta(days=7)
    assert not skal_kjore("schedule", "0 8 * * 2", tirsdag, nylig, krev_fersk=True)[0]
    assert skal_kjore("schedule", "0 8 * * 2", tirsdag, gammel, krev_fersk=True)[0]
    assert skal_kjore("schedule", "0 8 * * 2", tirsdag, None, krev_fersk=True)[0]
    # Mandag kjøres alltid, selv om kilden er fersk.
    assert skal_kjore("schedule", "0 8 * * 1", SOMMER_MANDAG, nylig, krev_fersk=True)[0]


def test_main_skriver_github_output(tmp_path, monkeypatch, capsys):
    utfil = tmp_path / "out"
    monkeypatch.setenv("GITHUB_OUTPUT", str(utfil))
    main(["--hendelse", "workflow_dispatch"])
    assert utfil.read_text() == "kjor=true\n"
    assert "Kjører" in capsys.readouterr().out
