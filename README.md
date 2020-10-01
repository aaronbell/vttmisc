# vttmisc

A library that contains a small set of scripts related to working with [VTT](https://docs.microsoft.com/en-us/typography/tools/vtt/). 

1) Remove SVTCA[X] - This script clears the "SVTCA[X]" tag from your VTT source files (specifically in the TSI1 table) as these can cause misalignments of diacritical marks. I suggest using this script after autohinting.

2) Fix OFFSET - This script overcomes the GID restictions placed in the font due to use of the OFFSET command. It takes a source font, and a new font, and updates the new font with the appropriate GIDs. 

3) MakeCVAR - This script generates a cvar table based on the TSIC table. Under most circumstances, output matches VTT's identically.*

*If you are doing more complex cvar modification, please double check. Most likely more complicated ones will need to go through VTT or varlib.

## Installation and Usage

```
$ pip install vttmisc
```
