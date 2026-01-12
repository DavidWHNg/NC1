# Import packages
from psychopy import core, event, gui, visual, parallel, prefs
import time
import math
import random
import csv
import os
ports_live = None # Set to None if parallel ports not plugged for coding/debugging other parts of exp

### Experiment details/parameters
## equipment parameters
port_buffer_duration = 1 #needs about 0.5s buffer for port signal to reset 
pain_response_duration = float("inf")
response_hold_duration = 1 # How long the rating screen is left on the response (only used for Pain ratings)
RENS_pulse_int = 0.1 # interval length for RENS on/off signals (e.g. 0.1 = 0.2s per pulse)

# parallel port triggers
port_address = 0x3ff8
pain_trig = 2 #levels and order need to be organised through CHEPS system
eda_trig = 1 #pin 1 to mark trial information on LabChart
tens_trig = {"RENS": 128, "control": 0} #Pin 8 in relay box just for the clicking sound

## within experiment parameters
experimentcode = "NC1"
P_info = {"PID": "",
        "SONA" : ""}
info_order = ["PID"]

# iti_range = [6,8]
iti = 6
familiarisation_iti = 3
cue_colours = ([-1,0.10588,-1],[-1,-1,1]) # 2 colours taken from Kirsten EEG
cue_colour_names = ('green','blue')
cue_positions = [(300,0),(-300,0)]
cue_width = 200

rating_scale_pos = (0,-350)
rating_text_pos = (0,-250) 
text_height = 30 
textStim_arguments = {'height':30,
                      'color': "white",
                      'wrapWidth': 960}

#calculate iti_jitter
# iti_jitter = [x * 1000 for x in iti_range]

# Participant info input
while True:
    try:
        P_info["PID"] = input("Enter participant ID: ")
        if not P_info["PID"]:
            print("Participant ID cannot be empty.")
            continue
        
        P_info["SONA"] = input("Enter SONA pool ID: ")

        
        block_order = [1, 2, 3, 4]
        random.shuffle(block_order)
            
        data_filename = P_info["PID"] + "_responses.csv"
        script_directory = os.path.dirname(os.path.abspath(__file__))  #Set the working directory to the folder the Python code is opened from
        
        #set a path to a "data" folder to save data in
        data_folder = os.path.join(script_directory, "data")
        
        # if data folder doesn"t exist, create one
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
            
        #set file name within "data" folder
        data_filepath = os.path.join(data_folder,data_filename)
        
        if os.path.exists(data_filepath):
            print(f"Data for participant {P_info['PID']} already exists. Choose a different participant ID.") ### to avoid re-writing existing data
        
        
        # Group == 1 == high OD
        # Group == 2 == low OD
        # Group == 3 == NH
        # cb == 1 == RENS = GREEN, control = BLUE
        # cb == 2 == RENS = BLUE, control = GREEN
            
        else:
            if int(P_info["PID"]) % 6 == 1:
                group = 1
                cb = 1 
                groupname = "highOD"
            elif int(P_info["PID"]) % 6 == 2:
                group = 2
                cb = 1 
                groupname = "lowOD"
            elif int(P_info["PID"]) % 6 == 3:
                group = 3
                cb = 1 
                groupname = "naturalhistory"
            elif int(P_info["PID"]) % 6 == 4:
                group = 1
                cb = 2 
                groupname = "highOD"
            elif int(P_info["PID"]) % 6 == 5:
                group = 2
                cb = 2 
                groupname = "lowOD"
            elif int(P_info["PID"]) % 6 == 0:
                group = 3
                cb = 2
                groupname = "naturalhistory"
            
            break  # Exit the loop if the participant ID is valid
        
    except KeyboardInterrupt:
        print("Participant info input canceled.")
        break  # Exit the loop if the participant info input is canceled

# get date and time of experiment start
datetime = time.strftime("%Y-%m-%d_%H.%M.%S")

#set stimulus colours according to cb 
stim_colours = {
  "RENS" : cue_colours[cb-1],
  "control": cue_colours[-cb] 
}

stim_colour_names = {
    "RENS" : cue_colour_names[cb-1],
    "control": cue_colour_names[-cb]
}

stim_positions = {
    "RENS" : cue_positions[cb-1],
    "control" : cue_positions[-cb]
}

