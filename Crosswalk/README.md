# Crosswalk Directory

This directory will contain the generated crosswalk files.

## Output Format

```
Crosswalk/
└── Crosswalk_2000_1980.xlsx
```

The Excel files contain the following columns:
- CITY2000/CITY1980: City names in respective years
- PREF2000/PREF1980: Prefecture names
- GUN2000/GUN1980: District names
- City Code 2000/1980: 5-digit administrative codes
- weight: Area-based weight for crosswalking

Note: These files are generated by the crosswalk creation process and should not be committed to version control. 