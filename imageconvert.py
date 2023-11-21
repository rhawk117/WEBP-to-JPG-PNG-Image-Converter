# everyone hates webp so...
# Automated WEBP to JPG or PNG image converter
# Created by: rhawk117
import logging as log
import os 
import sys
import requests as req
import re as regex 
import traceback as trace
from time import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --divider--
@staticmethod
def get_input(prompt: str, options: list) -> str:
    '''
    recursive input validation, recursive calls end as soon
    as valid input is provided (in options param) 
    '''
    usr_input = input('[?] '+ prompt).lower()
    if usr_input not in options:
        log.warning(f'User provided invalid input -> {usr_input}')
        print(
            f'[*] User Input Invalid [*] \n' +
            f'[*] Pick one of the following -> ' + ' , '.join(options))
        return get_input(prompt, options)
    else:
        log.info('Successfully recieved user input, returning to main')
        return usr_input

# --divider--
@staticmethod
def try_request(url:str) -> bool:
    '''
    used to see if the URL inputed by the user is 
    reachable by checking HTTP get request response 
    and status code
    '''
    if url == '':
        return False
    
    response = req.get(url)
    print(f'[*] Sent GET -> {url} and recieved a...\n>>{response.status_code} status code')
    try:
        response.raise_for_status()
        if response.status_code == 200: # if URL is reachable
            return True
    except req.exceptions.RequestException:
        print('[!] GET Request failed, ensure you provided a valid image address URL request.' + trace.format_exc())
        log.critical('[!] A req.exceptions.RequestException was raised!')
        log.critical(trace.format_exc())
        return False
    except Exception:
        print('[!] An unaccounted for exception occured, more information listed below.\n' + trace.format_exc())
        log.critical('An unaccounted Exception was raised in TryRequests!')
        log.critical(trace.format_exc())
        return False 

# --divider--
@staticmethod
def download_image(img_url:str, file_name) -> bool:
    '''
    Download the image from the image address recieved / returned
    from the process request function by writing the images binary, 
    returning true if successful; false if the attempt is unsuccessful
    '''
    try:
        os.chdir('output') # if your output directory is different, change it to the file path of it
        print(f'[*] Sending GET Request -> {img_url}')
        get_response = req.get(img_url)
        print(f'[*] GET Request successful! Attempting to download images binary...')
        with open(file_name, mode = 'wb') as img_file:
            img_file.write(get_response.content)
            print(f'[+] Successfully downloaded the image file.\nImage File Path: {img_file.name}\nClosing file..')
        return True 
    except Exception:
        print('[!] An error occured while trying to download your image file.')
        trace.print_exc()
        print(f'[+] However, you can still download it manually at -> {img_url} ')
        return False 

# --divider--
@staticmethod
def process_request(url:str):
    '''
    using the temporary image address URL 
    returned from HTTP GET request in main
    we use selenium to click the 'convert image'
    button on the website and then return the 
    converted image address to be downloaded
    '''

    start = time()
    print('*'*25)
    print('[*] Attempting to process user request...\nThis may take a while, selenium moment.')
    print('[*] Opening FireFox in headless mode...')
    config = webdriver.FirefoxOptions() 
    config.add_argument("--headless")
    try:
        print('[*] Initializing Driver Instance..')
        with webdriver.Firefox(options=config) as driver:
            delay = WebDriverWait(driver, 10)
            print(f'[*] Contacting -> {url}')
            driver.get(url)
            print('[*] Trying to click submit to load converted image')
            submit = delay.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR, '#tool-submit-button > input' 
                    )
                )
            )
            submit.click()
            print('[*] Clicked on submit trying to find the converted image, fetching converted image address...')
            img_scan = delay.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR, '#output > p.outfile > img' 
                    ) 
                )
            )
            img_address = img_scan.get_attribute('src')
            print('[*] Found converted image, returning image address for processing')
            print(f'[*] Request took approximately {round(time() - start, 2)} seconds to process.')
            return img_address 
    except Exception as error:
        print(f'Something went wrong....\nException information below: {trace.format_exc()}')
        log.critical('An Exception was raised while attempting to process request!')
        log.critical(trace.format_exc())
        