if ports_live == True:
    pport = parallel.ParallelPort(address=port_address) #Get from device Manager
    pport.setData(0)
    
elif ports_live == None:
    pport = None #Get from device Manager

# set up screen
exp_win = visual.Window(
    size=(1920, 1080), fullscr=True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor="testMonitor", color=[0, 0, 0], colorSpace="rgb1",
    blendMode="avg", useFBO=True,
    units="pix")

# fixation stimulus
fix_stim = visual.TextStim(exp_win,
                            text = "x",
                            color = "white",
                            height = 50,
                            font = "Roboto Mono Medium")


#define waiting function so experiment doesn't freeze as it does with wait()
def wait(time):
    countdown_timer = core.CountdownTimer(time)
    while countdown_timer.getTime() > 0:
        termination_check()
        

#create instruction trials
def instruction_trial(instructions, holdtime=0, spacebar_text=True, key=None):
    visual.TextStim(exp_win, text = instructions, **textStim_arguments).draw()
    exp_win.flip()
    wait(holdtime)
    if key != None:
        termination_check()
        event.waitKeys(keyList=key)
    if spacebar_text == True:
        visual.TextStim(exp_win, text = instructions, **textStim_arguments).draw()
        visual.TextStim(exp_win,
                        text = "\n\nPress spacebar to continue",
                        pos = (0,-400),
                        **textStim_arguments).draw()
        exp_win.flip()
        event.waitKeys(keyList="space")
    exp_win.flip()
    wait(2)
    
# Create functions
    # Save responses to a CSV file
