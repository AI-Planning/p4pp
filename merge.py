
from tarski.syntax import land, CompoundFormula
from tarski.syntax.formulas import neg, is_neg
import tarski.fstrips as fs
from tarski.io import fstrips as iofs, PDDLReader

import sys, os

USAGE = """
    Usage: python3 merge.py <domain1> <problem1> <domain2> <problem2> <out-domain> <out-problem>
"""

def confirm_same(dom1, dom2, checking):
    if dom1 != dom2:
        print(f"The {checking} are different for each domain")
        if dom1 - dom2:
            print("  In domain 1 but not 2: ", dom1 - dom2)
        if dom2 - dom1:
            print("  In domain 2 but not 1: ", dom2 - dom1)
        sys.exit(1)

def main(domain1_name, problem1_name, domain2_name, problem2_name, merged_domain, merged_problem):
    # ======================== Algorithm ========================
    #
    # 1. Parse each domain with tarski to get the fluent names.
    # 2. Forget tarski for a sec, and create new domain/problem files for each of them. Just do
    #  a string replace for every fluent name to prepend domain1_ or domain2_). If you make sure
    #  you do this with (<fluent_name> and not just <fluent name>, then I can't think of any reason
    #  it would fail. An example in python: new_pddl_str = old_pddl_str.replace('(on', '(domain1_on')
    # 3. Parse both domains again -- fluents should all be set and already renamed.
    # 4. Compute the new (fail_<act>) actions.
    # 5. If possible, augment one of them by adding everything from the other. Objects/types/action
    #  names should be the same, so you're just adding to the list of predicates, action preconditions,
    #  action effects, initial state, and goal state.
    # 6. If this doesn't work, you'd need to create a new domain/problem from scratch.
    # 7. Add the (failed) fluent and the (fail_<act>) actions.
    # 8. Write the newly merged domain/problem files.
    # 9. Modify the goal to just achieve (failed) and write that problem file too.
    #
    # Note: We will add all of the domain, problem changes to parse1
    # example of terminal line python3 merge.py domain.pddl problem.pddl domain2.pddl problem2.pddl dom3.pddl prob3.pddl


    # step 1: Parse each domain with tarski to get the fluent names
    domain1_fluent_names = return_fluent_names(domain1_name, problem1_name, domain2_name, problem2_name)
    domain2_fluent_names = return_fluent_names(domain2_name, problem2_name, domain2_name, problem2_name)

    # step 2: Create new .pddl files using string replacements -> use fluent names from above to identify them
    # 2a: prepend to domain files
    prepend_names(domain1_name, domain1_fluent_names, 1, "domain")
    prepend_names(domain2_name, domain2_fluent_names, 2, "domain")

    # 2b: prepend to problem files
    prepend_names(problem1_name, domain1_fluent_names, 1, "problem")
    prepend_names(problem2_name, domain2_fluent_names, 2, "problem")

    # step 3: Parse the new files using tarski
    parse1 = parse_pddl('updated_domain1.pddl', 'updated_problem1.pddl')
    parse2 = parse_pddl('updated_domain2.pddl', 'updated_problem2.pddl')
    os.system('rm updated_domain*.pddl updated_problem*.pddl')

    # raise error if the name of the domains are not the same
    assert parse1.domain_name == parse2.domain_name, "Names of the domains are differnt"
    assert parse1.name == parse2.name, "Names of the problems are differnt"

    # step 4: Compute the new (fail_<act>) actions
    lang1 = parse1.language
    lang2 = parse2.language

    # check if the constants are the same for each domain
    dom1_constants = set([c.name for c in lang1.constants()])
    dom2_constants = set([c.name for c in lang2.constants()])
    confirm_same(dom1_constants, dom2_constants, "constants")

    # raise error if the types are not the same
    dom1_types = set([ty.name for ty in lang1.sorts])
    dom2_types = set([ty.name for ty in lang2.sorts])
    confirm_same(dom1_types, dom2_types, "types")

    # step 5a: merge the second domain to the first domain
    # get the predicates for domain 2
    domain2_predicates = lang2.predicates

    for elem in domain2_predicates:
        curr_name = str(elem.name)
        if "=" not in curr_name:
            merged_predicate = lang1.predicate(*(elem.signature))

    # add the fail predicate
    failed = lang1.predicate('failed')

    # get the list of actions in each domain
    domain1_actions = list(parse1.actions)
    domain2_actions = list(parse2.actions)

    # raise error if the number of actions are different in each domain
    confirm_same(domain1_actions, domain2_actions, "actions")

    # # for each set of domain actions get the required parameters, preconditions, effects - map domain2 to domain 1, merge preconditions
    # #this is to make fail_turnon1, fail_turnoff1
    for action in domain1_actions:
        name = 'fail_' + action + '1'
        action_domain2 = parse1.get_action(action)

        # get fail action parameters
        domain_parameters = action_domain2.parameters

        # get preconditions of both domains
        domain1_precond = action_domain2.precondition
        domain2_precond = parse2.get_action(action).precondition

        #this creates the merged preconds for fail actions for domain1
        merged_precs = []
        if is_neg(domain2_precond): #check if precond is already negated, if yes, get subformulas to have positive version
            if isinstance(domain2_precond, CompoundFormula):
                merged_precs.extend(domain2_precond.subformulas)
        else: #otherwise negate it
            merged_precs.append(neg(domain2_precond))
        merged_precs.append(domain1_precond)
        final_prec = land(*merged_precs) # This makes land(*[A,B,C]) actually be land(A,B,C)

        # add the effect 'failed' and (and) it
        # def action(self, name, parameters, precondition, effects, cost=None)
        pd = parse1.action(name, domain_parameters,
                    precondition=final_prec,
                    effects=[fs.AddEffect(failed())])


    # # # for each set of domain actions get the required parameters, preconditions, effects - map domain1 to domain2, merge preconditions
    # # #this is to make fail_turnon2, fail_turnoff2
    for action in domain2_actions:
        name = 'fail_' + action + '2'

        action_domain2 = parse2.get_action(action)

        # get fail action parameters
        domain_parameters = action_domain2.parameters

        # get preconditions of both domains
        domain1_precond = parse1.get_action(action).precondition
        domain2_precond = action_domain2.precondition

        #this creates the merged preconds for fail actions for domain2
        merged_precs = []
        if is_neg(domain1_precond):
            if isinstance(domain1_precond, CompoundFormula):
                merged_precs.extend(domain1_precond.subformulas)
        else:
            merged_precs.append(neg(domain1_precond))
        merged_precs.append(domain2_precond)

        final_prec = land(*merged_precs) # This makes land(*[A,B,C]) actually be land(A,B,C)

        # make effect 'failed'
        pd = parse1.action(name, domain_parameters,
                    precondition=final_prec,
                    effects=[fs.AddEffect(failed())])

    # # merge the non fail actions from domain2 onto domain1
    for action in domain2_actions:
        name = action

        # get the actions from domain2
        action_domain2 = parse2.get_action(action)
        action_domain1 = parse1.get_action(action)

        # get fail action parameters
        domain_parameters = action_domain2.parameters

        # get preconditions of both domains
        domain1_precond = action_domain1.precondition
        domain2_precond = action_domain2.precondition

        # merge the preconditions
        merged_precs = []
        merged_precs.append(domain1_precond)
        merged_precs.append(domain2_precond)
        final_prec = land(*merged_precs)

        # get the effects of both domains and merge
        domain1_effects = action_domain1.effects
        domain2_effects = action_domain2.effects

        for effect in domain2_effects:
            domain1_effects.append(effect)

        # merge action
        action_domain1.parameters = domain_parameters
        action_domain1.precondition = final_prec
        action_domain1.effects = domain1_effects

    # merge the init
    # get domain1 and domain2 inital states and add them to the merged_initial states

    for atom in parse2.init.as_atoms():
        pred = lang1.get_predicate(atom.predicate.name)
        args = [lang1.get(o.symbol) for o in atom.subterms]
        parse1.init.add(pred(*args))


    # merge final
    parse1.goal = (failed())

    writer = iofs.FstripsWriter(parse1)
    writer.write(merged_domain, merged_problem)

    # fix requirements to add in negative precondition requirement
    with open(merged_domain, "r") as file_read:
        file_content = file_read.read()

    file_content = file_content.replace("(:requirements ", "(:requirements :negative-preconditions ")

    with open(merged_domain, "w") as updated_domain:
        updated_domain.write(file_content)


