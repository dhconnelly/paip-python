# defining lists in prolog

<- first(?x, pair(?x, ?more))
<- rest(?more, pair(?x, ?more))

<- member(?x, pair(?x, ?more))
<- member(?x, pair(?y, ?more)) :- member(?x, ?more)

<- length(nil, 0)
<- length(pair(?x, nil), inc(0))
<- length(pair(?first, ?rest), inc(?n)) :- length(?rest, ?n)