def save_data(data):
    for trial in trial_order:
        trial['datetime'] = datetime
        trial['experimentcode'] = experimentcode
        trial["PID"] = P_info["PID"]
        trial["SONA"] = P_info["SONA"]
        trial["group"] = group
        trial["groupname"] = groupname
        trial["cb"] = cb
        trial['blockorder'] = block_order
        trial["tens_colour"] = stim_colour_names["RENS"]
        trial["control_colour"] = stim_colour_names["control"]
        

    # Extract column names from the keys in the first trial dictionary
    colnames = list(trial_order[0].keys())

    # Open the CSV file for writing
    with open(data_filepath, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=colnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each trial"s data to the CSV file
        for trial in data:
            writer.writerow(trial)
    
def exit_screen(instructions):
    exp_win.flip()
    visual.TextStim(exp_win,
            text = instructions,
            height = text_height,
            color = "white",
            pos = (0,0)).draw()
    exp_win.flip()
    event.waitKeys()
    exp_win.close()
    
def termination_check(): #insert throughout experiment so participants can end at any point.
    keys_pressed = event.getKeys(keyList=["escape"])  # Check for "escape" key during countdown
    if "escape" in keys_pressed:
        if ports_live:
            pport.setData(0) # Set all pins to 0 to shut off context, RENS, shock etc.
        # Save participant information

        save_data(trial_order)
        exit_screen(instructions_text["termination"])
        core.quit()


# Define trials
trial_order = []

# familiarisation trials
num_familiarisation = 10

for i in range(1, num_familiarisation + 1):
    trial = {
        "phase": "familiarisation",
        "blocknum": None,
        "blockname":None,
        "stimulus": None,
        "outcome": None,
        "exp_response": None,
        "pain_response": None,
        "iti" : None
    } 
    trial_order.append(trial)

#### 4 x blocks (4x fixed 12x outcomes with high/low OD)
num_blocks_conditioning = 4
num_blocks_extinction = 4

conditioning_outcome_blocks = {
    "highOD": [
            ["low4", "high", "low3", "low5", "low3", "low5", "high", "low4", "high", "low5", "low4", "low3"],
            ["low5", "low3", "low4", "high", "high", "low3", "low5", "low4", "low3", "high", "low4", "low5"],
            ["low4", "low3", "low5", "high", "low5", "high", "low3", "low4", "low3", "high", "low4", "low5"],
            ["low5", "low4", "high", "low3", "low3", "low5", "high", "low4", "high", "low3", "low4", "low5"]
        ],
    "lowOD": [
            ["high", "high", "low4", "high", "high", "low3", "high", "high", "low5", "high", "high", "high"],
            ["high", "high", "low5", "high", "low4", "high", "high", "high", "low3", "high", "high", "high"],
            ["low3", "high", "high", "high", "high", "low5", "high", "high", "high", "low4", "high", "high"],
            ["high", "high", "low5", "high", "high", "low3", "high", "high", "low4", "high", "high", "high"]
        ],
    "naturalhistory": []
    }

#low heat for every trial in extinction regardless of stimulus
extinction_outcome_block = ['med']*12

#blockname
blockname = []

# Populate naturalhistory by alternating between highOD and lowOD by block number
# cb == 1 starts with highOD, cb == 2 starts with lowOD
for block in range(1, num_blocks_conditioning + 1):
    block_idx = block_order[block - 1]
    if groupname == "naturalhistory":
        if (block + cb) % 2 == 0:  # cb=1: blocks 1,3 are highOD; cb=2: blocks 1,3 are lowOD
            conditioning_outcome_blocks["naturalhistory"].append(conditioning_outcome_blocks["highOD"][block_idx - 1])
            blockname.append(f"highOD_{block_idx}")
        else:
            conditioning_outcome_blocks["naturalhistory"].append(conditioning_outcome_blocks["lowOD"][block_idx - 1])
            blockname.append(f"lowOD_{block_idx}")
    else:
        blockname.append(f"{groupname}_{block_idx}")

# calibration trials
num_calibration = 4
calibration_outcome_block = ['med'] * num_calibration

for i in range(1, num_calibration + 1):
    trial = {
        "phase": "calibration",
        "blocknum": None,
        "blockname": None,
        "stimulus": None,
        "outcome": calibration_outcome_block[i - 1],
        "exp_response": None,
        "pain_response": None,
        "iti": None
    }
    trial_order.append(trial)


### create list of trials based on trial_block order, iterating through stimulus + outcome blocks in parallel
for block in range(1, num_blocks_conditioning + 1):
    # Create trials for each outcome in this block
    for outcome in conditioning_outcome_blocks[groupname][block_order[block - 1] - 1]:
        trial = {
            "phase": "conditioning",
            "blocknum": block,
            "blockname": blockname[block - 1],
            "stimulus": None,
            "outcome": outcome,
            "exp_response": None,
            "pain_response": None,
            "iti": None
        }
        trial_order.append(trial)         
                    
#create extinction trials, all outcomes same regardless of condition (low heat)
for block in range(num_blocks_conditioning + 1, num_blocks_conditioning + num_blocks_extinction + 1):
    # All extinction trials use medium heat regardless of group
    for outcome in extinction_outcome_block:
        trial = {
            "phase": "extinction",
            "blocknum": block,
            "blockname":None,
            "stimulus": None,
            "outcome": outcome,
            "exp_response": None,
            "pain_response": None,
            "iti": None
        }
        trial_order.append(trial)


# # Assign trial numbers
for trialnum, trial in enumerate(trial_order, start=1):
    trial["trialnum"] = trialnum
    
save_data(trial_order)
    
# # text stimuli
instructions_text = {
    "welcome": "Welcome to the experiment! Please read the following instructions carefully.", 
    
    "familiarisation_1": ("Firstly, you will be familiarised with the thermal stimuli. This familiarisation procedure is necessary to ensure that participants are able to tolerate "
    "the heat pain delivered in this experiment. The thermal stimulus is delivered through the thermode attached to your forearm, which delivers heat pain by selectively stimulating pain fibres.\n\n"
    "As the density of pain fibres can vary between individuals, the pain experienced and the efficacy of RENS for participants who will receive RENS stimulation can also vary. "
    "As such, this familiarisation procedure will demonstrate the range of how painful the thermal stimulus could be for any participant."),
    
    "familiarisation_2": ("In the familiarisation procedure, you will experience the thermal stimuli at a range of intensities. The machine will start at a low intensity, and incrementally increase each level. "
    "After receiving each thermal stimulus, please give a pain rating for that level of heat by clicking and dragging your mouse on a scale from 1 to 10 where 1 is not painful and 10 is very painful. "
    "The familiarisation procedure will take you through 10 increasing levels of heat intensities. \n\n Although the higher levels of heat intensities may be more uncomfortable or painful, please note that "
    "the maximum level of heat is safe and unlikely to cause you any actual harm. If, however, you find the thermal stimuli intolerable at any stage, please let the experimenter know and we will terminate the experiment immediately. "
    "This procedure will proceed at your pace, so feel free to take your time to rest between heat levels."),
        
    "familiarisation_finish": "Thank you for completing the familiarisation protocol. we will now proceed to the next phase of the experiment",

    "blockrest" : "This is a rest interval. Please wait for the experimenter to adjust the thermode BEFORE pressing SPACEBAR.", 
    
    "blockresume" : "Feel free to take as much as rest as necessary before starting the next block.",
    
    "end" : "This concludes the experiment. Please ask the experimenter to help remove the devices.",
    
    "termination" : "The experiment has been terminated. Please ask the experimenter to help remove the devices.",

    "RENS_introduction" : "This experiment aims to investigate the effects of Transcutaneous Electrical Nerve Stimulation (RENS) on heat pain sensitivity. "
    "RENS is designed to increase pain sensitivity by enhancing the conductivity of pain signals being sent to your brain. Clinically this is used to enhance pain sensitivity in medical conditions where pain sensitivity is dampened. "
    "In the absence of medical conditions, RENS significantly amplifies pain signals, meaning stimulations will be more painful when the RENS device is active. Although the RENS itself is not painful, you will feel a small sensation when it is turned on. \n\n"
    "In this study you and another participant will receive a series of heat pain stimulations, and some heat pain stimulations will also be accompanied with RENS stimulation.",
    
    "conditioning" : "You will now receive a series of thermal stimuli and rate the intensity of each thermal stimulus. "
        "The thermal stimuli will be signaled by a 10 second countdown and the heat will be delivered at the end of the countdown when an X appears. If chosen on a trial, RENS will activate for that particular trial. "
        "During the countdown, you will also be asked to rate how painful you expect the heat to be. After each trial there will be a brief interval to allow you to rest between thermal stimuli. "
        "You will also receive a brief rest between blocks of trials where the experimenter will move the thermode to another location on your arm. \n\n"
        "Please wait for the experimenter now to prepare the thermal stimuli.",

    "calibration" : "You will first begin with four calibration trials to assess your baseline heat tolerance. No RENS will be delivered for these trials",

    "calibration_finish" : "Calibration finished. \n\n" +
                    "Please wait for the experimenter now to prepare the next set of thermal stimuli.",

    "blockname_text" : "EXPERIMENTER ONLY\n" + "\n".join([f"Block {i+1}: {name}" for i, name in enumerate(blockname)])
    
}

response_instructions = {
    "pain": "How painful was the heat?",
    "expectancy": "How painful do you expect the thermal stimulus to be?",
    "SM": "The demonstrator made the following response on this trial",
    "familiarisation": "When you are ready to receive the thermal stimulus, press the SPACEBAR to activate the thermal stimulus. ",
    "choice": "Please choose whether you want to receive RENS on this trial."
    }

trial_text = {
     None : visual.TextStim(exp_win,
            text=None,
            height = text_height,
            pos = rating_text_pos
            ),
     "pain": visual.TextStim(exp_win,
            text=response_instructions["pain"],
            height = text_height,
            pos = rating_text_pos
            ),
     "expectancy": visual.TextStim(exp_win,
            text=response_instructions["expectancy"],
            height = text_height,
            pos = rating_text_pos
            )
}

# Define button_text and buttons dictionaries
button_text = {
        "RENS": visual.TextStim(exp_win,
                    text="RENS",
                    color="white",
                    height=25,
                    pos=(400, -300),
                    wrapWidth=300
                    ),
        "control": visual.TextStim(exp_win,
                    text="No RENS",
                    color="white",
                    height=25,
                    pos=(-400, -300),
                    wrapWidth=300
                    ),
}
buttons = {
        "RENS": visual.Rect(exp_win,
                    width=300,
                    height=80,
                    fillColor="black",
                    lineColor="white",
                    pos=(400, -300)),
        "control": visual.Rect(exp_win,
                    width=300,
                    height=80,
                    fillColor="black",
                    lineColor="white",
                    pos=(-400, -300)),
}

# #Test questions
rating_stim = { "familiarisation": visual.Slider(exp_win,
                                    pos = rating_scale_pos,
                                    ticks=[0,50,100],
                                    labels=(1,5,10),
                                    granularity=0.1,
                                    size=(600,60),
                                    style=["rating"],
                                    autoLog = False,
                                    labelHeight = 30),
               "pain": visual.Slider(exp_win,
                                    pos = rating_scale_pos,
                                    ticks=[0,100],
                                    labels=("Not painful","Very painful"),
                                    granularity=0.1,
                                    size=(600,60),
                                    style=["rating"],
                                    autoLog = False,
                                    labelHeight = 30),
                "expectancy": visual.Slider(exp_win,
                                    pos = rating_scale_pos,
                                    ticks=[0,100],
                                    labels=("Not painful","Very painful"),
                                    granularity=0.1,
                                    size=(600,60),
                                    style=["rating"],
                                    autoLog = False,
                                    labelHeight = 30)}


rating_stim["familiarisation"].marker.size = (30,30)
rating_stim["familiarisation"].marker.color = "yellow"
rating_stim["familiarisation"].validArea.size = (660,100)

rating_stim["pain"].marker.size = (30,30)
rating_stim["pain"].marker.color = "yellow"
rating_stim["pain"].validArea.size = (660,100)

rating_stim["expectancy"].marker.size = (30,30)
rating_stim["expectancy"].marker.color = "yellow"
rating_stim["expectancy"].validArea.size = (660,100)

pain_rating = rating_stim["pain"]
exp_rating = rating_stim["expectancy"]
fam_rating = rating_stim["familiarisation"]
                                
# pre-draw countdown stimuli (numbers 10-1)
countdown_text = {}
for i in range(0,11):
    countdown_text[str(i)] = visual.TextStim(exp_win, 
                            color="white", 
                            height = 50,
                            text=str(i))

# visual cues for RENS/control trials
cue_stims = {"RENS" : visual.Rect(exp_win,
                        lineColor = stim_colours["RENS"],
                        fillColor = stim_colours["RENS"],
                        width = cue_width,
                        height = cue_width,
                        pos = stim_positions["RENS"],
                        autoLog = False),
             "control" : visual.Rect(exp_win,
                        lineColor = stim_colours["control"],
                        fillColor = stim_colours["control"],
                        width = cue_width,
                        height = cue_width,
                        pos = stim_positions["control"],
                        autoLog = False)
             }

# Define button_text dictionaries
#### Make trial functions
def show_fam_trial(current_trial):
    termination_check()
    # Wait for participant to ready up for shock
    visual.TextStim(exp_win,
        text=response_instructions["familiarisation"],
        height = 35,
        pos = (0,0),
        wrapWidth= 800
        ).draw()
    exp_win.flip()
    event.waitKeys(keyList = ["space"])
    
    # show fixation stimulus + deliver shock
    if pport != None:
        pport.setData(0)

    fix_stim.draw()
    exp_win.flip()
    
    if pport != None:
        pport.setData(pain_trig+eda_trig)
        core.wait(port_buffer_duration)
        pport.setData(0)
    
    # Get pain rating
    while fam_rating.getRating() is None: # while mouse unclicked
        termination_check()
        trial_text["pain"].draw()
        fam_rating.draw()
        exp_win.flip()
         
    pain_response_end_time = core.getTime() + response_hold_duration # amount of time for participants to adjust slider after making a response
    
    while core.getTime() < pain_response_end_time:
        termination_check()
        trial_text["pain"].draw()
        fam_rating.draw()
        exp_win.flip()

    current_trial["pain_response"] = fam_rating.getRating()
    fam_rating.reset()
    
    exp_win.flip()
    core.wait(familiarisation_iti)
    
def show_trial(current_trial):
    if pport != None:
        pport.setData(0)
        
    exp_win.flip()

        #If RENS trial, ask for choice:
    
    for button_name in button_text:
        buttons[button_name].draw()
        button_text[button_name].draw()

        
    visual.TextStim(exp_win,
            text=response_instructions["choice"],
            height = 35,
            pos = (0,0),
            ).draw()
        
    exp_win.flip()

    choice_finish = False
    mouse = event.Mouse()
   

    while choice_finish == False:
        termination_check()
        for button_name, button_rect in buttons.items():
            if mouse.isPressedIn(button_rect):
                current_trial["stimulus"] = button_name
                choice_finish = True

    
    # Start countdown to shock
    
    # Make a count-down screen
    countdown_timer = core.CountdownTimer(10)  # Set the initial countdown time to 10 seconds
  
    while countdown_timer.getTime() > 8:
        termination_check()
        countdown_text[str(int(math.ceil(countdown_timer.getTime())))].draw()
        exp_win.flip()
        
    while countdown_timer.getTime() < 8 and countdown_timer.getTime() > 7: #turn on RENS at 8 seconds if chosen
        termination_check()
        if pport != None:
            pport.setData(tens_trig[current_trial["stimulus"]])
        countdown_text[str(int(math.ceil(countdown_timer.getTime())))].draw()
        exp_win.flip()

    while countdown_timer.getTime() < 7 and countdown_timer.getTime() > 0: #ask for expectancy at 7 seconds
        termination_check()
        if pport != None:
            pport.setData(tens_trig[current_trial["stimulus"]])
        countdown_text[str(int(math.ceil(countdown_timer.getTime())))].draw()
        
        # Ask for expectancy rating
        trial_text["expectancy"].draw() 
        exp_rating.draw()
        exp_win.flip()    

    current_trial["exp_response"] = exp_rating.getRating() #saves the expectancy response for that trial
    exp_rating.reset() #resets the expectancy slider for subsequent trials
        
    # deliver shock
    if pport != None:
        pport.setData(0)
    fix_stim.draw()
    exp_win.flip()
    
    if pport != None:
        pport.setData(pain_trig[current_trial["outcome"]])
        
    wait(port_buffer_duration)

    if pport != None:
        pport.setData(0)

    # Get pain rating
    while pain_rating.getRating() is None: # while mouse unclicked
        termination_check()
        pain_rating.draw()
        trial_text["pain"].draw()
        exp_win.flip()
            
            
    pain_response_end_time = core.getTime() + response_hold_duration # amount of time for participants to adjust slider after making a response
    
    while core.getTime() < pain_response_end_time:
        termination_check()
        trial_text["pain"].draw()
        pain_rating.draw()
        exp_win.flip()
        
    current_trial["pain_response"] = pain_rating.getRating()
    pain_rating.reset()

    exp_win.flip()
    
    wait(iti)

exp_finish = None        
lastblocknum = None

# # Create second window on second screen to display blockname info
# info_win = visual.Window(
#     size=(600, 400), fullscr=False, screen=1,
#     allowGUI=True, allowStencil=False,
#     monitor="testMonitor", color=[0, 0, 0], colorSpace="rgb1",
#     blendMode="avg", useFBO=True,
#     units="pix")

# # Display blockname info
# blockname_text = "Block Order:\n" + "\n".join([f"Block {i+1}: {name}" for i, name in enumerate(blockname)])
# visual.TextStim(info_win, text=blockname_text, height=30, color="white", wrapWidth=550).draw()
# info_win.flip()

# Run experiment
while not exp_finish:
    exp_win.mouseVisible = True
    # termination_check()
    
    # # # ### introduce RENS and run familiarisation procedure
    instruction_trial(instructions=instructions_text["blockname_text"],spacebar_text=None,key="return")
    # instruction_trial(instructions_text["welcome"],3)
    # instruction_trial(instructions_text["RENS_introduction"],6)
    # instruction_trial(instructions_text["familiarisation_1"],10)
    # instruction_trial(instructions_text["familiarisation_2"],10)
    
    # for trial in list(filter(lambda trial: trial['phase'] == "familiarisation", trial_order)):
    #     show_fam_trial(trial)
    # instruction_trial(instructions_text["familiarisation_finish"],2)

    # instruction_trial(instructions_text["conditioning"],10)

    instruction_trial(instructions_text["calibration"],,spacebar_text=None,key="return")
    for trial in list(filter(lambda trial: trial['phase'] == "calibration", trial_order)):
        show_fam_trial(trial)
    
    for trial in list(filter(lambda trial: trial['phase'] == "conditioning", trial_order)):
        current_blocknum = trial['blocknum']
        if lastblocknum is not None and current_blocknum != lastblocknum:
            instruction_trial(instructions_text["blockrest"],10)
        show_trial(trial)
        lastblocknum = current_blocknum

    # if pport != None:
    #     pport.setData(0)
        
    # save trial data
    save_data(trial_order)
    # exit_screen(instructions_text["end"])
    
    exp_finish = True
    
exp_win.close()