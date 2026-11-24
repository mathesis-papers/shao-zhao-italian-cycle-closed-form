# Italian cycle-domination coefficients

The note proves a finite binomial sum for every labelled-cycle coefficient
`d_I(C_n, 2n-j)`, for `n >= 3` and `0 <= j <= 2n`. Its written proofs also
give a rational deficit generating function, a weighted order-five recurrence,
the sufficient polynomial stable range `n >= max(3,j+1)`, and the dominant
root that determines the limiting total-count ratio.
It also proves the exclusion polynomial has degree exactly `j-4` and
leading coefficient `2/(j-5)!` for `j >= 5`, proves the same limiting
ratio for paths, and gives the low-deficit Italian--Roman differences
and a star polynomial.

## Build

Use Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, compile with a standard LaTeX distribution:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is contained in `note.tex`; no BibTeX database, downloaded
figure, or other source dependency is required.

## Exact finite checks

Python 3.9 or newer, standard library only:

```sh
python3 verify.py > checks.json
```

The formula and boundary-conditioned enumeration agree at every coefficient
for cycle lengths 3 through 40. Direct enumeration of all candidate functions
provides a third comparison for lengths 3 through 10. Arithmetic is exact;
there is no floating-point tolerance. The output also specifies the finite
weighted-recurrence and fixed-deficit difference checks. These computations
are finite identities; the note supplies the general proofs.
Additional exact comparisons cover exclusion differences for `j=5,...,20`,
path counts at lengths 1 through 9, Roman differences at cycle lengths
3 through 10, and stars with 2 through 8 leaves. The nine-state matrix's
characteristic polynomial and strictly positive fourth power are checked
by exact integer matrix arithmetic.

## Formal statement coverage

`CycleDeficit.result` proves the coefficient identity for all `n >= 3` and
`j <= 2n`. `CycleItalianDominationRecurrence.result` proves the total-count
recurrence and its five initial values. The note links these exact declarations
at a fixed source revision. The weighted recurrence, generating function, and
polynomial stable range and growth limit are written proofs in the note.
The exclusion leading coefficient, path growth, Roman differences and star
polynomial also have written proofs; no further Lean declaration is claimed
for those conclusions.

## Attribution and license

Haobo Ma — ChronoAI Pte Ltd, Singapore.

Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore.

CC BY 4.0 (`cc-by-4.0`). The posed directions and prior low-deficit formulas
are attributed to Pingping Shao and Chengye Zhao in the note.
