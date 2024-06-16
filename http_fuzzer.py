import asyncio
import aiohttp
import re
import random
import string
import time
import typer
from typing_extensions import Annotated
import validators

def main(url: Annotated[str, typer.Argument(help="A HTTP URL like http://domainName:8080/lookup")], 
         http_method: Annotated[str, typer.Argument(help="POST (only POST supported at this time)")], 
         post_body: str,
         fuzz_data_type: str = 'Integer', # optional param in CLI looks like 'fuzz-data-type'
         fuzz_int_start: int = 0, # optional param in CLI looks like 'fuzz-int-start'
         fuzz_int_end: int = 100000, # optional param in CLI looks like 'fuzz-int-end'
         ):
    """
    FUZZYWUZZY, a simple Http Fuzzer tool. 
    
    Quickstart:

    python http_fuzzer.py "http://localhost:8080/lookup" "POST" "id=FUZZYWUZZY&someOtherFixedParm=0"

    Advanced Start:

    python http_fuzzer.py http_fuzzer.py "http://localhost:8080/lookup" "POST" "id=FUZZYWUZZY&someOtherFixedParm=0" --fuzz-data-type "Integer" --fuzz-int-start 0 --fuzz-int-end 100000

    Instructions:

    Use the String FUZZYWUZZY to select a parameter to fuzz, like "id=FUZZYWUZZY&someOtherParm=0". By default, the fuzzer
    will support an Integer range of values, and assumes a HTTP 200 response is a success, which will then be logged.
    
    Notes:

    Only POST body requests are currently supported for fuzzing, and currently only one parameter may be fuzzed at a time.

    """

    if not validate_url(url):
        raise Exception('Error: Invalid URL provided.')
    
    if not validate_http_method(http_method):
        raise Exception('Error: Invalid or Unsupported HTTP method provided.')
    
    if not validate_fuzz_data_type(fuzz_data_type):
        raise Exception('Error: Integer is the only valid value for this argument right now')
    
    if not validate_fuzz_int_start(fuzz_int_start) or not validate_fuzz_int_end(fuzz_int_end):
        raise Exception('Error: Invalid integers provided')
    
    fuzzed_param = validate_post_body_and_get_fuzzed_param(post_body)
    if not fuzzed_param:
        raise Exception('Error: Invalid POST body provided. Did you include exactly FUZZYWUZZY in your value?')
    
    print(f'Attempting to fuzz {http_method} body {post_body} for {fuzz_data_type} values at {url} '
          f'from {fuzz_int_start} to {fuzz_int_end}')

    # Keep track of how long it took to fuzz
    start_time = time.time()

    post_body_parm_name = fuzzed_param.split('=')[0]

    # Warning: While simple, this code will gobble up memory for lange ranges. Refactor if you have time!
    post_body_parms = [(post_body_parm_name+'='+ str(x)) for x in range(fuzz_int_start, fuzz_int_end + 1)]
    
    data_payloads = post_body_parms
    headers = []

    asyncio.run(post_fixed_url_variable_data(url, data_payloads, headers))

    print(f'Program took {(time.time() - start_time)} seconds to run')

def validate_fuzz_data_type(data_type_str):
    """Better be 'Integer', since that is the only val supported"""
    return data_type_str.upper() == 'INTEGER'

def validate_fuzz_int_start(start_int):
    """The starting integer to start fuzzing with"""
    return type(start_int) is int

def validate_fuzz_int_end(end_int):
    """The ending integer to end fuzzing with"""
    return type(end_int) is int

def validate_post_body_and_get_fuzzed_param(post_body):
    """Validate HTTP POST Form Data Body. Must have EXACTLY ONE FUZZYWUZZY value
       Quite a lot to validate here...
       Ran out of time to validate for Parameter Polution like id=123&id=123"""

    number_of_fuzzed_parms = 0
    fuzzed_param_str = ''
    # FUZZYWUZZY is required to fuzz a parameter. '=' is needed for param assignment
    if not '=' and 'FUZZYWUZZY' not in post_body:
        return None
    
    if '&' in post_body: # then we have multiple parms
        params = post_body.split('&')
    else: # only 1 param
        params = [post_body]

    for param_str in params:
        result_code = validate_post_body_param(param_str)
        if result_code == -1: # Invalid param
            return None
        elif result_code == 1: # Found EXACTLY one FUZZYWUZZY, in value
            number_of_fuzzed_parms +=1
            fuzzed_param_str = param_str
        elif result_code == 0: # Valid params but no FUZZYWUZZY found
            pass
        else:
            return None # Some other weird unknown code???

    if number_of_fuzzed_parms == 1:
        return fuzzed_param_str
    
    return None

    
