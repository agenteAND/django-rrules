# django-rrules version alpha

#### This a App to work based in [dateutil.rrule](https://github.com/dateutil/dateutil/) module to work with recurrence dates
This App aims to be more flexible than[ django-reccurence](https://github.com/django-recurrence/django-recurrence)

# install 
git clone https://github.com/agenteAND/django-rrules.git

## Usage
```python
# models.py
from django.db import models
from djangorrules.models import Recurrence

class Event(models.Model):
    e_name = models.CharField(max_length=100)
    e_something = models.CharField(max_length=30)
    recurrence = models.ForeignKey(Recurrence, related_name='recurrences', related_query_name='recurrence')
```

```ssh
# terminal
In [1] from djangorrules.models import Rule, Recurrence, RDate
In [2] from datetime import datetime
In [3] dt = datetime(1993, 7, 25)
In [4]: daily = Rule(recurrence=re, dtstart=dt, freq=Rule.DAILY, freq_type=Rule.COUNT, interval=1,  count=20)                                                                                           

In [5]: daily                                                                                                                                                                          
Out[5]: <Rule: daily, for 20 occurrences>

In [6]: str(daily)                                                                                                                                                                     
Out[6]: 'daily, for 20 occurrences'

In [7]: daily.to_dateutil_rule                                                                                                                                                        
Out[8]: <dateutil.rrule.rrule at 0x7f0710aca898>77
In [17]: for date in daily.to_dateutil_rule: 
    ...:     print(date) 
    ...:                                                                                                                                                                               
1993-07-25 05:03:07-04:00
1993-07-26 05:03:07-04:00
1993-07-27 05:03:07-04:00
1993-07-28 05:03:07-04:00
1993-07-29 05:03:07-04:00
1993-07-30 05:03:07-04:00
1993-07-31 05:03:07-04:00
1993-08-01 05:03:07-04:00
1993-08-02 05:03:07-04:00
1993-08-03 05:03:07-04:00
1993-08-04 05:03:07-04:00
1993-08-05 05:03:07-04:00
1993-08-06 05:03:07-04:00
1993-08-07 05:03:07-04:00
1993-08-08 05:03:07-04:00
1993-08-09 05:03:07-04:00
1993-08-10 05:03:07-04:00
1993-08-11 05:03:07-04:00
1993-08-12 05:03:07-04:00
1993-08-13 05:03:07-04:00

my_birthday = Rule(recurrence=re, dtstart=dt, freq=Rule.YEARLY, bymonth=['7'], bymonthday=['25'], freq_type=Rule.COUNT, interval=1,  count=27) 
In [25]: str(my_birthday)                                                                                                                                                              
Out[25]: 'annually, in Jul, on the 25th, for 27 occurrences'

In [26]: for date in my_birthday.to_dateutil_rule: 
    ...:     print(date) 
    ...:                                                                                                                                                                               
1993-07-25 05:03:07-04:00
1994-07-25 05:03:07-04:00
1995-07-25 05:03:07-04:00
1996-07-25 05:03:07-04:00
1997-07-25 05:03:07-04:00
1998-07-25 05:03:07-04:00
1999-07-25 05:03:07-04:00
2000-07-25 05:03:07-04:00
2001-07-25 05:03:07-04:00
2002-07-25 05:03:07-04:00
2003-07-25 05:03:07-04:00
2004-07-25 05:03:07-04:00
2005-07-25 05:03:07-04:00
2006-07-25 05:03:07-04:00
2007-07-25 05:03:07-04:00
2008-07-25 05:03:07-04:00
2009-07-25 05:03:07-04:00
2010-07-25 05:03:07-04:00
2011-07-25 05:03:07-04:00
2012-07-25 05:03:07-04:00
2013-07-25 05:03:07-04:00
2014-07-25 05:03:07-04:00
2015-07-25 05:03:07-04:00
2016-07-25 05:03:07-04:00
2017-07-25 05:03:07-04:00
2018-07-25 05:03:07-04:00
2019-07-25 05:03:07-04:00

In [29]: rules = Rule(recurrence=re, dtstart=dt, freq=Rule.YEARLY, bymonth=['7'], byweekday=['MO', 'WE'], freq_type=Rule.COUNT, interval=1, count=30, bysetpos=['-1', '2'])            
In [31]: rules.rule_to_text()                                                                                                                                                          
Out[31]: 'annually, in July, on the Monday or Wednesday, only the last or second instance, for 30 occurrences'

and more .... 
```

coming soon I will add unittest and implement the pip install
and more documentation.

PS: this app works, but use it at your own risk
i'm not an expert contributions are welcome at this stage of development.