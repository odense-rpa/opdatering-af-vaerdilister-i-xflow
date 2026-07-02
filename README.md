# Opdatering af værdilister i XFlow

Robotten henter organisationer og leverandører fra KMD Nexus og opdaterer tilsvarende værdilister i XFlow, så dropdowns i XFlow-formularer altid afspejler aktuelle Nexus-data.

## Hvad gør robotten?

1. Henter alle organisationer fra KMD Nexus og opdaterer værdilisten **Nexus - organisationer** i XFlow.
2. Henter organisationer fra Nexus med træhierarki, filtrerer til en godkendt delmængde af hjemmeplejeorganisationer, flader hierarkiet ud og opdaterer værdilisten **Nexus - organisationer til POF-robot** i XFlow. Den godkendte liste er hardcodet i `main.py`.
3. Henter alle leverandører fra KMD Nexus og opdaterer værdilisten **Nexus - leverandører** i XFlow.
4. Henter leverandører fra Nexus, filtrerer til kun leverandører af organisationstype med godkendte Ældrелoven-paragraffer (§ 7, § 9, § 9 stk. 2, § 11, § 16) og opdaterer værdilisten **Nexus - organisationsleverandører** i XFlow.

Opgaveafvikling registreres løbende i ODK Tracker.

## Forudsætninger

- Python ≥ 3.13
- [`uv`](https://docs.astral.sh/uv/) til pakkehåndtering
- Adgang til **Automation Server**
- Adgang til **KMD Nexus** (produktion)
- Adgang til **XFlow** (produktion)
- Adgang til **Odense SQL Server** (ODK Tracker)

## Installation

```sh
uv sync
```

## Konfiguration

Credentials registreres i Automation Server:

- `KMD Nexus - produktion`
- `Xflow - produktion`
- `Odense SQL Server`

## Kørsel

```sh
uv run python main.py
```

## Afhængigheder

| Pakke | Formål |
|---|---|
| `automation-server-client` | Forbinder til Automation Server og henter credentials |
| `kmd-nexus-client` | Henter organisationer og leverandører fra KMD Nexus |
| `odk-tools` | Registrerer opgaveafvikling og fakturering i ODK Tracker |
| `xflow-client` | Søger og opdaterer værdilister i XFlow |