def return_fluent_names(dname, pname, domain2_name, problem2_name):
    temp_parse = parse_pddl(dname, pname)
    temp_lang = temp_parse.language
    listPredicates = temp_lang.predicates

    domain1_fluent_names = []

    for elem in listPredicates:
        curr_name = str(elem.name)
        if "=" not in curr_name:
            domain1_fluent_names.append(curr_name)

    temp_parse = parse_pddl(domain2_name, problem2_name)
    temp_lang = temp_parse.language
    listPredicates = temp_lang.predicates

    return domain1_fluent_names


def prepend_names(file_name, fluent_names, number, type):
    with open(file_name, "r") as file_read:
        file_content = file_read.read()

    for pred in fluent_names:
        tmp_name = "(" + pred
        rpl_name = "(domain" + str(number) + "_" + pred
        file_content = file_content.replace(tmp_name, rpl_name)

    with open("updated_" + type + str(number) +".pddl", "w") as updated_domain:
        updated_domain.write(file_content)


def parse_pddl(dname, pname):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain(dname)
    problem = reader.parse_instance(pname)
    return problem


if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(USAGE)
        exit(1)

    domain1_name = sys.argv[1]
    problem1_name = sys.argv[2]
    domain2_name = sys.argv[3]
    problem2_name = sys.argv[4]
    merged_domain = sys.argv[5]
    merged_problem = sys.argv[6]

    main(domain1_name, problem1_name, domain2_name, problem2_name, merged_domain, merged_problem)


