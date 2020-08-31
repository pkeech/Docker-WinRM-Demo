## IMPORT FLASK MOUDLE & EXTENSIONS
from flask import url_for

## MAIN PAGE
class testMain(object):
    def test_home_page(self, client):
        response = client.get(url_for('app.index'))
        assert response.status_code == 200