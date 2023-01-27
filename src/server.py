
import os, random, string

from flask import Flask, request

app = Flask(__name__)


# Change to reflect the list of problems for testing
REFERENCE_LOC = 'data/reference'
TEMP_LOC = '/tmp'


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# endpoint that takes in a domain and problem file as strings in a json post request
# testing string:  curl -X POST -H "Content-Type: application/json" -d '{"domain": "domain_string", "problem": "problem_string"}' http://localhost:5000/align/2/
@app.route("/align/<int:prob>/", methods=['POST'])
def align(prob):
    print(request)
    print(request.form)

    dstring = request.json['domain']
    pstring = request.json['problem']
    rn = rand_hash()
    dfile = f'{TEMP_LOC}/domain.{rn}.pddl'
    pfile = f'{TEMP_LOC}/problem.{rn}.pddl'
    with open(dfile, 'w') as f:
        f.write(dstring)
    with open(pfile, 'w') as f:
        f.write(pstring)
    print(dfile, pfile)
    return check_alignment(prob, dfile, pfile)



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
