import json
import random
from pathlib import Path

OUTPUT_PATH = Path("dataset/raw/examples.jsonl")
RANDOM_SEED = 4242564

def get_article(word):
    return "an" if word[0].lower() in "aeiou" else "a"

def pluralise(word):
    irregular = {
        "person": "people",
        "child": "children",
        "bus": "buses",
    }

    if word in irregular:
        return irregular[word]

    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"

    if word.endswith("y") and len(word) > 1 and word[-2].lower() not in "aeiou":
        return word[:-1] + "ies"

    return word + "s"

def create_example(
    example_id,
    level,
    category,
    natural_language,
    prolog,
    template_group,
    nl_template=None,
    query=None,
    expected_result=None,
):
    example = {
        "id": example_id,
        "level": level,
        "category": category,
        "natural_language": natural_language,
        "prolog": prolog,
        "template_group": template_group,
    }

    if nl_template is not None:
        example["nl_template"] = nl_template

    if query is not None:
        example["query"] = query

    if expected_result is not None:
        example["expected_result"] = expected_result

    return example

def generate_facts():
    names = [
        "ash", "brook", "ciel", "dio", "edward", "faust", "gary",
        "haku", "irina", "joseph", "kai", "luffy", "mary", "nathan",
        "olivia", "petra", "quistis", "ray", "sinbad", "tanya", "usagi",
        "violet", "wendy", "xeno", "yuri", "zelda",
    ]

    unary_predicates = [
        "cat", "dog", "bird", "student", "teacher", "scientist",
        "musician", "doctor", "athlete", "artist", "human", "engineer",
        "programmer", "researcher", "writer", "chef", "pilot", "farmer",
        "dancer", "singer", "warrior", "scholar", "traveller", "merchant",
        "detective", "nurse",
    ]

    unary_templates = [
        ("unary_is", "{name} is {article} {predicate}."),
        ("unary_classified_as", "{name} is classified as {article} {predicate}."),
        ("unary_known_as", "{name} is known to be {article} {predicate}."),
        ("unary_category", "{name} belongs to the category of {predicate}."),
    ]

    binary_templates = {
        "likes": [
            ("binary_direct", "{first} likes {second}."),
            ("binary_paraphrase", "{first} is fond of {second}."),
        ],
        "knows": [
            ("binary_direct", "{first} knows {second}."),
            ("binary_paraphrase", "{first} is acquainted with {second}."),
        ],
        "helps": [
            ("binary_direct", "{first} helps {second}."),
            ("binary_paraphrase", "{first} gives assistance to {second}."),
        ],
        "follows": [
            ("binary_direct", "{first} follows {second}."),
            ("binary_paraphrase", "{first} is following {second}."),
        ],
        "visits": [
            ("binary_direct", "{first} visits {second}."),
            ("binary_paraphrase", "{first} goes to visit {second}."),
        ],
        "trusts": [
            ("binary_direct", "{first} trusts {second}."),
            ("binary_paraphrase", "{first} has trust in {second}."),
        ],
        "admires": [
            ("binary_direct", "{first} admires {second}."),
            ("binary_paraphrase", "{first} looks up to {second}."),
        ],
        "teaches": [
            ("binary_direct", "{first} teaches {second}."),
            ("binary_paraphrase", "{first} provides teaching to {second}."),
        ],
        "supports": [
            ("binary_direct", "{first} supports {second}."),
            ("binary_paraphrase", "{first} gives support to {second}."),
        ],
        "calls": [
            ("binary_direct", "{first} calls {second}."),
            ("binary_paraphrase", "{first} contacts {second} by phone."),
        ],
    }

    examples = []

    unary_combinations = [
        (name, predicate)
        for name in names
        for predicate in unary_predicates
    ]
    random.shuffle(unary_combinations)

    for example_number, (name, predicate) in enumerate(
        unary_combinations[:350],
        start=1,
    ):
        template_name, template = random.choice(unary_templates)

        natural_language = template.format(
            name=name.capitalize(),
            predicate=predicate,
            article=get_article(predicate),
        )

        examples.append(
            create_example(
                example_id=f"fact_{example_number:04d}",
                level=1,
                category="fact",
                natural_language=natural_language,
                prolog=f"{predicate}({name}).",
                template_group=f"unary_{predicate}",
                nl_template=template_name,
            )
        )

    binary_combinations = [
        (first, second, predicate)
        for first in names
        for second in names
        for predicate in binary_templates
        if first != second
    ]
    random.shuffle(binary_combinations)

    for example_number, (first, second, predicate) in enumerate(
        binary_combinations[:150],
        start=351,
    ):
        template_name, template = random.choice(binary_templates[predicate])

        natural_language = template.format(
            first=first.capitalize(),
            second=second.capitalize(),
        )

        examples.append(
            create_example(
                example_id=f"fact_{example_number:04d}",
                level=1,
                category="fact",
                natural_language=natural_language,
                prolog=f"{predicate}({first}, {second}).",
                template_group=f"binary_{predicate}",
                nl_template=template_name,
            )
        )

    return examples

