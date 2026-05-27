# Shortcut Methods Summary

## Fenske (minimum stages)

For a binary or pseudo-binary cut at total reflux:

    N_min = log[(xD / (1 - xD)) * ((1 - xB) / xB)] / log(alpha)

`alpha` is the geometric mean of top and bottom relative volatilities. The
result includes the reboiler as an equilibrium stage. Assumes constant
`alpha` across the column.

## Underwood (minimum reflux)

Solve for `theta` in:

    sum_i [ alpha_i * z_i / (alpha_i - theta) ] = 1 - q

with `alpha_HK < theta < alpha_LK`. Then:

    Rmin + 1 = sum_i [ alpha_i * xD_i / (alpha_i - theta) ]

`q` is the feed thermal condition (1.0 sat liquid, 0.0 sat vapor).

## Gilliland (actual stages)

The Molokanov closed-form approximation:

    X = (R - Rmin) / (R + 1)
    Y = 1 - exp[ (1 + 54.4 X) / (11 + 117.2 X) * (X - 1) / sqrt(X) ]
    N = (Nmin + Y) / (1 - Y)

The Gilliland correlation is empirical; reported deviations are typically
within ±10%.

## McCabe-Thiele (binary, constant alpha)

Operating lines:
- Rectifying: `y = R/(R+1) * x + xD/(R+1)`
- Stripping: passes through `(xB, xB)` and the intersection of the
  rectifying line with the q-line.

q-line: `y = q/(q-1) * x - xF/(q-1)` for `q != 1`; vertical at `x = xF` for
`q = 1`.

Stage stepping uses the equilibrium relation
`y = alpha x / (1 + (alpha - 1) x)` repeatedly between operating lines.

## Feed stage rule of thumb

Optimum feed stage is the stage at which the operating-line switch occurs in
the McCabe-Thiele construction. The Fenske/Underwood/Gilliland approach
estimates the feed-stage *ratio* via the Kirkbride equation, which is not
implemented here; consult Seader for that step.
