# FuzzyWuzzy Http Fuzzer
This directory contains a simple Proof-Of-Concept HTTP fuzzer `./http_fuzzer.py` which may be run with Docker or Python.

## Sample Output
![Demo of using the FuzzyWuzzy Http Fuzzer](media/fuzzy-wuzzy-fullrun.gif)

## Fuzzer Capabilities
The HTTP fuzzer can:
1. Fuzz one `Integer` HTTP body parameter on a HTTP `POST` request to a targeted url, given a range of integers and a parameter name.

## Docker Setup (Recommended)
1. Pick a target to attack or run `python3 -m http.server 8080` to test locally
1. `docker build -t fuzzy-wuzzy .`
1. `docker run --network host -t fuzzy-wuzzy "http://localhost:8080/lookup" "POST" "id=FUZZYWUZZY&someOtherFixedParm=0" --fuzz-data-type "Integer" --fuzz-int-start 0 --fuzz-int-end 100000`

Running `http_fuzzer.exe --help` will produce more detailed instructions on using the tool:

```
Usage: http_fuzzer.exe [OPTIONS] URL HTTP_METHOD POST_BODY

  FUZZYWUZZY, a simple Http Fuzzer tool.

  Quickstart:

  python http_fuzzer.py "http://localhost:8080/lookup" "POST"
  "id=FUZZYWUZZY&someOtherFixedParm=0"

  Advanced Start:

  python http_fuzzer.py http_fuzzer.py "http://localhost:8080/lookup" "POST"
  "id=FUZZYWUZZY&someOtherFixedParm=0" --fuzz-data-type "Integer" --fuzz-int-
  start 0 --fuzz-int-end 100000

  Instructions:

  Use the String FUZZYWUZZY to select a parameter to fuzz, like
  "id=FUZZYWUZZY&someOtherParm=0". By default, the fuzzer will support an
  Integer range of values, and assumes a HTTP 200 response is a success, which
  will then be logged.

  Notes:

  Only POST body requests are currently supported for fuzzing, and currently
  only one parameter may be fuzzed at a time.

Arguments:
  URL          A HTTP URL like http://domainName:8080/lookup  [required]
  HTTP_METHOD  POST (only POST supported at this time)  [required]
  POST_BODY    [required]

Options:
  --fuzz-data-type TEXT     [default: Integer]
  --fuzz-int-start INTEGER  [default: 0]
  --fuzz-int-end INTEGER    [default: 100000]
  --help                    Show this message and exit.
```

## Python Setup
(Important Note: `PATH_TO_YOUR_PYTHON_BINARY` and the keywords `python3` or `python` can often be used interchangeably below, but for MacOS and Linux especially you will want to install a version of Python that is isolated from your System's built-in Python or use [Virtual Environments](https://realpython.com/python-virtual-environments-a-primer/))

1. Install [Python](https://www.python.org/downloads/) >= 3.10, or install [Visual Studio Code](https://code.visualstudio.com/download), and then install the official [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python). Both of these methods should put `python` on your `PATH` variable.
2. Find where your Python executable lives
    - Check manually or type `where python` or `which python`
3. Clone this repo, and open up a Terminal/CommandPrompt/Shell there. From here, run `cd scanner`. 
4. Run `PATH_TO_YOUR_PYTHON_BINARY -m pip install -r requirements.txt` **twice**
5. Finally, run the actual scanner! Choose a parameter value to fuzz, and put the String "FUZZYWUZZY" inside it to select it for fuzzing.
    - Run it without optional arguments:
        -  `PATH_TO_YOUR_PYTHON_BINARY http_fuzzer.py "http://localhost:8080/lookup" "POST" "id=FUZZYWUZZY&someOtherFixedParm=0"`
    - Run it with optional arguments:
        - `PATH_TO_YOUR_PYTHON_BINARY http_fuzzer.py "http://localhost:8080/lookup" "POST" "id=FUZZYWUZZY&someOtherFixedParm=0" --fuzz-data-type "Integer" --fuzz-int-start 0 --fuzz-int-end 100000`
6. Use the `--help` flag to receive more instructions, like below:

```
Usage: http_fuzzer.exe [OPTIONS] URL HTTP_METHOD POST_BODY

  FUZZYWUZZY, a simple Http Fuzzer tool.

  Quickstart:

  python http_fuzzer.py "http://localhost:8080/lookup" "POST"
  "id=FUZZYWUZZY&someOtherFixedParm=0"

  Advanced Start:

  python http_fuzzer.py http_fuzzer.py "http://localhost:8080/lookup" "POST"
  "id=FUZZYWUZZY&someOtherFixedParm=0" --fuzz-data-type "Integer" --fuzz-int-
  start 0 --fuzz-int-end 100000

  Instructions:

  Use the String FUZZYWUZZY to select a parameter to fuzz, like
  "id=FUZZYWUZZY&someOtherParm=0". By default, the fuzzer will support an
  Integer range of values, and assumes a HTTP 200 response is a success, which
  will then be logged.

  Notes:

  Only POST body requests are currently supported for fuzzing, and currently
  only one parameter may be fuzzed at a time.

Arguments:
  URL          A HTTP URL like http://domainName:8080/lookup  [required]
  HTTP_METHOD  POST (only POST supported at this time)  [required]
  POST_BODY    [required]

Options:
  --fuzz-data-type TEXT     [default: Integer]
  --fuzz-int-start INTEGER  [default: 0]
  --fuzz-int-end INTEGER    [default: 100000]
  --help                    Show this message and exit.
```

## Testing
1. Run `PATH_TO_YOUR_PYTHON_BINARY -m pip install -r requirements.txt` **twice**, if you haven't already.
2. Run `PATH_TO_YOUR_PYTHON_BINARY -m pytest` in the `./scanner` directory
![Alt text](media/test-run.png)

## Distribution
Create a native binary that matches your OS using `pyinstaller`. This has been tested on Windows:
1.  `PATH_TO_YOUR_PYTHON_BINARY -m pip install pyinstaller`
2.  `PATH_TO_YOUR_PYTHON_BINARY -m PyInstaller http_fuzzer.py --onefile`