def generate_simple_rules():
    unary_rule_pairs = [
        ("cat", "animal"),
        ("dog", "animal"),
        ("bird", "animal"),
        ("fish", "animal"),
        ("student", "learner"),
        ("teacher", "educator"),
        ("doctor", "professional"),
        ("scientist", "researcher"),
        ("musician", "artist"),
        ("athlete", "competitor"),
        ("employee", "worker"),
        ("programmer", "technologist"),
        ("engineer", "professional"),
        ("painter", "artist"),
        ("runner", "athlete"),
        ("professor", "teacher"),
        ("undergraduate", "student"),
        ("surgeon", "doctor"),
        ("nurse", "professional"),
        ("chef", "worker"),
        ("pilot", "professional"),
        ("farmer", "worker"),
        ("dancer", "performer"),
        ("singer", "performer"),
        ("writer", "artist"),
        ("detective", "investigator"),
        ("scholar", "learner"),
        ("merchant", "trader"),
        ("warrior", "fighter"),
        ("traveller", "visitor"),
        ("rose", "flower"),
        ("tulip", "flower"),
        ("oak", "tree"),
        ("pine", "tree"),
        ("sparrow", "bird"),
        ("eagle", "bird"),
        ("salmon", "fish"),
        ("shark", "fish"),
        ("car", "vehicle"),
        ("bicycle", "vehicle"),
        ("bus", "vehicle"),
        ("train", "vehicle"),
        ("apple", "fruit"),
        ("banana", "fruit"),
        ("lion", "mammal"),
        ("tiger", "mammal"),
        ("horse", "mammal"),
        ("robot", "machine"),
        ("laptop", "computer"),
        ("phone", "device"),
    ]

    unary_templates = [
        ("every_x_is_y", "Every {source} is {target_article} {target}."),
        ("all_x_are_y", "All {source_plural} are {target_plural}."),
        ("if_x_then_y", "If something is {source_article} {source}, then it is {target_article} {target}."),
        ("anything_x_is_y", "Anything that is {source_article} {source} is also {target_article} {target}."),
        ("being_x_implies_y", "Being {source_article} {source} implies being {target_article} {target}."),
        ("classified_x_y", "Something classified as {source_article} {source} is also classified as {target_article} {target}."),
        ("whenever_x_y", "Whenever something is {source_article} {source}, it is {target_article} {target}."),
        ("x_always_y", "{source_article_cap} {source} is always {target_article} {target}."),
        ("considered_x_y", "Anything considered {source_article} {source} can also be considered {target_article} {target}."),
        ("category_x_y", "If something belongs to the category of {source}, it also belongs to the category of {target}."),
    ]

    binary_rules = [
        ("older_than(X, Y)", "parent(X, Y)", "parent_implies_older",
         "X is the parent of Y", "X is older than Y"),
        ("ancestor(X, Y)", "parent(X, Y)", "parent_implies_ancestor",
         "X is the parent of Y", "X is an ancestor of Y"),
        ("child_of(Y, X)", "parent(X, Y)", "parent_implies_child",
         "X is the parent of Y", "Y is a child of X"),
        ("known_by(Y, X)", "knows(X, Y)", "knows_inverse",
         "X knows Y", "Y is known by X"),
        ("supported_by(Y, X)", "supports(X, Y)", "supports_inverse",
         "X supports Y", "Y is supported by X"),
        ("helped_by(Y, X)", "helps(X, Y)", "helps_inverse",
         "X helps Y", "Y is helped by X"),
        ("teacher_of(X, Y)", "teaches(X, Y)", "teaches_implies_teacher",
         "X teaches Y", "X is a teacher of Y"),
        ("student_of(Y, X)", "teaches(X, Y)", "teaches_implies_student",
         "X teaches Y", "Y is a student of X"),
        ("followed_by(Y, X)", "follows(X, Y)", "follows_inverse",
         "X follows Y", "Y is followed by X"),
        ("trusted_by(Y, X)", "trusts(X, Y)", "trusts_inverse",
         "X trusts Y", "Y is trusted by X"),
        ("admired_by(Y, X)", "admires(X, Y)", "admires_inverse",
         "X admires Y", "Y is admired by X"),
        ("visited_by(Y, X)", "visits(X, Y)", "visits_inverse",
         "X visits Y", "Y is visited by X"),
        ("called_by(Y, X)", "calls(X, Y)", "calls_inverse",
         "X calls Y", "Y is called by X"),
        ("liked_by(Y, X)", "likes(X, Y)", "likes_inverse",
         "X likes Y", "Y is liked by X"),
        ("respected_by(Y, X)", "respects(X, Y)", "respects_inverse",
         "X respects Y", "Y is respected by X"),
        ("managed_by(Y, X)", "manages(X, Y)", "manages_inverse",
         "X manages Y", "Y is managed by X"),
        ("employed_by(Y, X)", "employs(X, Y)", "employs_inverse",
         "X employs Y", "Y is employed by X"),
        ("owned_by(Y, X)", "owns(X, Y)", "owns_inverse",
         "X owns Y", "Y is owned by X"),
        ("supervised_by(Y, X)", "supervises(X, Y)", "supervises_inverse",
         "X supervises Y", "Y is supervised by X"),
        ("trained_by(Y, X)", "trains(X, Y)", "trains_inverse",
         "X trains Y", "Y is trained by X"),
        ("guided_by(Y, X)", "guides(X, Y)", "guides_inverse",
         "X guides Y", "Y is guided by X"),
        ("protected_by(Y, X)", "protects(X, Y)", "protects_inverse",
         "X protects Y", "Y is protected by X"),
        ("invited_by(Y, X)", "invites(X, Y)", "invites_inverse",
         "X invites Y", "Y is invited by X"),
        ("recommended_by(Y, X)", "recommends(X, Y)", "recommends_inverse",
         "X recommends Y", "Y is recommended by X"),
        ("chosen_by(Y, X)", "chooses(X, Y)", "chooses_inverse",
         "X chooses Y", "Y is chosen by X"),
        ("reported_by(Y, X)", "reports(X, Y)", "reports_inverse",
         "X reports Y", "Y is reported by X"),
        ("observed_by(Y, X)", "observes(X, Y)", "observes_inverse",
         "X observes Y", "Y is observed by X"),
        ("contacted_by(Y, X)", "contacts(X, Y)", "contacts_inverse",
         "X contacts Y", "Y is contacted by X"),
        ("challenged_by(Y, X)", "challenges(X, Y)", "challenges_inverse",
         "X challenges Y", "Y is challenged by X"),
        ("follower_of(X, Y)", "follows(X, Y)", "follows_same_direction",
         "X follows Y", "X is a follower of Y"),
        ("assistant_of(X, Y)", "helps(X, Y)", "helps_same_direction",
         "X helps Y", "X acts as an assistant to Y"),
        ("supporter_of(X, Y)", "supports(X, Y)", "supports_same_direction",
         "X supports Y", "X is a supporter of Y"),
        ("admirer_of(X, Y)", "admires(X, Y)", "admires_same_direction",
         "X admires Y", "X is an admirer of Y"),
        ("visitor_of(X, Y)", "visits(X, Y)", "visits_same_direction",
         "X visits Y", "X is a visitor of Y"),
        ("caller_of(X, Y)", "calls(X, Y)", "calls_same_direction",
         "X calls Y", "X is a caller of Y"),
        ("guardian_of(X, Y)", "protects(X, Y)", "protects_same_direction",
         "X protects Y", "X is a guardian of Y"),
        ("trainer_of(X, Y)", "trains(X, Y)", "trains_same_direction",
         "X trains Y", "X is a trainer of Y"),
        ("guide_of(X, Y)", "guides(X, Y)", "guides_same_direction",
         "X guides Y", "X is a guide of Y"),
        ("supervisor_of(X, Y)", "supervises(X, Y)", "supervises_same_direction",
         "X supervises Y", "X is a supervisor of Y"),
        ("manager_of(X, Y)", "manages(X, Y)", "manages_same_direction",
         "X manages Y", "X is a manager of Y"),
    ]

    binary_templates = [
        ("binary_if_then", "If {body_text}, then {head_text}."),
        ("binary_when_then", "When {body_text}, {head_text}."),
        ("binary_whenever", "Whenever {body_text}, it follows that {head_text}."),
        ("binary_given", "Given that {body_text}, {head_text}."),
        ("binary_relationship", "If it is true that {body_text}, then {head_text}."),
    ]

    examples = []
    unary_candidates = []

    for source, target in unary_rule_pairs:
        for template_name, template in unary_templates:
            unary_candidates.append(
                (source, target, template_name, template)
            )

    random.shuffle(unary_candidates)

    for example_number, (source, target, template_name, template) in enumerate(
        unary_candidates[:400],
        start=1,
    ):
        natural_language = template.format(
            source=source,
            target=target,
            source_article=get_article(source),
            target_article=get_article(target),
            source_article_cap=get_article(source).capitalize(),
            source_plural=pluralise(source),
            target_plural=pluralise(target),
        )

        examples.append(
            create_example(
                example_id=f"rule_{example_number:04d}",
                level=2,
                category="simple_rule",
                natural_language=natural_language,
                prolog=f"{target}(X) :- {source}(X).",
                template_group=f"{source}_implies_{target}",
                nl_template=template_name,
            )
        )

    binary_candidates = []

    for head, body, group, body_text, head_text in binary_rules:
        for template_name, template in binary_templates:
            binary_candidates.append(
                (
                    head,
                    body,
                    group,
                    template_name,
                    template.format(
                        body_text=body_text,
                        head_text=head_text,
                    ),
                )
            )

    random.shuffle(binary_candidates)

    if len(binary_candidates) < 200:
        raise ValueError("Not enough unique binary simple-rule candidates.")

    for example_number, (
        head,
        body,
        group,
        template_name,
        natural_language,
    ) in enumerate(binary_candidates[:200], start=401):
        examples.append(
            create_example(
                example_id=f"rule_{example_number:04d}",
                level=2,
                category="simple_rule",
                natural_language=natural_language,
                prolog=f"{head} :- {body}.",
                template_group=group,
                nl_template=template_name,
            )
        )

    return examples

