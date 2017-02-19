"""
This module imports all AWS settings from django settings if they are defined with the prefix "AWS_".
This serves the purpose of keeping django tricks active, like overriding settings on tests.

The use of private variable (__variable) prevents importing more than the AWS variables
"""

from django_app import settings as __settings

__aws_imports = [ _ for _ in dir(__settings) if _.startswith("AWS_") ]


for __element in __aws_imports:
    vars()[__element] = getattr(__settings, __element)
