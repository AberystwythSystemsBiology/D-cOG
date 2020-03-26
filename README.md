# D-cOG

> This project is currently under development.

## Codepen

```bash
awk 'BEGIN {n_seq=0;} /^>/ {if(n_seq%50000==0){file=sprintf("myseq%d.fa",n_seq);} print >> file; n_seq++; next;} { print >> file; }' < e5.proteomes.faa
```

## Authors

- Nicholas Dimonaco <nid16@aber.ac.uk>
- Keiron O'Shea <keo7@aber.ac.uk>