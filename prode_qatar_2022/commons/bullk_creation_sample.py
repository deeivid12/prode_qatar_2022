from datetime import datetime
from django.utils import timezone
from django.utils.timezone import make_aware

# Ejemplo Copa America

bulk_teams = [
    {"name": "Argentina", "fifa_code": "ARG"},
    {"name": "Bolivia", "fifa_code": "BOL"},
    {"name": "Brasil", "fifa_code": "BRA"},
    {"name": "Canada", "fifa_code": "CAN"},
    {"name": "Chile", "fifa_code": "CHI"},
    {"name": "Colombia", "fifa_code": "COL"},
    {"name": "Costa Rica", "fifa_code": "CRI"},
    {"name": "Ecuador", "fifa_code": "ECU"},
    {"name": "Jamaica", "fifa_code": "JAM"},
    {"name": "Mexico", "fifa_code": "MEX"},
    {"name": "Panama", "fifa_code": "PAN"},
    {"name": "Paraguay", "fifa_code": "PY"},
    {"name": "Peru", "fifa_code": "PER"},
    {"name": "USA", "fifa_code": "USA"},
    {"name": "Uruguay", "fifa_code": "URU"},
    {"name": "Venezuela", "fifa_code": "VEN"},
]

bulk_games = [
    {
        "home_team": "Argentina",
        "away_team": "Canada",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 20, 21, 0),
    },
    {
        "home_team": "Peru",
        "away_team": "Chile",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 21, 21, 0),
    },
    {
        "home_team": "Ecuador",
        "away_team": "Venezuela",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 22, 19, 0),
    },
    {
        "home_team": "Mexico",
        "away_team": "Jamaica",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 22, 22, 0),
    },
    {
        "home_team": "USA",
        "away_team": "Bolivia",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 23, 19, 0),
    },
    {
        "home_team": "Uruguay",
        "away_team": "Panama",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 23, 22, 0),
    },
    {
        "home_team": "Colombia",
        "away_team": "Paraguay",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 24, 19, 0),
    },
    {
        "home_team": "Brasil",
        "away_team": "Costa Rica",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 24, 22, 0),
    },
    {
        "home_team": "Peru",
        "away_team": "Canada",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 25, 19, 0),
    },
    {
        "home_team": "Chile",
        "away_team": "Argentina",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 25, 22, 0),
    },
    {
        "home_team": "Ecuador",
        "away_team": "Jamaica",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 26, 19, 0),
    },
    {
        "home_team": "Venezuela",
        "away_team": "Mexico",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 26, 22, 0),
    },
    {
        "home_team": "Panama",
        "away_team": "USA",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 27, 19, 0),
    },
    {
        "home_team": "Uruguay",
        "away_team": "Bolivia",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 27, 22, 0),
    },
    {
        "home_team": "Colombia",
        "away_team": "Costa Rica",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 28, 19, 0),
    },
    {
        "home_team": "Paraguay",
        "away_team": "Brasil",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 28, 22, 0),
    },
    {
        "home_team": "Argentina",
        "away_team": "Peru",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 29, 21, 0),
    },
    {
        "home_team": "Canada",
        "away_team": "Chile",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 29, 21, 0),
    },
    {
        "home_team": "Mexico",
        "away_team": "Ecuador",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 30, 21, 0),
    },
    {
        "home_team": "Jamaica",
        "away_team": "Venezuela",
        "tournament": "Copa America",
        "date_time": datetime(2024, 6, 30, 21, 0),
    },
    {
        "home_team": "Bolivia",
        "away_team": "Panama",
        "tournament": "Copa America",
        "date_time": datetime(2024, 7, 1, 22, 0),
    },
    {
        "home_team": "USA",
        "away_team": "Uruguay",
        "tournament": "Copa America",
        "date_time": datetime(2024, 7, 1, 22, 0),
    },
    {
        "home_team": "Brasil",
        "away_team": "Colombia",
        "tournament": "Copa America",
        "date_time": datetime(2024, 7, 2, 22, 0),
    },
    {
        "home_team": "Costa Rica",
        "away_team": "Paraguay",
        "tournament": "Copa America",
        "date_time": datetime(2024, 7, 2, 22, 0),
    },
]

# Ejemplo Eurocopa

# bulk_teams = [
#     {"name": "Albania", "fifa_code": "ALB"},
#     {"name": "Alemania", "fifa_code": "ALE"},
#     {"name": "Austria", "fifa_code": "AUS"},
#     {"name": "Belgica", "fifa_code": "BEL"},
#     {"name": "Chequia", "fifa_code": "CHE"},
#     {"name": "Croacia", "fifa_code": "CRO"},
#     {"name": "Dinamarca", "fifa_code": "DIN"},
#     {"name": "Escocia", "fifa_code": "SCO"},
#     {"name": "Eslovaquia", "fifa_code": "SVK"},
#     {"name": "Eslovenia", "fifa_code": "SLO"},
#     {"name": "España", "fifa_code": "ESP"},
#     {"name": "Francia", "fifa_code": "FRA"},
#     {"name": "Georgia", "fifa_code": "GEO"},
#     {"name": "Hungria", "fifa_code": "HUN"},
#     {"name": "Inglaterra", "fifa_code": "ING"},
#     {"name": "Italia", "fifa_code": "ITA"},
#     {"name": "Paises Bajos", "fifa_code": "PBA"},
#     {"name": "Polonia", "fifa_code": "POL"},
#     {"name": "Portugal", "fifa_code": "POR"},
#     {"name": "Rumania", "fifa_code": "RUM"},
#     {"name": "Serbia", "fifa_code": "SER"},
#     {"name": "Suiza", "fifa_code": "SUI"},
#     {"name": "Turquia", "fifa_code": "TUR"},
#     {"name": "Ucrania", "fifa_code": "UCR"},
# ]


