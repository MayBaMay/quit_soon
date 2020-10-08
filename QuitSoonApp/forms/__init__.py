#!/usr/bin/env python

"""Import all forms in root package"""

from .registration_forms import (
    RegistrationForm,
    EmailValidationOnResetPassword
    )
from .parameters_form import ParametersForm
from .healthy_forms import (
    TypeAlternativeForm,
    ActivityForm,
    SubstitutForm,
    HealthForm,
    ChooseAlternativeFormWithEmptyFields,
)
from .smocky_forms import (
    PaquetForm,
    PaquetFormCreation,
    PaquetFormCustomGInCig,
    SmokeForm,
    ChoosePackFormWithEmptyFields,
)
