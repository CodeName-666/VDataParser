"""Default values for global market settings.

These values are used when no market settings are provided in the project
configuration. They mirror the fields of
:class:`objects.SettingsContentDataClass`.
"""

from typing import Dict

market_settings: Dict[str, str] = {
    "max_stammnummern": "250",
    "max_artikel": "40",
    "datum_counter": "2025-09-15 12:00:00",
    "flohmarkt_nr": "6",
    "psw_laenge": "10",
    "tabellen_prefix": "str",
    "verkaufer_liste": "verkeaufer",
    "max_user_ids": "8",
    "datum_flohmarkt": "2025-09-15",
    "flohmarkt_aktiv": "nein",
    "login_aktiv": "nein",
}
