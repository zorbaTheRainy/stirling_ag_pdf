#!/bin/python3
# assumes Python >= 3.7.x

# to create requirements.txt 
# pipreqs --force  --ignore .venv ; cat requirements.txt
import requests                                  # https://requests.readthedocs.io/en/latest/
from datetime import datetime,timedelta          # https://docs.python.org/3/library/datetime.html
import logging, logging.handlers                 # https://docs.python.org/3/howto/logging.html
import os                                        # https://docs.python.org/3/library/os.html
import sys                                       # https://docs.python.org/3/library/sys.html
import time                                      # https://docs.python.org/3/library/time.html



# ##################################################################
# FUNCTIONS
# ##################################################################

def accessStirlingAPI(url, post_data, inputFile, outputFile):
  """ puts/gets files form the Stirling API.  Performs an aciton based on `post_data` """

  # Prepare data for POST
  data = post_data
  data['fileInput'] = (inputFile, open(inputFile, 'rb'))

  # Perform request
  try:
    # Perform request
    response = requests.post(url, files=data, headers={'accept': '*/*'})
    # Check if request was successful
    response.raise_for_status()
  except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error: {errh}")
    return
  except requests.exceptions.ConnectionError as errc:
    print(f"Error Connecting: {errc}")
    return
  except requests.exceptions.Timeout as errt:
    print(f"Timeout Error: {errt}")
    return
  except requests.exceptions.RequestException as err:
    print(f"Something went wrong: {err}")
    return

  # Write output to file
  try:
    with open(outputFile, 'wb') as f:
      f.write(response.content)
  except IOError as e:
    print(f"An error occurred while writing the output file: {e}")
  # f.close() # in python the `with` automatically closes the file

  return

def reversePages(server, inputFile, outputFile):
  """ Reverses the order of all pages in a PDF """

  url = server + '/api/v1/general/rearrange-pages'
  # see https://scrape-it.cloud/curl-to-python-converter
  post_data = {
      "pageNumbers": (None, 'all'),
      "customMode": (None, 'REVERSE_ORDER')
  }
  accessStirlingAPI(url, post_data, inputFile, outputFile)
  return

def deleteFile(filename):
  """ deletes a file, with some error checking  """
  logger.info(f"Attempting to delete file:")
  logger.info(f"\t{filename}")
  if os.path.exists(filename):
    try:
      os.remove(filename)
      logger.info(f"\tFile successfully deleted.")
      return True
    except:
      logger.warning(f"\tError while trying to delete file: {filename}")
      return False
  else:
    logger.warning(f"\tFile did not exist in the first place. Nothing to do.")
    return True
  
# ##################################################################
# MAIN
# ##################################################################


# -------------------------------------------------------------
# setup logging
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG) # sets the level below which _no_ handler may go
# setup the STDOUT log
consoleHandler = logging.StreamHandler() # well this is annoying.  StreamHandler is logging.* while newer handlers are logging.handlers.*
consoleHandler.setLevel(logging.DEBUG)
consoleFormatter = logging.Formatter('%(message)s')
consoleHandler.setFormatter(consoleFormatter)
logger.addHandler(consoleHandler)

# -------------------------------------------------------------
# initialize configuration variables
isInDocker         = bool(os.getenv("AM_I_IN_A_DOCKER_CONTAINER",0))            # (hidden) Only used to set variables to different values if you're not in a Docker container
serverURL          =      os.getenv("API_SERVER_URL", "http://localhost:8080")  # (optional) The actual StirlingPDF server (default is http://localhost:8080, as this is run inside the same docker)
checkPeriodMin     =  int(os.getenv("CHECK_EVERY_X_MINUTES",2))                 # (optional) How often you want the inputDir scanned for new files
# directories
if isInDocker:
  inputDir  = "/inputDir/"   # mapped via Docker
  outputDir = "/outputDir/"  # mapped via Docker
  logDir    = "/logDir/"     # mapped via Docker
  allowFileDeletion = True
  allowToExitWithoutLoop = False
else:
  inputDir  = "./dirs/inputDir/"   # un-translated docs go here
  outputDir = "./dirs/outputDir/"  # merged & translated docs go here
  logDir    = "./dirs/logDir/"     # mapped via Docker
  allowFileDeletion = False
  allowToExitWithoutLoop = True
# variables shown to outside world
scriptVersion = "0.2.0"
# internal variables
checkPeriodSec = checkPeriodMin * 60 # note my inconsistency between "_Sec" and "Sec" (no underscore) when naming variables.  I know I should be better.


