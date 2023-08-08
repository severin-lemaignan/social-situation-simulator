Social Situation Simulator
==========================

A tool to create, visualize, annotate and analyse social situations.

![screenshot](doc/screenshot.png)


Usage
-----

- Ensure PySide6 is installed (`pip3 install pyside6`)
- `socialsituationsimulator.py`

Analysis
--------

### Extracting social sequences

If you export a social situation to a JSON file, you can then post-process it
and analyse it with `analyse.py`.

Check `./analyse.py -h` for the main options.

For instance, the following example takes a `situation_1.json` scene created in
the simulator, and generate *for each agent* and *at every timepoint* in the
scene a sequence of scene descriptions, as viewed by that agent, for the 4
seconds preceding that timepoint (and at 2 fps):

```
./analyse.py --egocentric -l 4 -s 2 -c situation_1-normalised-egocentric.csv situation_1.json
```

This sequence represent the evolution of the social situation, as perceived by
that agent, for a 4-seconds time window.

The description are normalised: an similar social situation, viewed by a
different agent, will have the exact same description (eg, same strings).

By default, this tool will also replace the names of the agents by *templated
slots* like `{A}`, `{B}`,... so that new identical descriptions with different
name can later be generated.

### Computing social embeddings

The script `compute_embeddings.py` then compute the social embeddings for each
of these descriptions.

Check `./compute_embeddings.py --help` for all the options.

For instance, the following call will parse all the descriptions in
`situation_1-normalised-egocentric.csv`.
Then, for each unique one:
 - it creates random 'variations' by randomizing the order of the descriptors;
 - replace with name templates with random names;
 - compute the resulting embedding (currently using OpenAI `text-embedding-ada-002`)

```
./compute_embeddings.py situation_1-normalised-egocentric.csv situation_1-normalised-egocentric-embeddings.csv
```

