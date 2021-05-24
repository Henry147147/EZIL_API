# EZIL_API
Simple tracker for workers on ezil.me mining pool. Used if you need to know how much each worker has earned

Required packages/programs: 
  - python 3.8 or higher
  - ast
  - requests
  - os
  - time
  - matplotlib

# Usage
- Put the python project in a directory that preferably you can access from another device, ie. on in NAS directory 
- Run the start.py on a device that will not be turned off, ie. a Raspberry pi or on the mining rig, this will poll the ezil api to get worker data
- If you want to calculate the eth per worker, run evaluate_data.py. If you are running from the same device as the ezil api tracker is running, then no modification to this file is required. If you are running from another machine, either run the evaluate_data.py from the same directory with the "\\\Data\\\\" directory in it or change the PATH variable in evaluate_data.py to reflect the location of the "\\\Data\\\\" directory  This will display a graph along with outputting the balance of each worker

# Purpose
This program was written so many people could mine to ezil.me pool and reach the payout quicker but still have certainty on who earned what.  
