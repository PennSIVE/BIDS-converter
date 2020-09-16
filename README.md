# BIDS converter

Usage:
```
usage: main.py [-h] [-p P] [-s S] [-ss SS] [-m M] [-o O] [--symlink]
               [--no-symlink] [--t1-labels T1_LABELS [T1_LABELS ...]]
               [--t2-labels T2_LABELS [T2_LABELS ...]]
               [--flair-labels FLAIR_LABELS [FLAIR_LABELS ...]]
               [--pd-labels PD_LABELS [PD_LABELS ...]]
               sub

Pattern-match Nifti directories to create BIDS dataset

positional arguments:
  sub                   sub command

optional arguments:
  -h, --help            show this help message and exit
  -p P                  Path to Niftis with placeholders specifying subject,
                        session, modality
  -s S                  Subject
  -ss SS                Session
  -m M                  Modality
  -o O                  Output directory
  --symlink             copy source niftis to destination using
                        symlinks/aliases
  --no-symlink          (deep) copy source niftis to destination
  --t1-labels T1_LABELS [T1_LABELS ...]
                        T1 labels
  --t2-labels T2_LABELS [T2_LABELS ...]
                        T2 labels
  --flair-labels FLAIR_LABELS [FLAIR_LABELS ...]
                        FLAIR labels
  --pd-labels PD_LABELS [PD_LABELS ...]
                        PD labels

```