# (p4pp) Planning tools for planning pedagogy

Tools for grading planning assignments.

## Building

Assuming you already have `planutils` installed and working, you can just run `./setup.sh`. Alternatively, you can run things through the included docker image.

## Docker

Perhaps the most convenient way to use this, is to run it through a preconfigured Docker image. To build:

```bash
docker build -t p4pp .
```

Running the image on Linux with a mirrored directory for the assignment PDDL:

```bash
docker run -it --privileged -v $(pwd):/PROJECT/data  p4pp
```

It assumes that the current directory has both `assignments`, `reference`, and `marking` subdirectories.

## Usage

First step is to configure the top of `grade.py` for the problem names and directories. If you built and ran the docker image with the commands above, then it will work by default if you run from the `example/` directory.

### Grading a single assignment

```bash
python3 grade.py <assignment ID>
```

### Grading all assignments

```bash
python3 grade.py all
```

### Viewing the results

In the `marking/` directory, you can view the results of the grading. `grade.txt` shows the combined results, and all the generated files are also sitting there.

## Requirements

If installing locally, you will need the following installed:

- `tabulate`
- `tarski[gringo]`
- `planutils`

From `planutils`, you'll need both `lama-first` and `val` installed.

Alternatively, you can run everything from the included Docker image.

## Citing This Work

```latex
@inproceedings{macq-keps-2022,
  author    = {Alex Coulter and Teo Ilie and Renee Tibando and Christian Muise},
  title     = {Theory Alignment via a Classical Encoding of Regular Bisimulation},
  booktitle = {The ICAPS Workshop on Knowledge Engineering for Planning and Scheduling (KEPS)},
  year      = {2022}
}
```