def validate_post_body_param(param):
    """Return -1 if invalid param, 1 if valid and ONE FUZZYWUZZY found in value, 0 if valid but no FUZZYWUZZY found """
    if '=' not in param:
        return -1
    key, value = param.split('=')
    if 'FUZZYWUZZY' in key:
        return -1 # not supporting fuzzing of param names yet
    if 'FUZZYWUZZY' in value:
        if 'FUZZYWUZZY' == value: # we want our value to EXACTLY equal our fuzzing parameter, for now
            return 1
        else:
            return -1 # Catch cases where FUZZYWUZZY is there, but not EXACTLY one FUZZYWUZZY
    else:
        return 0

def validate_http_method(http_method):
    """Validate HTTP methods that we support"""
    if http_method.upper() == 'POST':
        return True
    else:
        print("Error: POST is the only supported HTTP method at this time.")
        return False

def validate_url(url):
    """Validate a URL using validators, Regex and other tricks"""

    if not url or url == '' or type(url) is not str or len(url) > 10000:
        print("Error: Invalid URL: Wrong data type or too long")
        return False

    if validators.url(url):
        return True
    else:
        # localhost URLs fail validation in recommended Python validation libraries. Use 127.0.0.1 instead of localhost
        matches = re.search("localhost", url)
        if matches:
            url = find_and_replace_localhost_with_ip_in_url(url)

        # Try to validate our url again, now that we replaced 'localhost' with 127.0.0.1
        if validators.url(url):
            return True
        else:
            return False
    
    return False

def find_and_replace_localhost_with_ip_in_url(url):
    """Silly little function to replace localhost with 127.0.0.1"""
    matches = re.search("localhost", url)
    if matches:
        if matches.start() == 0: # e.g. localhost to 127.0.0.1
            url = replace_localhost_with_ip(url, 0)
        elif matches.start() == 6: # e.g. http://localhost to http://127.0.0.1
            url = replace_localhost_with_ip(url, 6)
        elif matches.start() == 7: # e.g. https://localhost to https://127.0.0.1
            url = replace_localhost_with_ip(url, 7)
    return url

def replace_localhost_with_ip(url, start_index):
    """Weird String operations to ONLY replace localhost with 127.0.0.1, exactly where we want it"""
    new_url = url[0:start_index] + '127.0.0.1' + url[start_index + len('127.0.0.1'):len(url)+1]
    return new_url

def get_random_ascii_string(length):
    """Generate a random ASCII string. Credit: https://pynative.com/python-generate-random-string/"""
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print(result_str)
    return result_str

async def post_fixed_url_variable_data(url, data_payloads, headers):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[post_formdata(url, data, headers, session) for data in data_payloads])
    print(f'Finished making {len(ret)} requests to {url}.')

async def post_formdata(url, data, headers, session):
    """POST application/x-www-form-urlencoded non-JSON traditional form data"""

    field_name, field_val = data.split('=')
    formdata = aiohttp.FormData()
    formdata.add_field(field_name, field_val)
    try:
        async with session.post(url=url, data=formdata, headers=headers) as response:
            if response.status == 200:
                print(f'POST {url} {data} {response.status}')
            
    except Exception as e:
        print(f'Unable to get url {url} due to {e.__class__}.')

