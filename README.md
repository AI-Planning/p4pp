# (p4pp) Planning tools for planning pedagogy

Tools for grading planning assignments.

## TODO

- [x] Make `src/` and move files there (updating docs and scripts)
- [x] Parameterize where the reference and assignment files are
- [ ] Create an example and show it in usage
- [ ] Make public

## Building

Assuming you already have `planutils` installed and working, you can just run `./setup.sh`. Alternatively, you can run things through the included docker image.

## Docker

Perhaps the most convenient way to use this, is to run it through a preconfigured Docker image. To build:

```bash
docker build -t p4pp .
```

Running the image on Linux with a mirrored directory for the assignment PDDL:

```bash
docker run -it --privileged -v $(pwd):/DATA p4pp
```

It assumes that the current directory has both `assignments` and `reference` subdirectories.

## Usage

Coming soon...

## Requirements

If installing locally, you will need the following installed:

- `tabulate`
- `tarski[gringo]`
- `planutils`

From `planutils`, you'll need both `lama-first` and `val` installed.

Alternatively, you can run everything from the included Docker image.

## Citing This Work

Coming soon...
