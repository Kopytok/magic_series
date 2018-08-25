# Magic series

Search for the Magic series using constraints programming.

## Definition
A series ![Series](https://latex.codecogs.com/gif.latex?S%3D%28S_0%2C%20S_1%2C%20...%2C%20S_n%29) is magic if ![S_i](https://latex.codecogs.com/gif.latex?S_i) represents the number of occurences of ![i](https://latex.codecogs.com/gif.latex?i) in ![S](https://latex.codecogs.com/gif.latex?S)


|   | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
|Occurences| ? | ? | ? | ? | ? |

**Ex**:

|   | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
|Occurences| 2 | 1 | 2 | 0 | 0 |

Series [2, 1, 2, 0, 0] satisfies the definition, because:

 - 2 occurences of 0
 - 1 occurence&nbsp;&nbsp;  of 1
 - 2 occurences of 2
 - 0 occurences of 3
 - 0 occurences of 4

## Concepts used

### Reification

From definition: `series[k] == sum(series[i] == k)`.

Let's expand the formula for `length = 5`:

```
series[0] = (series[0] == 0) + (series[1] == 0) + (series[2] == 0) + (series[3] == 0) + (series[4] == 0)
series[1] = (series[0] == 1) + (series[1] == 1) + (series[2] == 1) + (series[3] == 1) + (series[4] == 1)
series[2] = (series[0] == 2) + (series[1] == 2) + (series[2] == 2) + (series[3] == 2) + (series[4] == 2)
series[3] = (series[0] == 3) + (series[1] == 3) + (series[2] == 3) + (series[3] == 3) + (series[4] == 3)
series[4] = (series[4] == 4) + (series[1] == 4) + (series[2] == 4) + (series[3] == 4) + (series[4] == 4)
```

What if `series[2] = 1`?

```
series[0] = (series[0] == 0) + (series[1] == 0) + 0 + (series[3] == 0) + (series[4] == 0)
series[1] = (series[0] == 1) + (series[1] == 1) + 1 + (series[3] == 1) + (series[4] == 1)
1         = (series[0] == 2) + (series[1] == 2) + 0 + (series[3] == 2) + (series[4] == 2)
series[3] = (series[0] == 3) + (series[1] == 3) + 0 + (series[3] == 3) + (series[4] == 3)
series[4] = (series[4] == 4) + (series[1] == 4) + 0 + (series[3] == 4) + (series[4] == 4)
```

But now `series[1] > 0`, that means, that the domain can be simplified:

```
series[0] = (series[0] == 0) +                      + (series[3] == 0) + (series[4] == 0)
series[1] = (series[0] == 1) + (series[1] == 1) + 1 + (series[3] == 1) + (series[4] == 1)
1         = (series[0] == 2) + (series[1] == 2)     + (series[3] == 2) + (series[4] == 2)
series[3] = (series[0] == 3) + (series[1] == 3)     + (series[3] == 3) + (series[4] == 3)
series[4] = (series[4] == 4) + (series[1] == 4)     + (series[3] == 4) + (series[4] == 4)
```

To check if value `x` is equal to `v`, the following constraint is used:

```
((b == 1) & (x == v)) | ((b == 0) & (x != v))
```

Which means, that we take all reified constraints and replace them with ternary constraints and new boolean variables `b`. That concept is realised in class `Domain`.

### Constraints

```
sum(series[k])     == length
sum(series[k] * k) == length
```

 - Fill in the last missing value in column.
 - Choose the last missing number in series.
 - Fill missing values in row with `0`, if sum of the row is already equal to the number in postion.
 - Choose number, if corresponding row is already known.
 - Fill with `0` values, which are less than the current sum of the row. For example, if there's already two `1`s, that means, that value in position is >= 2.

All constraints are implemented in `prune.py`