if __name__ == '__main__':
    # And no CLI tool would be complete without some OG ASCII art (my art, used this tool https://www.asciiart.eu/image-to-ascii)
    print("""      .  . .   .       .   .           .              .        .            .           .       .        .   .  .      . .     ..      .      
.          .   .    .           .    .           ..        .                   .                            .  .       .         .   .        
   #@@@@@@@@@  @@@@    @@@@  @@@@@@@@@@@.@@@@@@@@@@@ @@@@     @@@@@@@@   @@@@   @@@@ @@@@  . @@@@ .@@@@@@@@@@% @@@@@@@@@@@ @@@@    .@@@@  . . 
   .@@@@@@@@@  @@@@  . @@@@ .@@@@@@@@@@@ @@@@@@@@@@@  @@@@   @@@@ .@@@  :@@@@  .@@@ .@@@@    @@@@ :@@@@@@@@@@@ @@@@@@@@@@@  @@@@  .@@@@   .   
   .@@@        @@@@    @@@@    .. @@@@        #@@@@     @@@@@@@=  .@@@+ @@@@@@.@@@+  @@@@... @@@@       @@@@      . @@@@     %@@@@@@@ .   . . 
   .@@@@@@@@*  @@@@ .  @@@@    .@@@@-   .   @@@@@   . .  @@@@@      @@@ @@ .@@.@@@   @@@@    @@@@    +@@@@ .      @@@@-     .  @@@@@       .  
   .@@@.    .  @@@@    @@@@   @@@@    .   @@@@@ .   . ..  @@@:.  . .@@@@@@  @@@@@@.  @@@@    @@@@   @@@@        @@@@. .  .     *@@@ ..     . .
   .@@@:       %@@@@*:@@@@:.@@@@@@@@@@@@.@@@@@@@@@@@+ .   @@@-.     -@@@@   #@@@@    @@@@@:@@@@@  @@@@@@@@@@@@:@@@@@@@@@@@   . #@@@   . .     
.. %@@@@       . @@@@@@@@. .@@@@@@@@@@@@.@@@@@@@@@@@*    .@@@%    .  @@@@    @@@@    ..@@@@@@@=   @@@@@@@@@@@@:@@@@@@@@@@@   . @@@@  . .   .  
      .        ..   .   .        ..    ..  ..  .     .         .   .        .. . .      .    .   .    .                   .  .         .      
.     .. ...      .  .   .    . .    .         ..  . .  .  . .   . .   .          .      .. .     . .  .       . .        .   ..   .  .  .    
.                 .  .  .      .         .    .                                   . .   .       .             .  ..   .       ..   .          
  .        .                .  .   .   .               .             
                        ..              .     .  .*@ @@  @ @@  @-    
   .       @@@@@@@@@-     .        . .          @@%@@% @  @ @@ @.    
.   .      @+.      @@@.   .            .  .   %@ . .. @@@@@@@ @@@@  
 .         @           @#:@@@@@@@@@@@@@@@@@@@@-@+   @@@@@@@@@@@%. @  
 .     . . @  @@@@@@@@@@@@           .        @@@@@@@@@@@@@@@@@*  @  
      ..  @@@@@@@@@@@@@.  .@       .      .       @@@@@@@@@@@@@#  @  
   .     @ @@@@@@@@@# .   . @       ...      . @@   @@@@@@@@@@@: @:  
 .     @@. @@@@@@@@          @@     .         @@.. ..#@@@@@@@*.@@-   
    .@@+    @@@@@*          .  @@    .      @@         @-.  @@@    . 
        @@.    @%  .:@@    . @@ @@       @@  -@@@       @@@@   .. .  
.   .   @@@@@@@@      .@@# @@   .@@%  .@@  @@@@@@@@*    =@     .  .  
  .           @          @@@              @@@@@@@@@@+ .  @*         .
 .           .@   . .  +@@  @@@  . .  .  @@@@@@@@@@@@    @@ .      . 
  ..  .      *@   .. =@@ .     @@    .   *@@@@@@@@@@:     @          
      ...    @@ ..            :@@@@@@@.    @@@@@@@@.    .#@.    .  . 
    .    .  @@@@@@        @@@         .@@    -%%.        @@         .
    ..     @@@@@@@@@:%@@@@   -@@@@@@   ..@.   .   .     =@*   .  .   
    .     @@@@@@@@@@@@@     @@@@@@@@@@    @@@@@@@@@@@@@@@            
   ..  . :@@@@@@@@@@@@      @@@@@@@@@@.     @@@@@@@@@@@@@     .    . 
  . ..    @@@@@@@@@@@    @. =@@@@@@@@     .  @@@@@@@@@@@@   . . .    
   ..    #@@@@@@@@@@@    @     @@=   .@       @@@@@@@@@@@=.    .  .  
   ..    @@@@@@@@@@@@. ..@@    @@     @      .:@@@@@@@@@@:   .  ..   
 .       @@@@@@@@@@@@     %@@@@@  -@@@*  .   .@@@@@@@@@@@-     ..    
       .  @@@@@@@@@@@      . @@@@@@@         @@@@@@@@@@@@   .  .   . 
   .  .    @@@@@@@@@@@@     .           .   @@@@@@@@@@@@@  .       . 
  .    .. .  @@@@@@@@@@@@@@+  .          @@@@@@@@@@@@@@@@ .          
..  . .  . .  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@     .....  
           .    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@              
        .          @@@@@@@@@@@@@@@@@@@@@@@@@@@@@#    ..   .  .       
 . .      . . ..       @@@@@@@@@@@@@@@@@@@@@@@+          .      .    
    ..  .    ..      . . .    :....=@@@@@@@ .    .           .  .    
     .       .    ..      ..                      ..       .         
  .  .   . .             .     .              .    .  .       ..     
          .          .                      ..                   ... 
          """)
    typer.run(main)