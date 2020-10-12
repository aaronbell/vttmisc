# vttmisc

A library that contains a small set of scripts related to working with [VTT](https://docs.microsoft.com/en-us/typography/tools/vtt/). 

## Installation and Usage

Vttmisc can be called via a build script, or directly from the command line.

```
$ pip install vttmisc
$ python vttmisc [-h] [--fix-offset] [--clear-svtca] [--makeCVAR] -i INPUTPATH [-s VTTPATH] [-d OUTPUT]
```

Options are as follows:

`--clear-svtca`
This script clears the "SVTCA[X]" tag from your VTT source files (specifically in the TSI1 table) as these can cause misalignments of diacritical marks. I suggest using this script after autohinting.

`--fix-offset`
This script overcomes the GID restictions placed in the font due to use of the OFFSET command. It takes a source font, and a new font, and updates the new font with the appropriate GIDs. 

`--makeCVAR`
This script generates a cvar table based on the TSIC table. Under most circumstances, output matches VTT's identically.*

*If you are doing more complex cvar modification, please double check. Most likely more complicated ones will need to go through VTT or varlib.

Additional settings:

`-i` input path of new font (required)

`-s` input path of source VTT font (required for makeCVAR)

`-d` output path (optional: script will export using a default name if not provided)