# bulk_games = [
#     {
#         "home_team": "Alemania",
#         "away_team": "Escocia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 14, 16, 0),
#     },
#     {
#         "home_team": "Hungria",
#         "away_team": "Suiza",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 15, 10, 0),
#     },
#     {
#         "home_team": "España",
#         "away_team": "Croacia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 15, 13, 0),
#     },
#     {
#         "home_team": "Italia",
#         "away_team": "Albania",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 15, 16, 0),
#     },
#     {
#         "home_team": "Polonia",
#         "away_team": "Paises Bajos",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 16, 10, 0),
#     },
#     {
#         "home_team": "Eslovenia",
#         "away_team": "Dinamarca",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 16, 13, 0),
#     },
#     {
#         "home_team": "Serbia",
#         "away_team": "Inglaterra",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 16, 16, 0),
#     },
#     {
#         "home_team": "Rumania",
#         "away_team": "Ucrania",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 17, 10, 0),
#     },
#     {
#         "home_team": "Belgica",
#         "away_team": "Eslovaquia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 17, 13, 0),
#     },
#     {
#         "home_team": "Austria",
#         "away_team": "Francia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 17, 16, 0),
#     },
#     {
#         "home_team": "Turquia",
#         "away_team": "Georgia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 18, 13, 0),
#     },
#     {
#         "home_team": "Portugal",
#         "away_team": "Chequia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 18, 16, 0),
#     },
#     {
#         "home_team": "Croacia",
#         "away_team": "Albania",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 19, 10, 0),
#     },
#     {
#         "home_team": "Alemania",
#         "away_team": "Hungria",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 19, 13, 0),
#     },
#     {
#         "home_team": "Escocia",
#         "away_team": "Suiza",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 19, 16, 0),
#     },
#     {
#         "home_team": "Eslovenia",
#         "away_team": "Serbia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 20, 10, 0),
#     },
#     {
#         "home_team": "Dinamarca",
#         "away_team": "Inglaterra",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 20, 13, 0),
#     },
#     {
#         "home_team": "España",
#         "away_team": "Italia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 20, 16, 0),
#     },
#     {
#         "home_team": "Eslovaquia",
#         "away_team": "Ucrania",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 21, 10, 0),
#     },
#     {
#         "home_team": "Polonia",
#         "away_team": "Austria",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 21, 13, 0),
#     },
#     {
#         "home_team": "Paises Bajos",
#         "away_team": "Francia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 21, 16, 0),
#     },
#     {
#         "home_team": "Georgia",
#         "away_team": "Chequia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 22, 10, 0),
#     },
#     {
#         "home_team": "Turquia",
#         "away_team": "Portugal",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 22, 13, 0),
#     },
#     {
#         "home_team": "Belgica",
#         "away_team": "Rumania",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 22, 16, 0),
#     },
#     {
#         "home_team": "Suiza",
#         "away_team": "Alemania",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 23, 16, 0),
#     },
#     {
#         "home_team": "Escocia",
#         "away_team": "Hungria",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 23, 16, 0),
#     },
#     {
#         "home_team": "Albania",
#         "away_team": "España",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 24, 16, 0),
#     },
#     {
#         "home_team": "Croacia",
#         "away_team": "Italia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 24, 16, 0),
#     },
#     {
#         "home_team": "Francia",
#         "away_team": "Polonia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 25, 13, 0),
#     },
#     {
#         "home_team": "Paises Bajos",
#         "away_team": "Austria",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 25, 13, 0),
#     },
#     {
#         "home_team": "Dinamarca",
#         "away_team": "Serbia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 25, 16, 0),
#     },
#     {
#         "home_team": "Inglaterra",
#         "away_team": "Eslovenia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 25, 16, 0),
#     },
#     {
#         "home_team": "Eslovaquia",
#         "away_team": "Rumania",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 26, 13, 0),
#     },
#     {
#         "home_team": "Ucrania",
#         "away_team": "Belgica",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 26, 13, 0),
#     },
#     {
#         "home_team": "Georgia",
#         "away_team": "Portugal",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 26, 16, 0),
#     },
#     {
#         "home_team": "Chequia",
#         "away_team": "Turquia",
#         "tournament": "Eurocopa",
#         "date_time": datetime(2024, 6, 26, 16, 0),
#     },
# ]