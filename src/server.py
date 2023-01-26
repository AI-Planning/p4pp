
import os, random, string

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Change to reflect the list of problems for testing
REFERENCE_LOC = 'data/reference'
TEMP_LOC = '/tmp'

def rand_hash():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

def check_alignment(prob, dfile, pfile):
    rn = rand_hash()
    mdfile = f'{TEMP_LOC}/domain.{rn}.merged.pddl'
    mpfile = f'{TEMP_LOC}/problem.{rn}.merged.pddl'
    planfile = f'{TEMP_LOC}/plan.{rn}.merged'
    planoutput = f'{TEMP_LOC}/plan.{rn}.merged.log'
    os.system(f'python3 merge.py {REFERENCE_LOC}/domain.pddl {REFERENCE_LOC}/{prob} {dfile} {pfile} {mdfile} {mpfile}')
    os.system(f'./plan.sh {planfile} {mdfile} {mpfile}')

    # check file for failure message
    with open(f'{planoutput}', 'r') as f:
        mtext = f.read()
        align = 'Search stopped without finding a solution.' in mtext
    if not (align or os.path.isfile(f'{planfile}')):
        print(f'Warning: Alignment failed')

    plan = None
    if os.path.isfile(f'{planfile}'):
        with open(f'{planfile}', 'r') as f:
            plan = f.read()
    return (align, plan)
