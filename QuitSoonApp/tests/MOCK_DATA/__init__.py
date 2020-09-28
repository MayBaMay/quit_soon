#!/usr/bin/env python
# pylint: disable=C0103 #Module name "MOCK_DATA" doesn't conform to snake_case naming style (invalid-name)

"""
Import all data and tools in root package
in order to acces them easily
"""

from .row_data import (
    row_paquet_data, row_conso_cig_data, fake_smoke, fake_smoke_for_trophies,
    row_alternative_data, row_conso_alt_data, fake_healthy
    )
from .clean_data import (
    CreatePacks, CreateSmoke,
    CreateAlternative, CreateConsoAlternative,
    )
