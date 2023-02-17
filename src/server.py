
import os, random, string

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Change to reflect the list of problems for testing
REFERENCE_LOC = 'data/reference'
TEMP_LOC = '/tmp'

PROBLEMS = ['p01', 'p02', 'p03']

# serve plugin.js from the local file contents
@app.route("/plugin.js")
def plugin():
    with open('plugin.js', 'r') as f:
        contents = f.read()
    # Make sure it has javascript mime type
    return (contents, 200, {'Content-Type': 'application/javascript', 'Access-Control-Allow-Origin': '*'})


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# endpoint that takes in a domain and problem file as strings in a json post request
# testing string:  curl -X POST -H "Content-Type: application/json" --data @data2.json http://localhost:80/align/p01/
@app.route("/align/<prob>/", methods=['POST'])
def align(prob):
    dstring = request.json['domain']
    pstring = request.json['problem']
    rn = rand_hash()
    dfile = f'{TEMP_LOC}/domain.{rn}.pddl'
    pfile = f'{TEMP_LOC}/problem.{rn}.pddl'
    with open(dfile, 'w') as f:
        f.write(dstring)
    with open(pfile, 'w') as f:
        f.write(pstring)
    try:
        (align, plan, error) =  check_alignment(prob, dfile, pfile)
        assert align or plan or error
        if plan:
            steps = plan.split('\n')
            assert '' == steps[-1]
            steps = steps[:-2]
            assert '(fail' in steps[-1]
            failed_action_name = steps[-1].split(' ')[0].split('fail_')[1]
            direction = failed_action_name[-1]
            failed_action = f'({failed_action_name[:-1]}'+steps[-1].split(f'fail_{failed_action_name}')[1]
            steps = steps[:-1]
            message =  'After executing the following action sequence...\n\n'
            message += '\n'.join(steps)
            message += '\n\n...the following action is executable in '
            if direction == '1':
                message += 'the solution, but not your model:\n\n'
            else:
                assert direction == '2'
                message += 'your model, but not the solution:\n\n'
            message += failed_action + '\n\n'
        elif error:
            message = "There appears to be an error with the merge:\n\n"
            message += error.strip().split('\n')[-1]
        else:
            message = "Everything looks good!"
        resp = {'align': align, 'result': message, 'status': 'success'}
    except Exception as e:
        print(e)
        resp = {'align': False, 'error': str(e), 'status': 'error'}
    return (resp, 200, {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'})


# json endpoint to return the list of problems
@app.route("/problems/")
def problems():
    return {'problems': PROBLEMS}


def rand_hash():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

def check_alignment(prob, dfile, pfile):
    rn = rand_hash()
    mdfile = f'{TEMP_LOC}/domain.{rn}.merged.pddl'
    mpfile = f'{TEMP_LOC}/problem.{rn}.merged.pddl'
    planfile = f'{TEMP_LOC}/plan.{rn}.merged'
    planoutput = f'{TEMP_LOC}/plan.{rn}.merged.log'
    mergeoutput = f'{TEMP_LOC}/merge.{rn}.merged.log'
    os.system(f'python3 merge.py {REFERENCE_LOC}/domain.pddl {REFERENCE_LOC}/{prob}.pddl {dfile} {pfile} {mdfile} {mpfile} > {mergeoutput} 2>&1')
    os.system(f'./plan.sh {planfile} {mdfile} {mpfile} > {planoutput} 2>&1')

    # check file for failure message
    error = None
    with open(f'{planoutput}', 'r') as f:
        mtext = f.read()
        align = 'Search stopped without finding a solution.' in mtext
    if not (align or os.path.isfile(f'{planfile}')):
        print(f'Warning: Alignment failed')
        with open(f'{mergeoutput}', 'r') as f:
            error = f.read()

    plan = None
    if os.path.isfile(f'{planfile}'):
        with open(f'{planfile}', 'r') as f:
            plan = f.read()
    return (align, plan, error)
