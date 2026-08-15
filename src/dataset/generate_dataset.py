import json
import random
from pathlib import Path

OUTPUT_PATH = Path("dataset/raw/examples.jsonl")
RANDOM_SEED = 4242564

def create_example(
    example_id,
    level,
    category,
    natural_language,
    prolog,
    template_group,
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

    if query is not None:
        example["query"] = query

    if expected_result is not None:
        example["expected_result"] = expected_result

    return example

def generate_facts():
    names = [
        "ash",
        "brook",
        "ciel",
        "dio",
        "edward",
        "faust",
        "gary",
        "haku",
        "irina",
        "joseph",
        "kai",
        "luffy",
        "mary",
        "nathan",
        "olivia",
        "petra",
        "quistis",
        "ray",
        "sinbad",
        "tanya",
        "usagi",
        "violet",
        "wendy",
        "xeno",
        "yuri",
        "zelda"
    ]

    unary_predicates = [
        "cat",
        "dog",
        "bird",
        "student",
        "teacher",
        "scientist",
        "musician",
        "doctor",
        "athlete",
        "artist",
        "human",
        "engineer",
        "programmer",
        "researcher",
        "writer",
        "chef",
        "pilot",
        "farmer",
        "dancer",
        "singer",
        "warrior",
        "scholar",
        "traveller",
        "merchant",
        "detective",
        "nurse"
    ]

    unary_templates = [
        "{name} is a {predicate}.",
        "{name} is classified as a {predicate}.",
        "{name} is known to be a {predicate}.",
        "{name} belongs to the category of {predicate}."
    ]

    binary_predicates = [
        "likes",
        "knows",
        "helps",
        "follows",
        "visits",
        "trusts",
        "admires",
        "teaches",
        "supports",
        "calls"
    ]

    binary_templates = {
        "likes": [
            "{first} likes {second}.",
            "{first} is fond of {second}."
        ],
        "knows": [
            "{first} knows {second}.",
            "{first} is acquainted with {second}."
        ],
        "helps": [
            "{first} helps {second}.",
            "{first} gives assistance to {second}."
        ],
        "follows": [
            "{first} follows {second}.",
            "{first} is following {second}."
        ],
        "visits": [
            "{first} visits {second}.",
            "{first} goes to visit {second}."
        ],
        "trusts": [
            "{first} trusts {second}.",
            "{first} has trust in {second}."
        ],
        "admires": [
            "{first} admires {second}.",
            "{first} looks up to {second}."
        ],
        "teaches": [
            "{first} teaches {second}.",
            "{first} provides teaching to {second}."
        ],
        "supports": [
            "{first} supports {second}.",
            "{first} gives support to {second}."
        ],
        "calls": [
            "{first} calls {second}.",
            "{first} contacts {second} by calling them."
        ]
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
        start=1
    ):
        template = random.choice(unary_templates)

        natural_language = template.format(
            name=name.capitalize(),
            predicate=predicate
        )

        prolog = f"{predicate}({name})."

        examples.append(
            create_example(
                example_id=f"fact_{example_number:04d}",
                level=1,
                category="fact",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"unary_{predicate}"
            )
        )

    binary_combinations = [
        (first, second, predicate)
        for first in names
        for second in names
        for predicate in binary_predicates
        if first != second
    ]

    random.shuffle(binary_combinations)

    for offset, (first, second, predicate) in enumerate(
        binary_combinations[:150],
        start=351
    ):
        template = random.choice(binary_templates[predicate])

        natural_language = template.format(
            first=first.capitalize(),
            second=second.capitalize()
        )

        prolog = f"{predicate}({first}, {second})."

        examples.append(
            create_example(
                example_id=f"fact_{offset:04d}",
                level=1,
                category="fact",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"binary_{predicate}"
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
        "Every {source} is a {target}.",
        "All {source}s are {target}s.",
        "If something is a {source}, then it is a {target}.",
        "Anything that is a {source} is also a {target}.",
        "Being a {source} implies being a {target}.",
        "Something classified as a {source} is also classified as a {target}.",
        "Whenever something is a {source}, it is a {target}.",
        "A {source} is always a {target}.",
        "Anything considered a {source} can also be considered a {target}.",
        "If an entity belongs to the category {source}, it also belongs to the category {target}.",
    ]

    binary_rules = [
        {
            "head": "older_than(X, Y)",
            "body": "parent(X, Y)",
            "templates": [
                "If X is the parent of Y, then X is older than Y.",
                "A parent is older than their child.",
                "Whenever one person is the parent of another, the parent is older than the child.",
                "If someone is another person's parent, they are older than that person.",
                "Being the parent of someone implies being older than them.",
            ],
            "group": "parent_implies_older",
        },
        {
            "head": "ancestor(X, Y)",
            "body": "parent(X, Y)",
            "templates": [
                "Every parent is an ancestor of their child.",
                "If X is the parent of Y, then X is an ancestor of Y.",
                "Someone who is a person's parent is also that person's ancestor.",
                "Parenthood implies an ancestor relationship.",
                "If one person is the parent of another, the first is an ancestor of the second.",
            ],
            "group": "parent_implies_ancestor",
        },
        {
            "head": "known_by(Y, X)",
            "body": "knows(X, Y)",
            "templates": [
                "If X knows Y, then Y is known by X.",
                "Anyone known by someone is known by that person.",
                "If one person knows another, the second person is known by the first.",
                "Knowing someone means that person is known by you.",
                "When X knows Y, Y is known by X.",
            ],
            "group": "knows_inverse",
        },
        {
            "head": "supported_by(Y, X)",
            "body": "supports(X, Y)",
            "templates": [
                "If X supports Y, then Y is supported by X.",
                "Anyone receiving support from someone is supported by that person.",
                "When one person supports another, the second is supported by the first.",
                "If X gives support to Y, Y is supported by X.",
                "Supporting someone means they are supported by you.",
            ],
            "group": "supports_inverse",
        },
        {
            "head": "helped_by(Y, X)",
            "body": "helps(X, Y)",
            "templates": [
                "If X helps Y, then Y is helped by X.",
                "Someone who receives help from another person is helped by them.",
                "When X helps Y, Y is helped by X.",
                "If one person assists another, the second is helped by the first.",
                "Helping someone means that person is helped by you.",
            ],
            "group": "helps_inverse",
        },
        {
            "head": "teacher_of(X, Y)",
            "body": "teaches(X, Y)",
            "templates": [
                "If X teaches Y, then X is a teacher of Y.",
                "Anyone who teaches someone is their teacher.",
                "If one person teaches another, the first is the teacher of the second.",
                "Teaching someone makes you their teacher.",
                "Whenever X teaches Y, X is Y's teacher.",
            ],
            "group": "teaches_implies_teacher",
        },
        {
            "head": "student_of(Y, X)",
            "body": "teaches(X, Y)",
            "templates": [
                "If X teaches Y, then Y is a student of X.",
                "Anyone taught by someone is their student.",
                "If one person teaches another, the second is the student's teacher relationship reversed.",
                "When X teaches Y, Y is a student of X.",
                "Being taught by someone makes you their student.",
            ],
            "group": "teaches_implies_student",
        },
        {
            "head": "followed_by(Y, X)",
            "body": "follows(X, Y)",
            "templates": [
                "If X follows Y, then Y is followed by X.",
                "Someone who is followed by another person is followed by them.",
                "When X follows Y, Y is followed by X.",
                "If one person follows another, the second is followed by the first.",
                "Following someone means they are followed by you.",
            ],
            "group": "follows_inverse",
        },
        {
            "head": "trusted_by(Y, X)",
            "body": "trusts(X, Y)",
            "templates": [
                "If X trusts Y, then Y is trusted by X.",
                "Someone trusted by another person is trusted by them.",
                "When X trusts Y, Y is trusted by X.",
                "If one person trusts another, the second is trusted by the first.",
                "Trusting someone means that person is trusted by you.",
            ],
            "group": "trusts_inverse",
        },
        {
            "head": "admired_by(Y, X)",
            "body": "admires(X, Y)",
            "templates": [
                "If X admires Y, then Y is admired by X.",
                "Someone admired by another person is admired by them.",
                "When X admires Y, Y is admired by X.",
                "If one person admires another, the second is admired by the first.",
                "Admiring someone means that person is admired by you.",
            ],
            "group": "admires_inverse",
        },
    ]

    examples = []

    unary_candidates = []

    for source, target in unary_rule_pairs:
        for template in unary_templates:
            unary_candidates.append(
                (
                    source,
                    target,
                    template,
                )
            )

    random.shuffle(unary_candidates)

    for example_number, (source, target, template) in enumerate(
        unary_candidates[:400],
        start=1
    ):
        natural_language = template.format(
            source=source,
            target=target,
        )

        prolog = f"{target}(X) :- {source}(X)."

        examples.append(
            create_example(
                example_id=f"rule_{example_number:04d}",
                level=2,
                category="simple_rule",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"{source}_implies_{target}",
            )
        )

    binary_candidates = []

    for rule in binary_rules:
        for template in rule["templates"]:
            binary_candidates.append(
                (
                    rule["head"],
                    rule["body"],
                    template,
                    rule["group"],
                )
            )

    repeated_binary_candidates = []

    while len(repeated_binary_candidates) < 200:
        shuffled = binary_candidates.copy()
        random.shuffle(shuffled)
        repeated_binary_candidates.extend(shuffled)

    binary_candidates = repeated_binary_candidates[:200]

    for example_number, (head, body, template, group) in enumerate(
        binary_candidates,
        start=401
    ):
        prolog = f"{head} :- {body}."

        examples.append(
            create_example(
                example_id=f"rule_{example_number:04d}",
                level=2,
                category="simple_rule",
                natural_language=template,
                prolog=prolog,
                template_group=group,
            )
        )

    return examples

def generate_multi_condition_rules():
    two_condition_rules = [
        {
            "head": "eligible(X)",
            "body": ["adult(X)", "citizen(X)"],
            "templates": [
                "A person is eligible if they are an adult and a citizen.",
                "Anyone who is both an adult and a citizen is eligible.",
                "If someone is an adult and a citizen, then they are eligible.",
                "Being an adult and a citizen makes someone eligible.",
                "A person qualifies as eligible when they are both an adult and a citizen.",
            ],
            "group": "adult_citizen_eligible",
        },
        {
            "head": "can_drive(X)",
            "body": ["adult(X)", "has_licence(X)"],
            "templates": [
                "A person can drive if they are an adult and have a licence.",
                "Anyone who is an adult and has a licence can drive.",
                "If someone is an adult and possesses a licence, then they can drive.",
                "Being an adult with a licence allows someone to drive.",
                "A person is permitted to drive when they are an adult and have a licence.",
            ],
            "group": "adult_licence_drive",
        },
        {
            "head": "grandparent(X, Z)",
            "body": ["parent(X, Y)", "parent(Y, Z)"],
            "templates": [
                "If X is the parent of Y and Y is the parent of Z, then X is the grandparent of Z.",
                "A person is someone's grandparent if they are the parent of that person's parent.",
                "A parent of a parent is a grandparent.",
                "If someone has a child who is also a parent, then they are a grandparent.",
                "Someone is the grandparent of another person when their child is that person's parent.",
            ],
            "group": "grandparent",
        },
        {
            "head": "can_vote(X)",
            "body": ["adult(X)", "registered(X)"],
            "templates": [
                "A person can vote if they are an adult and registered.",
                "Anyone who is both an adult and registered can vote.",
                "If someone is an adult and is registered, then they can vote.",
                "Being a registered adult allows someone to vote.",
                "A person may vote when they are an adult and registered.",
            ],
            "group": "adult_registered_vote",
        },
        {
            "head": "employable(X)",
            "body": ["qualified(X)", "available(X)"],
            "templates": [
                "Someone is employable if they are qualified and available.",
                "Anyone who is both qualified and available is employable.",
                "If someone is qualified and available, then they are employable.",
                "Being qualified and available makes a person employable.",
                "A person is considered employable when they are qualified and available.",
            ],
            "group": "qualified_available_employable",
        },
        {
            "head": "healthy(X)",
            "body": ["exercises(X)", "eats_well(X)"],
            "templates": [
                "A person is healthy if they exercise and eat well.",
                "Anyone who exercises and eats well is healthy.",
                "If someone exercises and eats well, then they are healthy.",
                "Exercising and eating well makes someone healthy.",
                "A person can be considered healthy when they exercise and eat well.",
            ],
            "group": "exercise_diet_healthy",
        },
        {
            "head": "successful_student(X)",
            "body": ["studies(X)", "attends_classes(X)"],
            "templates": [
                "A student is successful if they study and attend classes.",
                "Anyone who studies and attends classes is a successful student.",
                "If someone studies and attends classes, then they are a successful student.",
                "Studying and attending classes makes someone a successful student.",
                "A person becomes a successful student by studying and attending classes.",
            ],
            "group": "study_attendance_success",
        },
        {
            "head": "trusted_employee(X)",
            "body": ["honest(X)", "reliable(X)"],
            "templates": [
                "An employee is trusted if they are honest and reliable.",
                "Anyone who is honest and reliable is a trusted employee.",
                "If someone is honest and reliable, then they are trusted as an employee.",
                "Being honest and reliable makes someone a trusted employee.",
                "A person is considered a trusted employee when they are honest and reliable.",
            ],
            "group": "honest_reliable_trusted",
        },
        {
            "head": "close_friend(X, Y)",
            "body": ["knows(X, Y)", "trusts(X, Y)"],
            "templates": [
                "X is a close friend of Y if X knows Y and trusts Y.",
                "If one person knows and trusts another, then they are a close friend of that person.",
                "Knowing and trusting someone makes a person their close friend.",
                "If X both knows Y and trusts Y, then X is a close friend of Y.",
                "Someone is a close friend of another person when they know and trust them.",
            ],
            "group": "knows_trusts_friend",
        },
        {
            "head": "mentor(X, Y)",
            "body": ["teaches(X, Y)", "supports(X, Y)"],
            "templates": [
                "X is a mentor of Y if X teaches and supports Y.",
                "If someone teaches and supports another person, then they are their mentor.",
                "Teaching and supporting someone makes a person their mentor.",
                "If X teaches Y and supports Y, then X mentors Y.",
                "A person is a mentor when they both teach and support another person.",
            ],
            "group": "teaches_supports_mentor",
        },
        {
            "head": "predator(X)",
            "body": ["animal(X)", "hunts(X)"],
            "templates": [
                "An animal is a predator if it hunts.",
                "If something is an animal and hunts, then it is a predator.",
                "Anything that is both an animal and a hunter is a predator.",
                "Being an animal that hunts makes something a predator.",
                "A creature is a predator when it is an animal and hunts.",
            ],
            "group": "animal_hunts_predator",
        },
        {
            "head": "water_animal(X)",
            "body": ["animal(X)", "swims(X)"],
            "templates": [
                "An animal that swims is a water animal.",
                "If something is an animal and swims, then it is a water animal.",
                "Anything that is both an animal and capable of swimming is a water animal.",
                "Being an animal that swims makes something a water animal.",
                "A creature is considered a water animal when it is an animal and swims.",
            ],
            "group": "animal_swims_water",
        },
        {
            "head": "team_member(X)",
            "body": ["employee(X)", "assigned_to_team(X)"],
            "templates": [
                "An employee is a team member if they are assigned to a team.",
                "If someone is an employee and assigned to a team, then they are a team member.",
                "Anyone who is both an employee and assigned to a team is a team member.",
                "Being an employee assigned to a team makes someone a team member.",
                "A person becomes a team member when they are an employee assigned to a team.",
            ],
            "group": "employee_assigned_team",
        },
        {
            "head": "research_candidate(X)",
            "body": ["student(X)", "interested_in_research(X)"],
            "templates": [
                "A student is a research candidate if they are interested in research.",
                "If someone is a student and interested in research, then they are a research candidate.",
                "Anyone who studies and has an interest in research can be a research candidate.",
                "Being a student interested in research makes someone a research candidate.",
                "A person is considered a research candidate when they are a student with an interest in research.",
            ],
            "group": "student_research_candidate",
        },
        {
            "head": "dangerous(X)",
            "body": ["armed(X)", "hostile(X)"],
            "templates": [
                "Someone is dangerous if they are armed and hostile.",
                "If someone is armed and hostile, then they are dangerous.",
                "Anyone who is both armed and hostile is dangerous.",
                "Being armed and hostile makes a person dangerous.",
                "A person is considered dangerous when they are armed and hostile.",
            ],
            "group": "armed_hostile_dangerous",
        },
    ]

    three_condition_rules = [
        {
            "head": "qualified(X)",
            "body": ["graduate(X)", "experienced(X)", "certified(X)"],
            "templates": [
                "Someone is qualified if they are a graduate, experienced, and certified.",
                "A person is qualified when they have graduated, have experience, and are certified.",
                "If someone is a graduate, experienced, and certified, then they are qualified.",
                "Being a graduate with experience and certification makes someone qualified.",
                "A person qualifies when they are a graduate, experienced, and certified.",
            ],
            "group": "graduate_experience_certified",
        },
        {
            "head": "excellent_employee(X)",
            "body": ["skilled(X)", "reliable(X)", "hardworking(X)"],
            "templates": [
                "Someone is an excellent employee if they are skilled, reliable, and hardworking.",
                "A skilled, reliable, and hardworking person is an excellent employee.",
                "If someone is skilled, reliable, and hardworking, then they are an excellent employee.",
                "Being skilled, reliable, and hardworking makes someone an excellent employee.",
                "A person is considered an excellent employee when they are skilled, reliable, and hardworking.",
            ],
            "group": "skilled_reliable_hardworking",
        },
        {
            "head": "good_candidate(X)",
            "body": ["educated(X)", "experienced(X)", "motivated(X)"],
            "templates": [
                "Someone is a good candidate if they are educated, experienced, and motivated.",
                "An educated, experienced, and motivated person is a good candidate.",
                "If someone is educated, experienced, and motivated, then they are a good candidate.",
                "Being educated, experienced, and motivated makes someone a good candidate.",
                "A person is considered a good candidate when they are educated, experienced, and motivated.",
            ],
            "group": "educated_experienced_motivated",
        },
        {
            "head": "adventurer(X)",
            "body": ["brave(X)", "prepared(X)", "travels(X)"],
            "templates": [
                "Someone is an adventurer if they are brave, prepared, and travel.",
                "A brave and prepared person who travels is an adventurer.",
                "If someone is brave, prepared, and travels, then they are an adventurer.",
                "Being brave, prepared, and willing to travel makes someone an adventurer.",
                "A person qualifies as an adventurer when they are brave, prepared, and travel.",
            ],
            "group": "brave_prepared_travels",
        },
        {
            "head": "advanced_student(X)",
            "body": ["student(X)", "experienced(X)", "high_grades(X)"],
            "templates": [
                "Someone is an advanced student if they are a student, experienced, and have high grades.",
                "A student with experience and high grades is an advanced student.",
                "If someone is a student, has experience, and has high grades, then they are an advanced student.",
                "Being an experienced student with high grades makes someone an advanced student.",
                "A person is considered an advanced student when they are a student with experience and high grades.",
            ],
            "group": "student_experience_grades",
        },
        {
            "head": "secure_system(X)",
            "body": ["encrypted(X)", "authenticated(X)", "monitored(X)"],
            "templates": [
                "A system is secure if it is encrypted, authenticated, and monitored.",
                "An encrypted, authenticated, and monitored system is secure.",
                "If a system is encrypted, authenticated, and monitored, then it is secure.",
                "Encryption, authentication, and monitoring make a system secure.",
                "A system can be considered secure when it is encrypted, authenticated, and monitored.",
            ],
            "group": "encrypted_authenticated_monitored",
        },
        {
            "head": "valuable_item(X)",
            "body": ["rare(X)", "old(X)", "well_preserved(X)"],
            "templates": [
                "An item is valuable if it is rare, old, and well preserved.",
                "A rare, old, and well-preserved item is valuable.",
                "If something is rare, old, and well preserved, then it is valuable.",
                "Being rare, old, and well preserved makes an item valuable.",
                "An object is considered valuable when it is rare, old, and well preserved.",
            ],
            "group": "rare_old_preserved",
        },
        {
            "head": "strong_team(X)",
            "body": ["cooperative(X)", "skilled(X)", "organised(X)"],
            "templates": [
                "A team is strong if it is cooperative, skilled, and organised.",
                "A cooperative, skilled, and organised team is strong.",
                "If a team is cooperative, skilled, and organised, then it is strong.",
                "Cooperation, skill, and organisation make a team strong.",
                "A team is considered strong when it is cooperative, skilled, and organised.",
            ],
            "group": "cooperative_skilled_organised",
        },
    ]

    special_rules = [
        {
            "head": "sibling(X, Y)",
            "body": ["parent(Z, X)", "parent(Z, Y)", "X \\= Y"],
            "templates": [
                "Two different people are siblings if they share the same parent.",
                "If X and Y have the same parent and X is not Y, then they are siblings.",
                "People with a common parent are siblings provided they are different people.",
                "X is a sibling of Y when they share a parent and are not the same person.",
                "If two distinct people have the same parent, they are siblings.",
            ],
            "group": "sibling_inequality",
        },
        {
            "head": "can_fly(X)",
            "body": ["bird(X)", "\\+ flightless(X)"],
            "templates": [
                "A bird can fly if it is not flightless.",
                "Any bird that is not flightless can fly.",
                "If something is a bird and is not flightless, then it can fly.",
                "A creature can fly when it is a bird and there is no evidence that it is flightless.",
                "Being a bird allows flight provided it is not flightless.",
            ],
            "group": "bird_not_flightless",
        },
        {
            "head": "safe(X)",
            "body": ["inspected(X)", "\\+ dangerous(X)"],
            "templates": [
                "Something is safe if it has been inspected and is not dangerous.",
                "An inspected object that is not dangerous is safe.",
                "If something is inspected and there is no evidence it is dangerous, then it is safe.",
                "Being inspected and not dangerous makes something safe.",
                "An object is considered safe when it has been inspected and is not dangerous.",
            ],
            "group": "inspected_not_dangerous",
        },
        {
            "head": "available(X)",
            "body": ["employee(X)", "\\+ busy(X)"],
            "templates": [
                "An employee is available if they are not busy.",
                "Any employee who is not busy is available.",
                "If someone is an employee and is not busy, then they are available.",
                "Being an employee who is not busy makes someone available.",
                "An employee can be considered available when there is no evidence they are busy.",
            ],
            "group": "employee_not_busy",
        },
        {
            "head": "different_parent(X, Y)",
            "body": ["parent(X, Z)", "parent(Y, Z)", "X \\= Y"],
            "templates": [
                "X and Y are different parents if they both parent Z and are not the same person.",
                "Two distinct people are different parents when they share a child.",
                "If X and Y are both parents of Z and X is not Y, then they are different parents.",
                "People who share a child but are not the same individual are different parents.",
                "Two people count as different parents when they parent the same person and are distinct.",
            ],
            "group": "shared_child_inequality",
        },
    ]

    examples = []
    two_condition_candidates = []
    three_condition_candidates = []
    special_candidates = []

    for rule in two_condition_rules:
        for template in rule["templates"]:
            two_condition_candidates.append(
                (
                    rule["head"],
                    rule["body"],
                    template,
                    rule["group"],
                )
            )

    for rule in three_condition_rules:
        for template in rule["templates"]:
            three_condition_candidates.append(
                (
                    rule["head"],
                    rule["body"],
                    template,
                    rule["group"],
                )
            )

    for rule in special_rules:
        for template in rule["templates"]:
            special_candidates.append(
                (
                    rule["head"],
                    rule["body"],
                    template,
                    rule["group"],
                )
            )

    def expand_candidates(candidates, target):
        expanded = []

        while len(expanded) < target:
            batch = candidates.copy()
            random.shuffle(batch)
            expanded.extend(batch)

        return expanded[:target]

    two_condition_candidates = expand_candidates(
        two_condition_candidates,
        300
    )

    three_condition_candidates = expand_candidates(
        three_condition_candidates,
        150
    )

    special_candidates = expand_candidates(
        special_candidates,
        50
    )

    all_candidates = (
        two_condition_candidates
        + three_condition_candidates
        + special_candidates
    )

    random.shuffle(all_candidates)

    for example_number, (head, body, template, group) in enumerate(
        all_candidates,
        start=1
    ):
        prolog = f"{head} :- {', '.join(body)}."

        examples.append(
            create_example(
                example_id=f"multi_{example_number:04d}",
                level=3,
                category="multi_condition_rule",
                natural_language=template,
                prolog=prolog,
                template_group=group,
            )
        )

    return examples

def generate_reasoning():
    names = [
        "ash", "brook", "ciel", "dio", "edward", "faust",
        "gary", "haku", "irina", "joseph", "kai", "luffy",
        "mary", "nathan", "olivia", "petra", "quistis", "ray",
        "sinbad", "tanya", "usagi", "violet", "wendy", "xeno",
        "yuri", "zelda"
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
        ("programmer", "technologist")
    ]

    for i in range(100):
        name = names[i % len(names)]
        source, target = classifications[i % len(classifications)]

        expected = i % 2 == 0

        if expected:
            query_name = name
        else:
            query_name = names[(i + 7) % len(names)]

        natural_language = (
            f"{name.capitalize()} is a {source}. "
            f"Every {source} is a {target}. "
            f"Is {query_name.capitalize()} a {target}?"
        )

        prolog = (
            f"{source}({name}).\n"
            f"{target}(X) :- {source}(X)."
        )

        query = f"{target}({query_name})."

        examples.append(
            create_example(
                example_id=f"reasoning_{example_number:04d}",
                level=4,
                category="reasoning",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"classification_{source}_{target}",
                query=query,
                expected_result=expected
            )
        )

        example_number += 1

    for i in range(100):
        first = names[i % len(names)]
        second = names[(i + 1) % len(names)]
        third = names[(i + 2) % len(names)]

        expected = i % 2 == 0

        if expected:
            query_target = third
        else:
            query_target = names[(i + 8) % len(names)]

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

        query = f"grandparent({first}, {query_target})."

        examples.append(
            create_example(
                example_id=f"reasoning_{example_number:04d}",
                level=4,
                category="reasoning",
                natural_language=natural_language,
                prolog=prolog,
                template_group="grandparent_reasoning",
                query=query,
                expected_result=expected
            )
        )

        example_number += 1

    condition_sets = [
        ("eligible", "adult", "citizen"),
        ("can_drive", "adult", "has_licence"),
        ("employable", "qualified", "available"),
        ("healthy", "exercises", "eats_well"),
        ("trusted_employee", "honest", "reliable"),
        ("research_candidate", "student", "interested_in_research"),
        ("dangerous", "armed", "hostile"),
        ("team_member", "employee", "assigned_to_team")
    ]

    for i in range(100):
        name = names[i % len(names)]
        result, condition_one, condition_two = condition_sets[
            i % len(condition_sets)
        ]

        expected = i % 2 == 0

        if expected:
            facts = (
                f"{condition_one}({name}).\n"
                f"{condition_two}({name}).\n"
            )

            natural_language = (
                f"{name.capitalize()} satisfies {condition_one.replace('_', ' ')} "
                f"and {condition_two.replace('_', ' ')}. "
                f"Anyone satisfying both conditions is {result.replace('_', ' ')}. "
                f"Is {name.capitalize()} {result.replace('_', ' ')}?"
            )

        else:
            facts = f"{condition_one}({name}).\n"

            natural_language = (
                f"{name.capitalize()} satisfies {condition_one.replace('_', ' ')}. "
                f"There is no statement that {name.capitalize()} satisfies "
                f"{condition_two.replace('_', ' ')}. "
                f"Both conditions are required to be {result.replace('_', ' ')}. "
                f"Is {name.capitalize()} {result.replace('_', ' ')}?"
            )

        prolog = (
            facts
            + f"{result}(X) :- "
            f"{condition_one}(X), "
            f"{condition_two}(X)."
        )

        query = f"{result}({name})."

        examples.append(
            create_example(
                example_id=f"reasoning_{example_number:04d}",
                level=4,
                category="reasoning",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"conjunction_{result}",
                query=query,
                expected_result=expected
            )
        )

        example_number += 1

    negation_rules = [
        ("can_fly", "bird", "flightless"),
        ("available", "employee", "busy"),
        ("safe", "inspected", "dangerous"),
        ("allowed_entry", "registered", "banned"),
        ("active", "member", "suspended")
    ]

    for i in range(100):
        name = names[i % len(names)]
        result, positive_condition, negative_condition = negation_rules[
            i % len(negation_rules)
        ]

        expected = i % 2 == 0

        if expected:
            facts = f"{positive_condition}({name}).\n"

            natural_language = (
                f"{name.capitalize()} is {positive_condition.replace('_', ' ')}. "
                f"There is no evidence that {name.capitalize()} is "
                f"{negative_condition.replace('_', ' ')}. "
                f"Someone is {result.replace('_', ' ')} if they satisfy the first "
                f"condition and are not {negative_condition.replace('_', ' ')}. "
                f"Is {name.capitalize()} {result.replace('_', ' ')}?"
            )

        else:
            facts = (
                f"{positive_condition}({name}).\n"
                f"{negative_condition}({name}).\n"
            )

            natural_language = (
                f"{name.capitalize()} is {positive_condition.replace('_', ' ')} "
                f"and is also {negative_condition.replace('_', ' ')}. "
                f"Someone is {result.replace('_', ' ')} only if they satisfy the "
                f"first condition and are not {negative_condition.replace('_', ' ')}. "
                f"Is {name.capitalize()} {result.replace('_', ' ')}?"
            )

        prolog = (
            facts
            + f"{result}(X) :- "
            f"{positive_condition}(X), "
            f"\\+ {negative_condition}(X)."
        )

        query = f"{result}({name})."

        examples.append(
            create_example(
                example_id=f"reasoning_{example_number:04d}",
                level=4,
                category="reasoning",
                natural_language=natural_language,
                prolog=prolog,
                template_group=f"negation_{result}",
                query=query,
                expected_result=expected
            )
        )

        example_number += 1

    return examples

def generate_dataset():
    random.seed(RANDOM_SEED)

    dataset = []

    dataset.extend(generate_facts())
    dataset.extend(generate_simple_rules())
    dataset.extend(generate_multi_condition_rules())
    dataset.extend(generate_reasoning())

    ids = [example["id"] for example in dataset]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate example IDs found.")

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