def generate_multi_condition_rules():
    two_condition_rules = [
        ("eligible(X)", ["adult(X)", "citizen(X)"], "adult_citizen_eligible", "a person is an adult", "they are a citizen", "they are eligible"),
        ("can_drive(X)", ["adult(X)", "has_licence(X)"], "adult_licence_drive", "a person is an adult", "they have a licence", "they can drive"),
        ("employable(X)", ["qualified(X)", "available(X)"], "qualified_available_employable", "a person is qualified", "they are available", "they are employable"),
        ("healthy(X)", ["exercises(X)", "eats_well(X)"], "exercise_diet_healthy", "a person exercises", "they eat well", "they are healthy"),
        ("successful_student(X)", ["studies(X)", "attends_classes(X)"], "study_attendance_success", "a person studies", "they attend classes", "they are a successful student"),
        ("trusted_employee(X)", ["honest(X)", "reliable(X)"], "honest_reliable_trusted", "a person is honest", "they are reliable", "they are a trusted employee"),
        ("predator(X)", ["animal(X)", "hunts(X)"], "animal_hunts_predator", "something is an animal", "it hunts", "it is a predator"),
        ("water_animal(X)", ["animal(X)", "swims(X)"], "animal_swims_water", "something is an animal", "it swims", "it is a water animal"),
        ("team_member(X)", ["employee(X)", "assigned_to_team(X)"], "employee_assigned_team", "a person is an employee", "they are assigned to a team", "they are a team member"),
        ("research_candidate(X)", ["student(X)", "interested_in_research(X)"], "student_research_candidate", "a person is a student", "they are interested in research", "they are a research candidate"),
        ("dangerous(X)", ["armed(X)", "hostile(X)"], "armed_hostile_dangerous", "a person is armed", "they are hostile", "they are dangerous"),
        ("can_vote(X)", ["adult(X)", "registered(X)"], "adult_registered_vote", "a person is an adult", "they are registered", "they can vote"),
        ("can_enter(X)", ["authorised(X)", "identified(X)"], "authorised_identified_enter", "a person is authorised", "they are identified", "they can enter"),
        ("promotable(X)", ["experienced(X)", "high_performance(X)"], "experienced_performance_promotable", "a person is experienced", "they have high performance", "they are promotable"),
        ("prepared(X)", ["trained(X)", "equipped(X)"], "trained_equipped_prepared", "a person is trained", "they are equipped", "they are prepared"),
        ("eligible_for_award(X)", ["nominated(X)", "qualified(X)"], "nominated_qualified_award", "a person is nominated", "they are qualified", "they are eligible for an award"),
        ("trusted_source(X)", ["verified(X)", "reliable(X)"], "verified_reliable_source", "a source is verified", "it is reliable", "it is a trusted source"),
        ("operational(X)", ["powered(X)", "functional(X)"], "powered_functional_operational", "a system is powered", "it is functional", "it is operational"),
        ("ready_for_use(X)", ["tested(X)", "approved(X)"], "tested_approved_ready", "something is tested", "it is approved", "it is ready for use"),
        ("priority_case(X)", ["urgent(X)", "important(X)"], "urgent_important_priority", "a case is urgent", "it is important", "it is a priority case"),
    ]

    two_templates = [
        ("two_if_and", "If {first} and {second}, then {result}."),
        ("two_when_both", "When {first} and {second}, {result}."),
        ("two_both", "If both {first} and {second}, {result}."),
        ("two_requires", "{result_cap} when {first} and {second}."),
        ("two_combination", "The combination of the facts that {first} and {second} means that {result}."),
        ("two_given", "Given that {first} and {second}, {result}."),
        ("two_provided", "Provided that {first} and {second}, {result}."),
        ("two_condition", "{result_cap} if {first} while also {second}."),
        ("two_joint", "If it is established that {first} and that {second}, then {result}."),
        ("two_simultaneous", "When it is true that {first} and also true that {second}, {result}."),
        ("two_once", "Once both conditions hold, namely that {first} and {second}, {result}."),
        ("two_jointly", "{first_cap} and {second}; together these imply that {result}."),
        ("two_where", "In a case where {first} and {second}, {result}."),
        ("two_so_long", "So long as {first} and {second}, {result}."),
        ("two_if_true", "If the statements that {first} and {second} are true, then {result}."),
    ]

    three_condition_rules = [
        ("qualified(X)", ["graduate(X)", "experienced(X)", "certified(X)"], "graduate_experience_certified",
         ["a person is a graduate", "they are experienced", "they are certified"], "they are qualified"),
        ("excellent_employee(X)", ["skilled(X)", "reliable(X)", "hardworking(X)"], "skilled_reliable_hardworking",
         ["a person is skilled", "they are reliable", "they are hardworking"], "they are an excellent employee"),
        ("good_candidate(X)", ["educated(X)", "experienced(X)", "motivated(X)"], "educated_experienced_motivated",
         ["a person is educated", "they are experienced", "they are motivated"], "they are a good candidate"),
        ("adventurer(X)", ["brave(X)", "prepared(X)", "travels(X)"], "brave_prepared_travels",
         ["a person is brave", "they are prepared", "they travel"], "they are an adventurer"),
        ("advanced_student(X)", ["student(X)", "experienced(X)", "high_grades(X)"], "student_experience_grades",
         ["a person is a student", "they are experienced", "they have high grades"], "they are an advanced student"),
        ("secure_system(X)", ["encrypted(X)", "authenticated(X)", "monitored(X)"], "encrypted_authenticated_monitored",
         ["a system is encrypted", "it is authenticated", "it is monitored"], "it is secure"),
        ("valuable_item(X)", ["rare(X)", "old(X)", "well_preserved(X)"], "rare_old_preserved",
         ["an item is rare", "it is old", "it is well preserved"], "it is valuable"),
        ("strong_team(X)", ["cooperative(X)", "skilled(X)", "organised(X)"], "cooperative_skilled_organised",
         ["a team is cooperative", "it is skilled", "it is organised"], "it is a strong team"),
        ("safe_vehicle(X)", ["inspected(X)", "maintained(X)", "insured(X)"], "inspected_maintained_insured",
         ["a vehicle is inspected", "it is maintained", "it is insured"], "it is a safe vehicle"),
        ("approved_project(X)", ["reviewed(X)", "funded(X)", "scheduled(X)"], "reviewed_funded_scheduled",
         ["a project is reviewed", "it is funded", "it is scheduled"], "it is an approved project"),
    ]

    three_templates = [
        ("three_if", "If {a}, {b}, and {c}, then {result}."),
        ("three_when", "When {a}, {b}, and {c}, {result}."),
        ("three_all", "If all three conditions hold: {a}, {b}, and {c}, then {result}."),
        ("three_given", "Given that {a}, {b}, and {c}, {result}."),
        ("three_combined", "The facts that {a}, {b}, and {c} together imply that {result}."),
        ("three_provided", "Provided that {a}, {b}, and {c}, {result}."),
        ("three_joint", "If it is established that {a}, that {b}, and that {c}, then {result}."),
        ("three_where", "In a case where {a}, {b}, and {c}, {result}."),
        ("three_once", "Once it is true that {a}, {b}, and {c}, {result}."),
        ("three_conditions", "{result_cap} when the three conditions hold that {a}, {b}, and {c}."),
        ("three_simultaneous", "When all of the following are true - {a}, {b}, and {c} - {result}."),
        ("three_so_long", "So long as {a}, {b}, and {c}, {result}."),
        ("three_truth", "If the statements that {a}, {b}, and {c} are all true, then {result}."),
        ("three_jointly", "{a_cap}, {b}, and {c}; jointly, these imply that {result}."),
        ("three_requirements", "Meeting the requirements that {a}, {b}, and {c} means that {result}."),
    ]

    special_rules = [
        ("sibling(X, Y)", ["parent(Z, X)", "parent(Z, Y)", "X \\= Y"], "sibling_inequality",
         [
             "Two different people are siblings if they share the same parent.",
             "If X and Y have the same parent and X is not Y, then they are siblings.",
             "People with a common parent are siblings provided they are different people.",
             "X is a sibling of Y when they share a parent and are not the same person.",
             "If two distinct people have the same parent, they are siblings.",
             "When X and Y share parent Z and are different individuals, X and Y are siblings.",
             "Sharing a parent makes two people siblings as long as they are not the same person.",
             "Two people count as siblings when one parent has both of them as children and they are distinct.",
             "If parent Z has both X and Y as children, and X differs from Y, then X and Y are siblings.",
             "X and Y are siblings whenever they have a parent in common and X is not equal to Y.",
         ]),
        ("can_fly(X)", ["bird(X)", "\\+ flightless(X)"], "bird_not_flightless",
         [
             "A bird can fly if it is not known to be flightless.",
             "Any bird that is not flightless can fly.",
             "If something is a bird and there is no evidence that it is flightless, then it can fly.",
             "A creature can fly when it is a bird and flightlessness cannot be established.",
             "Being a bird allows flight provided there is no evidence of being flightless.",
             "If X is a bird and flightless(X) cannot be proven, then X can fly.",
             "A bird is able to fly when no fact establishes that it is flightless.",
             "Anything known to be a bird can fly unless it can be shown to be flightless.",
             "If an entity is a bird and is not provably flightless, it can fly.",
             "A creature qualifies as able to fly when it is a bird and there is no evidence it is flightless.",
         ]),
        ("safe(X)", ["inspected(X)", "\\+ dangerous(X)"], "inspected_not_dangerous",
         [
             "Something is safe if it has been inspected and there is no evidence that it is dangerous.",
             "An inspected object is safe when it is not known to be dangerous.",
             "If something is inspected and dangerousness cannot be established, then it is safe.",
             "Being inspected and not provably dangerous makes something safe.",
             "An object is considered safe when it has been inspected and there is no evidence it is dangerous.",
             "If X is inspected and dangerous(X) cannot be proven, then X is safe.",
             "An inspected item is safe provided that no fact establishes it as dangerous.",
             "Anything inspected can be considered safe unless it can be shown to be dangerous.",
             "If an entity is inspected and is not provably dangerous, it is safe.",
             "Inspection establishes safety when there is no evidence of danger.",
         ]),
        ("available(X)", ["employee(X)", "\\+ busy(X)"], "employee_not_busy",
         [
             "An employee is available if there is no evidence that they are busy.",
             "Any employee who is not known to be busy is available.",
             "If someone is an employee and busyness cannot be established, then they are available.",
             "Being an employee who is not provably busy makes someone available.",
             "An employee can be considered available when there is no evidence they are busy.",
             "If X is an employee and busy(X) cannot be proven, then X is available.",
             "An employee is available provided that no fact establishes that they are busy.",
             "Anyone who is an employee is available unless they can be shown to be busy.",
             "If an employee is not provably busy, that employee is available.",
             "Employment together with the absence of evidence of being busy implies availability.",
         ]),
        ("different_parent(X, Y)", ["parent(X, Z)", "parent(Y, Z)", "X \\= Y"], "shared_child_inequality",
         [
             "X and Y are different parents if they both parent Z and are not the same person.",
             "Two distinct people are different parents when they share a child.",
             "If X and Y are both parents of Z and X is not Y, then they are different parents.",
             "People who share a child but are not the same individual are different parents.",
             "Two people count as different parents when they parent the same person and are distinct.",
             "When X and Y are parents of the same child and differ from one another, they are different parents.",
             "Sharing a child makes X and Y different parents provided X is not equal to Y.",
             "If the same child Z has parents X and Y, and X differs from Y, then they are different parents.",
             "X and Y qualify as different parents when both parent Z and they are distinct people.",
             "Two people are different parents whenever they have a child in common and are not the same person.",
         ]),
    ]

    candidates = []

    for head, body, group, first, second, result in two_condition_rules:
        for template_name, template in two_templates:
            candidates.append(
                (
                    head,
                    body,
                    group,
                    template_name,
                    template.format(
                        first=first,
                        second=second,
                        result=result,
                        result_cap=result.capitalize(),
                        first_cap=first.capitalize(),
                    ),
                )
            )

    for head, body, group, conditions, result in three_condition_rules:
        a, b, c = conditions
        for template_name, template in three_templates:
            candidates.append(
                (
                    head,
                    body,
                    group,
                    template_name,
                    template.format(
                        a=a,
                        b=b,
                        c=c,
                        result=result,
                        result_cap=result.capitalize(),
                        a_cap=a.capitalize(),
                    ),
                )
            )

    for head, body, group, templates in special_rules:
        for index, natural_language in enumerate(templates, start=1):
            candidates.append(
                (
                    head,
                    body,
                    group,
                    f"special_{index}",
                    natural_language,
                )
            )

    random.shuffle(candidates)

    if len(candidates) < 500:
        raise ValueError(
            f"Only {len(candidates)} unique multi-condition candidates are available."
        )

    examples = []

    for example_number, (
        head,
        body,
        group,
        template_name,
        natural_language,
    ) in enumerate(candidates[:500], start=1):
        examples.append(
            create_example(
                example_id=f"multi_{example_number:04d}",
                level=3,
                category="multi_condition_rule",
                natural_language=natural_language,
                prolog=f"{head} :- {', '.join(body)}.",
                template_group=group,
                nl_template=template_name,
            )
        )

    return examples

