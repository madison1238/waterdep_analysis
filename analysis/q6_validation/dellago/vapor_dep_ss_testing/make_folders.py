import os, shutil, re

ss_ratios = [100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000, 500000]
temps =  [180,190,200,210,220,230,240]

for ss in ss_ratios:
    ss_dir = f"sims/ss_{ss}"
    os.makedirs(ss_dir, exist_ok=True)
    for temp in temps:
        if (ss == 100000) and (temp <= 210):
            continue
        if (ss== 500000) and (temp < 200):
            continue
        temp_dir = f"{ss_dir}/temp_{temp}"
        os.makedirs(temp_dir, exist_ok=True)

        shutil.copytree('base/*', temp_dir, dirs_exist_ok=True)
        controller_script = f"{temp_dir}/controller.py"
        sb_controller = f"{temp_dir}/sb.controller"

        #update controller
        with open(controller_script, 'r') as f:
            controller_text = f.read()
        controller_text = re.sub(r"\bSTART_TEMP1\b", str(temp), controller_text)
        controller_text = re.sub(r"\bEND_TEMP1\b", str(temp), controller_text)
        controller_text = re.sub(r"\bTARGET_SATURATION1\b", str(ss), controller_text)
        with open(controller_script, 'w') as f:
            f.write(controller_text)

        #update controller sbacth
        job_name = f"t_{temp}_ss_{ss}_cont"
        with open(sb_controller, 'r') as f:
            sb_controller_text = f.read()
        controller_text = re.sub(r"\bJOB_NAME1\b", str(temp), sb_controller_text)
        with open(sb_controller, 'w') as f:
            f.write(sb_controller_text)
        

