from http_fuzzer import validate_url, validate_post_body_and_get_fuzzed_param, validate_post_body_param, get_random_ascii_string

def test_validate_url():
    valid_urls= [
        'http://localhost:8080/lookup'
        'http://localhost:8080/lookup',
        'http://127.0.0.1:8080/lookup',
        'https://www.google.com',
        'https://google.com',
    ]
    for url in valid_urls:
        assert validate_url(url) == True

    # Due to CLI options, it shouldn't be possible to pass in non-String data, but let's try anyway
    invalid_urls = [
        4,
        'http://:8080/lookup',
        'localhost:8080/lookup', # Valid URL, but not precise. Require a protocol (http/https)
        '',
        None,
        r'\/\/\/\/\/',
        ''
        'DFJKLKJDF03kj3r://dfj02f',
        f'http://website.com/{get_random_ascii_string(20000)}' # valid but stupid long URL.
    ]
    for url in invalid_urls:
        assert validate_url(url) == False

def test_get_random_ascii_string():
    result = get_random_ascii_string(100)
    assert type(result) == str and len(result) == 100 and result.isascii()

def test_validate_post_body_param():
    valid_params_no_fuzz = [
        "id=fuzzywuzzy",
        "id=123",
        "id=abc",
        "1=2",
        "something=something"
    ]
    valid_params_valid_fuzzywuzzy = [
        "id=FUZZYWUZZY",
        "1=FUZZYWUZZY",
        "id33=FUZZYWUZZY"
    ]
    invalid_params = [ # Some of these may be supported in the future, but right now they are not
        "noEqualsSign+1",
        "id=FUZZYWUZZYandFRIENDS",
        "id=FUZZYWUZZYFUZZYWUZZY",
        "FUZZYWUZZY=1",
        "FUZZYWUZZY=FUZZYWUZZY"
    ]
    for param in valid_params_no_fuzz:
        assert validate_post_body_param(param) == 0
    for param in valid_params_valid_fuzzywuzzy:
        assert validate_post_body_param(param) == 1
    for param in invalid_params:
        assert validate_post_body_param(param) == -1

def test_validate_post_body_and_get_fuzzed_param():
    valid_post_bodies = [
        "id=FUZZYWUZZY&someOtherParm=0",
        "id=FUZZYWUZZY",
        "someOtherParm=FUZZYWUZZY"
    ]
    invalid_post_bodies = [
        "FUZZYWUZZY=1",
        "FUZZYWUZZY2=1",
        "1=FUZZYWUZZY&2=FUZZYWUZZY" # not supporting multiple params fuzzing yet
    ]
    for body in valid_post_bodies:
        assert validate_post_body_and_get_fuzzed_param(body) is not None
    for body in invalid_post_bodies:
        assert validate_post_body_and_get_fuzzed_param(body) is None