def generate_reasoning():
    names = [
        "ash", "brook", "ciel", "dio", "edward", "faust", "gary",
        "haku", "irina", "joseph", "kai", "luffy", "mary", "nathan",
        "olivia", "petra", "quistis", "ray", "sinbad", "tanya", "usagi",
        "violet", "wendy", "xeno", "yuri", "zelda",
    ]

    examples = []
    example_number = 1

    classifications = [
        ("cat", "animal"),
        ("dog", "animal"),
        ("bird", "animal"),
        ("student", "learner"),
        ("teacher", "educator"),
        ("doctor", "professional"),
        ("scientist", "researcher"),
        ("musician", "artist"),
        ("athlete", "competitor"),
        ("programmer", "technologist"),
    ]

    classification_combinations = [
        (name, source, target)
        for name in names
        for source, target in classifications
    ]
    random.shuffle(classification_combinations)

    for i, (name, source, target) in enumerate(
        classification_combinations[:100]
    ):
        expected = i % 2 == 0

        if expected:
            query_name = name
        else:
            query_name = random.choice(
                [candidate for candidate in names if candidate != name]
            )

        source_article = get_article(source)
        target_article = get_article(target)

        natural_language = (
            f"{name.capitalize()} is {source_article} {source}. "
            f"Every {source} is {target_article} {target}. "
            f"Is {query_name.capitalize()} {target_article} {target}?"
        )

        prolog = (
            f"{source}({name}).\n"
            f"{target}(X) :- {source}(X)."
        )

        examples.append(
            create_example(
                example_id=f"reasoning_{example_number:04d}",
                level=4,
                category="reasoning",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"classification_{source}_{target}",
                nl_template="classification_fact_rule_question",
                query=f"{target}({query_name}).",
                expected_result=expected,
            )
        )
        example_number += 1

    family_combinations = [
        (first, second, third)
        for first in names
        for second in names
        for third in names
        if len({first, second, third}) == 3
    ]
    random.shuffle(family_combinations)

    for i, (first, second, third) in enumerate(
        family_combinations[:100]
    ):
        expected = i % 2 == 0

        if expected:
            query_target = third
        else:
            query_target = random.choice(
                [
                    name
                    for name in names
                    if name not in {first, second, third}
                ]
            )

        natural_language = (
            f"{first.capitalize()} is {second.capitalize()}'s parent. "
            f"{second.capitalize()} is {third.capitalize()}'s parent. "
            "A parent of a parent is a grandparent. "
            f"Is {first.capitalize()} {query_target.capitalize()}'s grandparent?"
        )

        prolog = (
            f"parent({first}, {second}).\n"
            f"parent({second}, {third}).\n"
            "grandparent(X, Z) :- parent(X, Y), parent(Y, Z)."
        )

        examples.append(
            create_example(
                example_id=f"reasoning_{example_number:04d}",
                level=4,
                category="reasoning",
                natural_language=natural_language,
                prolog=prolog,
                template_group="grandparent_reasoning",
                nl_template="grandparent_chain_question",
                query=f"grandparent({first}, {query_target}).",
                expected_result=expected,
            )
        )
        example_number += 1

    condition_sets = [
        {
            "result": "eligible",
            "condition_one": "adult",
            "condition_two": "citizen",
            "fact_one": "{name} is an adult.",
            "fact_two": "{name} is a citizen.",
            "missing_two": "There is no information stating that {name} is a citizen.",
            "rule": "Anyone who is an adult and a citizen is eligible.",
            "question": "Is {name} eligible?",
        },
        {
            "result": "can_drive",
            "condition_one": "adult",
            "condition_two": "has_licence",
            "fact_one": "{name} is an adult.",
            "fact_two": "{name} has a licence.",
            "missing_two": "There is no information stating that {name} has a licence.",
            "rule": "Anyone who is an adult and has a licence can drive.",
            "question": "Can {name} drive?",
        },
        {
            "result": "employable",
            "condition_one": "qualified",
            "condition_two": "available",
            "fact_one": "{name} is qualified.",
            "fact_two": "{name} is available.",
            "missing_two": "There is no information stating that {name} is available.",
            "rule": "Anyone who is qualified and available is employable.",
            "question": "Is {name} employable?",
        },
        {
            "result": "healthy",
            "condition_one": "exercises",
            "condition_two": "eats_well",
            "fact_one": "{name} exercises.",
            "fact_two": "{name} eats well.",
            "missing_two": "There is no information stating that {name} eats well.",
            "rule": "Anyone who exercises and eats well is healthy.",
            "question": "Is {name} healthy?",
        },
        {
            "result": "trusted_employee",
            "condition_one": "honest",
            "condition_two": "reliable",
            "fact_one": "{name} is honest.",
            "fact_two": "{name} is reliable.",
            "missing_two": "There is no information stating that {name} is reliable.",
            "rule": "Anyone who is honest and reliable is a trusted employee.",
            "question": "Is {name} a trusted employee?",
        },
        {
            "result": "research_candidate",
            "condition_one": "student",
            "condition_two": "interested_in_research",
            "fact_one": "{name} is a student.",
            "fact_two": "{name} is interested in research.",
            "missing_two": "There is no information stating that {name} is interested in research.",
            "rule": "Any student who is interested in research is a research candidate.",
            "question": "Is {name} a research candidate?",
        },
        {
            "result": "dangerous",
            "condition_one": "armed",
            "condition_two": "hostile",
            "fact_one": "{name} is armed.",
            "fact_two": "{name} is hostile.",
            "missing_two": "There is no information stating that {name} is hostile.",
            "rule": "Anyone who is armed and hostile is dangerous.",
            "question": "Is {name} dangerous?",
        },
        {
            "result": "team_member",
            "condition_one": "employee",
            "condition_two": "assigned_to_team",
            "fact_one": "{name} is an employee.",
            "fact_two": "{name} is assigned to a team.",
            "missing_two": "There is no information stating that {name} is assigned to a team.",
            "rule": "Any employee assigned to a team is a team member.",
            "question": "Is {name} a team member?",
        },
    ]

    conjunction_combinations = [
        (name, condition)
        for name in names
        for condition in condition_sets
    ]
    random.shuffle(conjunction_combinations)

    for i, (name, condition) in enumerate(
        conjunction_combinations[:100]
    ):
        expected = i % 2 == 0
        display_name = name.capitalize()

        if expected:
            facts = (
                f"{condition['condition_one']}({name}).\n"
                f"{condition['condition_two']}({name}).\n"
            )
            natural_language = (
                f"{condition['fact_one'].format(name=display_name)} "
                f"{condition['fact_two'].format(name=display_name)} "
                f"{condition['rule']} "
                f"{condition['question'].format(name=display_name)}"
            )
        else:
            facts = f"{condition['condition_one']}({name}).\n"
            natural_language = (
                f"{condition['fact_one'].format(name=display_name)} "
                f"{condition['missing_two'].format(name=display_name)} "
                f"{condition['rule']} "
                f"{condition['question'].format(name=display_name)}"
            )

        prolog = (
            facts
            + f"{condition['result']}(X) :- "
            f"{condition['condition_one']}(X), "
            f"{condition['condition_two']}(X)."
        )

        examples.append(
            create_example(
                example_id=f"reasoning_{example_number:04d}",
                level=4,
                category="reasoning",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"conjunction_{condition['result']}",
                nl_template="conjunction_reasoning",
                query=f"{condition['result']}({name}).",
                expected_result=expected,
            )
        )
        example_number += 1

    negation_rules = [
        {
            "result": "can_fly",
            "positive": "bird",
            "negative": "flightless",
            "positive_fact": "{name} is a bird.",
            "negative_fact": "{name} is flightless.",
            "missing_negative": "There is no evidence that {name} is flightless.",
            "rule": "A bird can fly if there is no evidence that it is flightless.",
            "question": "Can {name} fly?",
        },
        {
            "result": "available",
            "positive": "employee",
            "negative": "busy",
            "positive_fact": "{name} is an employee.",
            "negative_fact": "{name} is busy.",
            "missing_negative": "There is no evidence that {name} is busy.",
            "rule": "An employee is available if there is no evidence that they are busy.",
            "question": "Is {name} available?",
        },
        {
            "result": "safe",
            "positive": "inspected",
            "negative": "dangerous",
            "positive_fact": "{name} has been inspected.",
            "negative_fact": "{name} is dangerous.",
            "missing_negative": "There is no evidence that {name} is dangerous.",
            "rule": "Something that has been inspected is safe if there is no evidence that it is dangerous.",
            "question": "Is {name} safe?",
        },
        {
            "result": "allowed_entry",
            "positive": "registered",
            "negative": "banned",
            "positive_fact": "{name} is registered.",
            "negative_fact": "{name} is banned.",
            "missing_negative": "There is no evidence that {name} is banned.",
            "rule": "A registered person is allowed entry if there is no evidence that they are banned.",
            "question": "Is {name} allowed entry?",
        },
        {
            "result": "active",
            "positive": "member",
            "negative": "suspended",
            "positive_fact": "{name} is a member.",
            "negative_fact": "{name} is suspended.",
            "missing_negative": "There is no evidence that {name} is suspended.",
            "rule": "A member is active if there is no evidence that they are suspended.",
            "question": "Is {name} active?",
        },
    ]

    negation_combinations = [
        (name, rule)
        for name in names
        for rule in negation_rules
    ]
    random.shuffle(negation_combinations)

    for i, (name, rule) in enumerate(negation_combinations[:100]):
        expected = i % 2 == 0
        display_name = name.capitalize()

        if expected:
            facts = f"{rule['positive']}({name}).\n"
            natural_language = (
                f"{rule['positive_fact'].format(name=display_name)} "
                f"{rule['missing_negative'].format(name=display_name)} "
                f"{rule['rule']} "
                f"{rule['question'].format(name=display_name)}"
            )
        else:
            facts = (
                f"{rule['positive']}({name}).\n"
                f"{rule['negative']}({name}).\n"
            )
            natural_language = (
                f"{rule['positive_fact'].format(name=display_name)} "
                f"{rule['negative_fact'].format(name=display_name)} "
                f"{rule['rule']} "
                f"{rule['question'].format(name=display_name)}"
            )

        prolog = (
            facts
            + f"{rule['result']}(X) :- "
            f"{rule['positive']}(X), "
            f"\\+ {rule['negative']}(X)."
        )

        examples.append(
            create_example(
                example_id=f"reasoning_{example_number:04d}",
                level=4,
                category="reasoning",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"negation_{rule['result']}",
                nl_template="negation_reasoning",
                query=f"{rule['result']}({name}).",
                expected_result=expected,
            )
        )
        example_number += 1

    return examples

