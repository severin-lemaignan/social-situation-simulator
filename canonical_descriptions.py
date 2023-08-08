import re


def _canonical(desc, slot_mapping=None):

    # Step 1: re-order the descriptor by alphabetical order, ignoring the name's slots
    tokens = [x.strip() for x in desc.split(";")]
    naked_tokens = [re.sub(r"\{.*?\}", "", x) for x in tokens]

    canonical_form = "; ".join([x for _, x in sorted(zip(naked_tokens, tokens))])

    # Step 2: re-order the name slots by order of appearance
    slot_mapping = slot_mapping if slot_mapping else {}
    target_slots = "ABCDEFGHIJKLMNOPQRSTUVW"
    target_idx = len(slot_mapping)

    for match in re.findall(r"\{(.*?)\}", canonical_form):

        if match not in slot_mapping:
            slot_mapping[match] = target_slots[target_idx]
            target_idx += 1

    for k, v in slot_mapping.items():
        canonical_form = canonical_form.replace("{%s}" % k, "{%s__new__}" % v)

    canonical_form = canonical_form.replace("__new__", "")

    # Step 3: re-sort the descriptors by alphabetical order, including the names' slots
    # (as a consequence, the descriptors for person 'A' will be grouped together, follow by person 'B', etc
    canonical_form = "; ".join(sorted(canonical_form.split("; ")))

    return canonical_form, slot_mapping


def canonical(desc):

    desc, _ = _canonical(desc)
    return desc


def canonize(descriptions, maintain_mapping=True):
    """
    Return the canonical transformation of a set of descriptions, keeping the same
    remapping of names accross descriptions.
    """

    result = []
    desc, slot_mapping = _canonical(descriptions[0])
    result.append(desc)

    for desc in descriptions[1:]:
        desc, slot_mapping = _canonical(
            desc, slot_mapping if maintain_mapping else None
        )
        result.append(desc)

    return result, slot_mapping


if __name__ == "__main__":

    desc1 = "{A} is talking; {B} and {C} are looking at each other; {B} is not far from {C}; {D} and {A} are looking at each other"
    desc2 = "{A} is not far from {B}; {C} and {D} are looking at each other; {D} is talking; {A} and {B} are looking at each other"

    assert canonical(desc2) == canonical(desc1)

    descriptions = [
        "{A} and {B} are looking at each other; {C} and {D} are looking at each other; {D} is talking; {A} is not far from {B}",
        "{A} and {B} are looking at each other; {C} and {D} are looking at each other; {C} is not far from {B}; {D} is passing by; {A} is not far from {B}",
        "{A} and {B} are looking at each other; {C} and {D} are looking at each other; {A} is walking towards {B}; {C} is not far from {B}; {A} is not far from {B}",
        "{A} is walking towards {B}; {C} is not far from {B}; {A} is not far from {B}",
        "{A} is walking towards {B}; {C} is not far from {B}; {A} is not far from {B}",
        "{C} is looking at {B}; {A} is walking towards {B}; {C} is not far from {B}; {A} is not far from {B}",
        "{C} is looking at {B}; {A} is walking towards {B}; {C} is not far from {B}; {A} is not far from {B}",
    ]

    descriptions2 = [
        "{B} is looking at {A}; {B} is not far from {C}",
        "{A} and {B} are looking at each other; {A} is talking; {C} and {D} are looking at each other; {D} is walking towards {C}; {D} is not far from {C}; {B} is not far from {C}; {B} is talking; {E} is talking",
        "{A} and {B} are looking at each other; {A} is talking; {C} and {D} are looking at each other; {D} is walking towards {C}; {D} is not far from {C}; {B} is not far from {C}; {B} is talking; {D} is talking; {E} is talking",
        "{A} and {B} are looking at each other; {D} is walking towards {C}; {D} is not far from {C}; {B} is not far from {C}; {D} is talking",
        "{D} is not far from {C}; {C} and {D} are looking at each other; {D} is talking; {D} is walking towards {C}",
        "{A} and {B} are looking at each other; {C} and {D} are looking at each other; {A} is walking away from {C}; {D} is walking towards {C}; {D} is not far from {C}; {B} is not far from {C}",
        "{A} and {B} are looking at each other; {C} and {D} are looking at each other; {D} is walking towards {C}; {D} is not far from {C}; {B} is not far from {C}",
    ]

    desc3 = "{A} is walking towards {C}; {C} and {B} are looking at each other; {C} is talking; {B} is talking"

    print()
    for d in canonize(descriptions)[0]:
        print(d)

    print()
    for d in canonize(descriptions2)[0]:
        print(d)