# --divider--
@staticmethod
def check_file_name(file_name:str, extension:str) -> bool:
    '''
    checks the file name inputed by user to see if it's a 
    valid file name returning true if it is, false otherwise
    '''
    if file_name == '':
        return False
    prefix = '[!] Invalid File Name [!]\n'
    expression = regex.compile(r"^[A-Za-z0-9_.-]*$")
    if not regex.match(expression, file_name):
        print(prefix + 'Cannot create a file with invalid characters')
        return False

    # Check for valid extension
    if not file_name.endswith('.' + extension):
        print(prefix + f'Files must end with the .{extension} extension')
        return False

    # Check for maximum length
    if len(file_name) > 25:
        print(prefix + 'File names should be less than 25 characters')
        return False

    # Check for reserved names
    if file_name.lower() in ["con", "prn", "nul"]:
        print(prefix + 'File names cannot be reserved')
        return False
    
    # Check in Presets folder if file with same name exists
    if os.path.isfile('output\\' + file_name):
        print(prefix + 'A file with the same name already exist!')
        return False 
    
    return True # file name passes all checks, return True

# --divider--
@staticmethod
def header() -> None:
    print('**Convert WEBP to JPG or PNG***')
    print('***Developed by rhawk117***')
    print('GitHub: https://github.com/rhawk117')

# --divider--
@staticmethod
def main() -> None:
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(path) # change CWD to program's dir
    prog_log = 'logs\\prog_log.log' 

    if not os.path.exists('logs'): # if a logging directory doesn't exist 
        print('[!] Couldn\'t find a log directory, making one to store program logs')
        os.mkdir('logs')

    try: # override previous program log, adjust if you'd like to save individual program logs
        with open(file=prog_log, mode='w'):
            pass
    except Exception:
        print('[!] Coudln\'t create or overwrite log of program instance... ;/')
    log.basicConfig(level=log.DEBUG, format=' %(asctime)s – %(levelname)s -%(message)s', filename=prog_log)

    if not os.path.exists('output'): # if the output directory used by the program doesn't exist
        print('[!] Could not find an output directory, making one..')
        os.mkdir('output')

    running = True
    while running: # program loop
        header()
        # get image address url from user
        extension = get_input('Convert WEBP image to JPG or PNG: ', ['png','jpg'])
        query = f'https://ezgif.com/webp-to-{extension}?url='# URL image address 
        complete_url = ''
        while not try_request(complete_url):
            img_address = input('Enter a URL to the WEBPs image Address: ')
            complete_url = query + img_address
        complete_url = req.get(complete_url).url # gets the temporary redirect URL created when img is submitted 
        
       # get output image file from user
        output_file = ''
        while not check_file_name(output_file, extension):
            output_file = input(f'Enter the name for output file ending with the ".{extension}" file extension: ')
        print(f'The {output_file} will be saved in the programs output directory.')

        # attempt to process users request
        log.info('Calling process_request function')
        print('[*] Attempting to process user request..')
        img_address = process_request(complete_url) 
        
        print(f'[+] Converted Image Address Found -> {img_address}\nStarting Download Attempt..')
        download_image(img_address, output_file)
        choice = get_input('Would you like to convert another image (y/n): ', ['y', 'n'])
        if choice == 'y':    
            print('[~] Restarting Main Routine..\n\n\n')
            log.info('User opted to process another image, restarting program.\n\n')
            continue
        else:
            print('[*] Exiting Program [*]')
            log.info('User entered no, exiting program.')
            break

if __name__ == '__main__':
    main()
    input("[*] Press 'enter' to close the program [*]\n")
    sys.exit()