def validate_generated_dataset(dataset):
    ids = [example["id"] for example in dataset]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate example IDs found.")

    pairs = [
        (
            example["natural_language"],
            example["prolog"],
            example.get("query"),
        )
        for example in dataset
    ]

    if len(pairs) != len(set(pairs)):
        duplicate_count = len(pairs) - len(set(pairs))
        raise ValueError(
            f"Found {duplicate_count} duplicate NL-Prolog-query examples."
        )

def generate_dataset():
    random.seed(RANDOM_SEED)

    dataset = []
    dataset.extend(generate_facts())
    dataset.extend(generate_simple_rules())
    dataset.extend(generate_multi_condition_rules())
    dataset.extend(generate_reasoning())

    validate_generated_dataset(dataset)

    return dataset

def save_jsonl(dataset, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for example in dataset:
            json.dump(example, file, ensure_ascii=False)
            file.write("\n")

def print_summary(dataset):
    print("=" * 40)
    print("DATASET GENERATION SUMMARY")
    print("=" * 40)

    categories = [
        "fact",
        "simple_rule",
        "multi_condition_rule",
        "reasoning",
    ]

    for category in categories:
        count = sum(
            1 for example in dataset
            if example["category"] == category
        )
        print(f"{category}: {count}")

    reasoning_examples = [
        example
        for example in dataset
        if example["category"] == "reasoning"
    ]

    true_queries = sum(
        example["expected_result"] is True
        for example in reasoning_examples
    )

    false_queries = sum(
        example["expected_result"] is False
        for example in reasoning_examples
    )

    print()
    print(f"Reasoning true queries:  {true_queries}")
    print(f"Reasoning false queries: {false_queries}")
    print()
    print(f"Total examples: {len(dataset)}")
    print("=" * 40)

def main():
    dataset = generate_dataset()
    save_jsonl(dataset, OUTPUT_PATH)
    print_summary(dataset)
    print()
    print(f"Saved dataset to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()