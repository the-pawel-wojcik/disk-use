# Disk use
Plot disk use over time by directory.

## Generate the input data
For a daily summary use
```bash
file_name=$(date +%Y-%m-%d).txt

du -s * | sort -nr > $file_name
```