# setup the global log file
try:
  globalLogFile = os.path.join(logDir, "_monitorfolder.log")
  globalFileHandler = logging.handlers.RotatingFileHandler(globalLogFile ,'a',34359738368,3) # filename, append, number of bytes max, number of logs max
  globalFileHandler.setLevel(logging.INFO)
  globalFileFormatter = logging.Formatter('%(asctime)s - %(levelname)7s - %(message)s')
  globalFileHandler.setFormatter(globalFileFormatter)
  logger.addHandler(globalFileHandler)
  globalFileHandler.setFormatter(logging.Formatter('%(message)s')) # turn off the custom formatting too
  logger.info(f"") # start on a fresh line (in-case the server crashed mid-line the previous run)
  globalFileHandler.setFormatter(globalFileFormatter) # turn the formatting back on
  logger.info(f"Creating global log file!")
  logger.info(f"\tGlobal Log file: {globalLogFile}")
except Exception as error:
  globalFileHandler = None # assign the None value if fileHandler failed
  logger.info(f"") # start on a fresh line (in-case the server crashed mid-line the previous run)
  logger.warning(f"Unable to write to global log file!")
  logger.warning(f"\tGlobal Log file: {globalLogFile}")
  logger.warning(f"\t{error}")
logger.info(f'----------------------------------------') # added separator line to global log
logger.info(f'--- Starting new execution of script ---') 
logger.info(f'----------------------------------------') # added separator line to global log

# spit out some debug info
if True:  # really just here for indentation and code folding purposes
  logger.debug(f"Configuration Variables are ...")
  tmpVarB = os.environ.get("API_SERVER_URL")
  tmpVarD = os.environ.get("CHECK_EVERY_X_MINUTES")
  # logger.debug(f"\tDEEPL_AUTH_KEY:          {tmpVarA}")
  # logger.debug(f"\tauth_key:                {auth_key}")
  logger.debug(f"\API_SERVER_URL:               {tmpVarB}")
  logger.debug(f"\t    serverURL:               {serverURL}")
  logger.debug(f"\tCHECK_EVERY_X_MINUTES:       {tmpVarD}")
  logger.debug(f"\t    checkPeriodMin:          {checkPeriodMin}")
  logger.debug(f"\tinputDir:       {inputDir}")
  logger.debug(f"\toutputDir:      {outputDir}")
  logger.debug(f"\tlogDir:         {logDir}")
  logger.debug(f"")
  logger.debug(f"\tallowFileDeletion:         {allowFileDeletion}")
  logger.debug(f"\tallowToExitWithoutLoop:    {allowToExitWithoutLoop}")
  logger.debug(f"")
  logger.debug(f"\tScript name:             {__file__}")
  logger.debug(f"\tScript version:          {scriptVersion}")
  thisFilesLastModDate = datetime.fromtimestamp(os.path.getmtime(__file__))
  logger.debug(f"\tScript last modified:    {thisFilesLastModDate}")

# check that the directories are OK
if not os.access(inputDir, os.W_OK): # need to write due to safe filename renaming
  logger.error(f"Unable to write to input directory!")
  logger.error(f"\t{inputDir}")
  logger.error(f"FATAL ERROR!  Closing Program!")
  exitProgram()
if not os.access(outputDir, os.W_OK):
  logger.error(f"Unable to write to output directory!")
  logger.error(f"\t{outputDir}")
  logger.error(f"FATAL ERROR!  Closing Program!")
  exitProgram()
if not os.access(logDir, os.W_OK): # a non-fatal error if you can't write logs
  logger.warning(f"Unable to write to log file directory!")
  logger.warning(f"\t{logDir}")
  logger.warning(f"Program will still continue, but this should be attended to.")


# -------------------------------------------------------------
# process any files in the directory
logger.info(f'----------------------------------------') # added separator line to global log
while True: # loop forever

  # get every PDF file in inputDir; send it off for processing; output the result in outputDir
  for file in os.listdir(os.fsencode(inputDir)):
      filename = os.fsdecode(file)
      filename_orig = filename
      if filename.lower().endswith(".pdf"): 

        logger.info(f'Processing file: {os.path.join(inputDir, os.fsdecode(file))}') 
        # create variables for all the files
        inputFile  = os.path.join(inputDir, filename)
        outputFile = os.path.join(outputDir, filename)
        logFile    = os.path.join(logDir,os.path.splitext(filename)[0] + '.log')

        reversePages(serverURL, inputFile, outputFile)
        
        # clean up the old files, make sure that inputFiles aren't re-processed at another date
        if (os.path.exists(outputFile)  and allowFileDeletion): # if we successfully created the outputFile
          deleteFile(inputFile)

        logger.info(f'Finished processing file.')
            
        if allowToExitWithoutLoop:
          sys.exit("Exiting program due to allowToExitWithoutLoop variable being set to True.")
        else:
          time.sleep(20) # Delay for X seconds to prevent pounding on the server.

        logger.info(f'----------------------------------------') # added separator line to global log
        continue # move to next file
      else:
        continue # move to next file
  # Delay for X minutes until checking the directory again ... and again ... and again.
  time.sleep(checkPeriodSec)
      

# #####################################
# Version history
# #####################################
# v0.2.0 2023-03-16
#    * Basic functionality
#

