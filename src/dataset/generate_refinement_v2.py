import json
import random
from pathlib import Path

SEED = 4242564

OUTPUT_PATH = Path(
    "dataset/refinement/targeted_v2.jsonl"
)

TARGET_EXAMPLES = 250

random.seed(SEED)

NAMES = [
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

FACT_GROUPS = [
    {
        "template_group": "refine_helps",
        "predicate": "helps",
        "templates": [
            "{a} assists {b}.",
            "{a} provides help to {b}.",
            "{a} gives assistance to {b}.",
            "{a} lends a hand to {b}.",
            "{a} offers support to {b}."
        ]
    },
    {
        "template_group": "refine_visits",
        "predicate": "visits",
        "templates": [
            "{a} pays a visit to {b}.",
            "{a} goes to see {b}.",
            "{a} visits {b}.",
            "{a} calls in on {b}.",
            "{a} goes to meet {b}."
        ]
    },
    {
        "template_group": "refine_teaches",
        "predicate": "teaches",
        "templates": [
            "{a} teaches {b}.",
            "{a} provides lessons to {b}.",
            "{a} instructs {b}.",
            "{a} gives tuition to {b}.",
            "{a} educates {b}."
        ]
    },
    {
        "template_group": "refine_follows",
        "predicate": "follows",
        "templates": [
            "{a} follows {b}.",
            "{a} goes after {b}.",
            "{a} trails behind {b}.",
            "{a} moves behind {b}.",
            "{a} keeps behind {b}."
        ]
    },
    {
        "template_group": "refine_respects",
        "predicate": "respects",
        "templates": [
            "{a} respects {b}.",
            "{a} has respect for {b}.",
            "{a} regards {b} with respect.",
            "{a} holds {b} in high regard.",
            "{a} shows respect towards {b}."
        ]
    }
]

SIMPLE_RULE_GROUPS = [
    {
        "template_group": "refine_supporter",
        "head": "supporter_of(X, Y)",
        "body": "helps(X, Y)",
        "templates": [
            "If X helps Y, then X is a supporter of Y.",
            "Anyone who helps another person acts as their supporter.",
            "When X provides help to Y, X is considered a supporter of Y.",
            "X is a supporter of Y whenever X helps Y.",
            "Helping Y makes X a supporter of Y."
        ]
    },
    {
        "template_group": "refine_mentor",
        "head": "mentor_of(X, Y)",
        "body": "teaches(X, Y)",
        "templates": [
            "If X teaches Y, then X is a mentor of Y.",
            "Anyone who teaches Y acts as a mentor to Y.",
            "Teaching Y makes X a mentor of Y.",
            "X is Y's mentor whenever X teaches Y.",
            "When X teaches Y, X is considered Y's mentor."
        ]
    },
    {
        "template_group": "refine_companion",
        "head": "companion_of(X, Y)",
        "body": "travels_with(X, Y)",
        "templates": [
            "If X travels with Y, then X is a companion of Y.",
            "Travelling with Y makes X a companion of Y.",
            "When X travels alongside Y, X is Y's companion.",
            "X is a companion of Y whenever X travels with Y.",
            "Anyone travelling with Y acts as a companion to Y."
        ]
    },
    {
        "template_group": "refine_guardian",
        "head": "guardian_of(X, Y)",
        "body": "protects(X, Y)",
        "templates": [
            "If X protects Y, then X is a guardian of Y.",
            "Anyone who protects Y acts as Y's guardian.",
            "Protecting Y makes X a guardian of Y.",
            "X is Y's guardian whenever X protects Y.",
            "When X protects Y, X is considered Y's guardian."
        ]
    },
    {
        "template_group": "refine_guide",
        "head": "guide_of(X, Y)",
        "body": "guides(X, Y)",
        "templates": [
            "If X guides Y, then X is a guide of Y.",
            "Anyone who guides Y acts as Y's guide.",
            "Guiding Y makes X a guide of Y.",
            "X is Y's guide whenever X guides Y.",
            "When X guides Y, X is considered Y's guide."
        ]
    },
    {
        "template_group": "refine_defender",
        "head": "defender_of(X, Y)",
        "body": "defends(X, Y)",
        "templates": [
            "If X defends Y, then X is a defender of Y.",
            "Anyone who defends Y acts as Y's defender.",
            "Defending Y makes X a defender of Y.",
            "X is Y's defender whenever X defends Y.",
            "When X defends Y, X is considered Y's defender."
        ]
    }
]

NEGATION_GROUPS = [
    {
        "template_group": "refine_member_not_suspended",
        "subject": "member",
        "result": "eligible",
        "head": "eligible(X)",
        "positive": "member(X)",
        "negative": "suspended(X)"
    },
    {
        "template_group": "refine_student_not_absent",
        "subject": "student",
        "result": "present",
        "head": "present(X)",
        "positive": "student(X)",
        "negative": "absent(X)"
    },
    {
        "template_group": "refine_device_not_broken",
        "subject": "device",
        "result": "usable",
        "head": "usable(X)",
        "positive": "device(X)",
        "negative": "broken(X)"
    },
    {
        "template_group": "refine_account_not_locked",
        "subject": "account",
        "result": "accessible",
        "head": "accessible(X)",
        "positive": "account(X)",
        "negative": "locked(X)"
    },
    {
        "template_group": "refine_worker_not_absent",
        "subject": "worker",
        "result": "available",
        "head": "available(X)",
        "positive": "worker(X)",
        "negative": "absent(X)"
    },
    {
        "template_group": "refine_vehicle_not_damaged",
        "subject": "vehicle",
        "result": "operational",
        "head": "operational(X)",
        "positive": "vehicle(X)",
        "negative": "damaged(X)"
    },
    {
        "template_group": "refine_candidate_not_disqualified",
        "subject": "candidate",
        "result": "eligible",
        "head": "eligible(X)",
        "positive": "candidate(X)",
        "negative": "disqualified(X)"
    },
    {
        "template_group": "refine_machine_not_faulty",
        "subject": "machine",
        "result": "operational",
        "head": "operational(X)",
        "positive": "machine(X)",
        "negative": "faulty(X)"
    },
    {
        "template_group": "refine_member_not_banned",
        "subject": "member",
        "result": "permitted",
        "head": "permitted(X)",
        "positive": "member(X)",
        "negative": "banned(X)"
    },
    {
        "template_group": "refine_document_not_archived",
        "subject": "document",
        "result": "active",
        "head": "active(X)",
        "positive": "document(X)",
        "negative": "archived(X)"
    }
]

NEGATION_TEMPLATES = [
    "A {subject} is {result} when there is no evidence that they are {negative}.",
    "Any {subject} is {result} unless they can be shown to be {negative}.",
    "If something is a {subject} and being {negative} cannot be established, it is {result}.",
    "Being a {subject} and not being provably {negative} implies being {result}.",
    "A {subject} counts as {result} provided no fact establishes that it is {negative}.",
    "Something known to be a {subject} is {result} unless evidence shows that it is {negative}.",
]

SHARED_RELATION_GROUPS = [
    {
        "template_group": "refine_same_team_inequality",
        "head": "teammate(X, Y)",
        "relation": "member_of",
        "shared_object": "team",
        "result": "teammates"
    },
    {
        "template_group": "refine_same_employer_inequality",
        "head": "coworker(X, Y)",
        "relation": "works_for",
        "shared_object": "organisation",
        "result": "coworkers"
    },
    {
        "template_group": "refine_same_course_inequality",
        "head": "classmate(X, Y)",
        "relation": "studies",
        "shared_object": "course",
        "result": "classmates"
    },
    {
        "template_group": "refine_same_city_inequality",
        "head": "co_resident(X, Y)",
        "relation": "lives_in",
        "shared_object": "city",
        "result": "co-residents"
    },
    {
        "template_group": "refine_same_club_inequality",
        "head": "clubmate(X, Y)",
        "relation": "belongs_to",
        "shared_object": "club",
        "result": "clubmates"
    },
    {
        "template_group": "refine_same_project_inequality",
        "head": "collaborator(X, Y)",
        "relation": "works_on",
        "shared_object": "project",
        "result": "collaborators"
    },
    {
        "template_group": "refine_same_teacher_inequality",
        "head": "fellow_student(X, Y)",
        "relation": "student_of",
        "shared_object": "teacher",
        "result": "fellow students"
    },
    {
        "template_group": "refine_same_house_inequality",
        "head": "housemate(X, Y)",
        "relation": "lives_at",
        "shared_object": "house",
        "result": "housemates"
    },
    {
        "template_group": "refine_same_department_inequality",
        "head": "colleague(X, Y)",
        "relation": "works_in",
        "shared_object": "department",
        "result": "colleagues"
    },
    {
        "template_group": "refine_same_group_inequality",
        "head": "groupmate(X, Y)",
        "relation": "member_of",
        "shared_object": "group",
        "result": "groupmates"
    }
]

SHARED_RELATION_TEMPLATES = [
    "Two different people are {result} when they share the same {object}.",
    "X and Y are {result} if both are associated with the same {object} Z and X differs from Y.",
    "People connected to the same {object} are {result} provided they are different people.",
    "If X and Y share {object} Z and X is not Y, then they are {result}.",
    "Sharing the same {object} makes two distinct people {result}.",
    "Two distinct individuals count as {result} whenever they share a {object}."
]

CONJUNCTION_GROUPS = [
    {
        "template_group": "refine_adult_member_authorised",
        "head": "authorised(X)",
        "condition_a": "adult",
        "condition_b": "member",
        "body": ["adult(X)", "member(X)"],
        "result": "authorised"
    },
    {
        "template_group": "refine_trained_certified_qualified",
        "head": "qualified(X)",
        "condition_a": "trained",
        "condition_b": "certified",
        "body": ["trained(X)", "certified(X)"],
        "result": "qualified"
    },
    {
        "template_group": "refine_registered_paid_active",
        "head": "active(X)",
        "condition_a": "registered",
        "condition_b": "paid",
        "body": ["registered(X)", "paid(X)"],
        "result": "active"
    },
    {
        "template_group": "refine_student_enrolled_valid",
        "head": "valid_student(X)",
        "condition_a": "student",
        "condition_b": "enrolled",
        "body": ["student(X)", "enrolled(X)"],
        "result": "a valid student"
    },
    {
        "template_group": "refine_member_verified_trusted",
        "head": "trusted(X)",
        "condition_a": "a member",
        "condition_b": "verified",
        "body": ["member(X)", "verified(X)"],
        "result": "trusted"
    },
    {
        "template_group": "refine_device_powered_connected_online",
        "head": "online(X)",
        "condition_a": "powered",
        "condition_b": "connected",
        "body": ["powered(X)", "connected(X)"],
        "result": "online"
    },
    {
        "template_group": "refine_employee_trained_ready",
        "head": "ready(X)",
        "condition_a": "an employee",
        "condition_b": "trained",
        "body": ["employee(X)", "trained(X)"],
        "result": "ready"
    },
    {
        "template_group": "refine_registered_verified_approved",
        "head": "approved(X)",
        "condition_a": "registered",
        "condition_b": "verified",
        "body": ["registered(X)", "verified(X)"],
        "result": "approved"
    }
]

CONJUNCTION_TEMPLATES = [
    "A person is {result} if they are {a} and {b}.",
    "Anyone who is both {a} and {b} is {result}.",
    "Being {a} together with being {b} implies being {result}.",
    "If someone is {a} and {b}, then they are {result}.",
    "Someone who is {a} and also {b} qualifies as {result}."
]

def make_id(number):
    return f"refine_v2_{number:04d}"

def build_example(
    number,
    level,
    category,
    natural_language,
    prolog,
    template_group,
    nl_template
):
    return {
        "id": make_id(number),
        "level": level,
        "category": category,
        "natural_language": natural_language,
        "prolog": prolog,
        "template_group": template_group,
        "nl_template": nl_template
    }

def generate_fact_example(number):
    group = random.choice(FACT_GROUPS)

    a, b = random.sample(NAMES, 2)

    template = random.choice(group["templates"])

    natural_language = template.format(
        a=a.capitalize(),
        b=b.capitalize()
    )

    prolog = (
        f"{group['predicate']}({a}, {b})."
    )

    return build_example(
        number=number,
        level=1,
        category="fact",
        natural_language=natural_language,
        prolog=prolog,
        template_group=group["template_group"],
        nl_template=template
    )

def generate_simple_rule_example(number):
    group = random.choice(SIMPLE_RULE_GROUPS)

    template = random.choice(group["templates"])

    prolog = (
        f"{group['head']} :- "
        f"{group['body']}."
    )

    return build_example(
        number=number,
        level=2,
        category="simple_rule",
        natural_language=template,
        prolog=prolog,
        template_group=group["template_group"],
        nl_template=template
    )

def generate_negation_example(number):
    group = random.choice(NEGATION_GROUPS)
    template = random.choice(NEGATION_TEMPLATES)

    negative_word = (
        group["negative"]
        .replace("(X)", "")
        .replace("_", " ")
    )

    natural_language = template.format(
        subject=group["subject"],
        result=group["result"],
        negative=negative_word
    )

    prolog = (
        f"{group['head']} :- "
        f"{group['positive']}, "
        f"\\+ {group['negative']}."
    )

    return build_example(
        number=number,
        level=3,
        category="multi_condition_rule",
        natural_language=natural_language,
        prolog=prolog,
        template_group=group["template_group"],
        nl_template=template
    )

def generate_shared_relation_example(number):
    group = random.choice(
        SHARED_RELATION_GROUPS
    )

    template = random.choice(
        SHARED_RELATION_TEMPLATES
    )

    natural_language = template.format(
        result=group["result"],
        object=group["shared_object"]
    )

    relation = group["relation"]

    prolog = (
        f"{group['head']} :- "
        f"{relation}(X, Z), "
        f"{relation}(Y, Z), "
        f"X \\= Y."
    )

    return build_example(
        number=number,
        level=3,
        category="multi_condition_rule",
        natural_language=natural_language,
        prolog=prolog,
        template_group=group["template_group"],
        nl_template=template
    )

def generate_conjunction_example(number):
    group = random.choice(
        CONJUNCTION_GROUPS
    )

    template = random.choice(
        CONJUNCTION_TEMPLATES
    )

    natural_language = template.format(
        result=group["result"],
        a=group["condition_a"],
        b=group["condition_b"]
    )

    body = ", ".join(group["body"])

    prolog = (
        f"{group['head']} :- "
        f"{body}."
    )

    return build_example(
        number=number,
        level=3,
        category="multi_condition_rule",
        natural_language=natural_language,
        prolog=prolog,
        template_group=group["template_group"],
        nl_template=template
    )

def generate_dataset():
    examples = []

    seen_pairs = set()

    generation_plan = (
        ["fact"] * 90
        + ["simple_rule"] * 30
        + ["negation"] * 50
        + ["shared_relation"] * 50
        + ["conjunction"] * 30
    )

    random.shuffle(generation_plan)

    attempts = 0

    while (
        len(examples) < TARGET_EXAMPLES
        and attempts < 10000
    ):
        attempts += 1

        generation_type = generation_plan[
            len(examples)
        ]

        number = len(examples) + 1

        if generation_type == "fact":
            example = generate_fact_example(
                number
            )

        elif generation_type == "simple_rule":
            example = generate_simple_rule_example(
                number
            )

        elif generation_type == "negation":
            example = generate_negation_example(
                number
            )

        elif generation_type == "shared_relation":
            example = generate_shared_relation_example(
                number
            )

        elif generation_type == "conjunction":
            example = generate_conjunction_example(
                number
            )

        else:
            raise ValueError(
                f"Unknown generation type: "
                f"{generation_type}"
            )

        pair = (
            example["natural_language"],
            example["prolog"]
        )

        if pair in seen_pairs:
            continue

        seen_pairs.add(pair)

        examples.append(example)

    if len(examples) != TARGET_EXAMPLES:
        raise RuntimeError(
            "Could not generate the requested "
            f"{TARGET_EXAMPLES} unique examples. "
            f"Generated {len(examples)}."
        )

    return examples

def save_jsonl(examples, path):
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        for example in examples:
            file.write(
                json.dumps(
                    example,
                    ensure_ascii=False
                )
                + "\n"
            )

def print_summary(examples):
    level_counts = {}
    category_counts = {}
    template_counts = {}

    for example in examples:
        level = example["level"]
        category = example["category"]
        template = example["template_group"]

        level_counts[level] = (
            level_counts.get(level, 0) + 1
        )

        category_counts[category] = (
            category_counts.get(
                category,
                0
            ) + 1
        )

        template_counts[template] = (
            template_counts.get(
                template,
                0
            ) + 1
        )

    print("===== V2 REFINEMENT DATASET =====")
    print(f"Seed: {SEED}")
    print(f"Total examples: {len(examples)}")

    print()
    print("===== BY LEVEL =====")

    for level in sorted(level_counts):
        print(
            f"Level {level}: "
            f"{level_counts[level]}"
        )

    print()
    print("===== BY CATEGORY =====")

    for category in sorted(
        category_counts
    ):
        print(
            f"{category}: "
            f"{category_counts[category]}"
        )

    print()
    print("===== BY TEMPLATE GROUP =====")

    for template in sorted(
        template_counts
    ):
        print(
            f"{template}: "
            f"{template_counts[template]}"
        )

    print()
    print(
        f"Saved to: {OUTPUT_PATH}"
    )

def main():
    examples = generate_dataset()

    save_jsonl(
        examples,
        OUTPUT_PATH
    )

    print_summary(examples)

if __name__ == "__main__":
    main()