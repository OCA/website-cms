# Copyright 2024 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


class FormRedirect(Exception):
    """Triggers a redirect to given URL."""

    def __init__(self, message, next_url):
        super().__init__(message)
        self.next_url = next_url
