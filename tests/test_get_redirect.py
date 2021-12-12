import random
import pytest
from app.main import get_redirect

@pytest.mark.parametrize(
    "path", (
        "my_path",
        "",
        "region/SEALAND/my_path",
    )
)
def test_get_redirect(mocker, path):
    class Mirror:
        def __init__(self):
            self.mode = "redirect"

        def all_regions(self):
            return ["SEALAND"]

        def next(self, region):
            repos = [
                'example.com/repo/',
                'exampler2.com/nested/repo/',
                'exampler3.com/wild/repo/'
            ]
            self.choice = random.choice(repos)
            return self.choice


    mocker.patch("app.main.get_region", return_value="SEALAND")

    mirror = Mirror()
    client_ip = "192.168.1.1"
    scheme = "https"
    result = get_redirect(path, client_ip, scheme, mirror)
    expected = f"{scheme}://{mirror.choice}my_path"
    if not path:
        expected = f"{scheme}://{mirror.choice}"

    assert result == expected
