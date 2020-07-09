import re
import pytz
from datetime import datetime, time
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import dateformat, timezone
from django.utils.translation import gettext_lazy as _, pgettext as _p

from django.core.exceptions import ValidationError
from multiselectfield import MultiSelectField
from dateutil.rrule import weekday, rrule, rruleset, rrulestr

from .utils import join_with_conjunction


class Recurrence(models.Model):
    """
    generate a dateutil rruleset

    The rruleset type allows more complex recurrence setups, mixing multiple rules,
    dates, exclusion rules, and exclusion dates. The type constructor takes the following
    keyword arguments:

    rruleset methods
    The following methods are available:

    rruleset.rrule(rrule)
    Include the given rrule instance in the recurrence set generation.

    rruleset.rdate(dt)
    Include the given datetime instance in the recurrence set generation.

    rruleset.exrule(rrule)
    Include the given rrule instance in the recurrence set exclusion list. Dates which
    are part of the given recurrence rules will not be generated, even if some inclusive
    rrule or rdate matches them.

    rruleset.exdate(dt)
    Include the given datetime instance in the recurrence set exclusion list. Dates included
    that way will not be generated, even if some inclusive rrule or rdate matches them.

    rruleset.before(dt, inc=False)
    Returns the last recurrence before the given datetime instance. The inc keyword defines
    what happens if dt is an occurrence. With inc == True, if dt itself is an occurrence, it
    will be returned.

    rruleset.after(dt, inc=False)
    Returns the first recurrence after the given datetime instance. The inc keyword defines
    what happens if dt is an occurrence. With inc == True, if dt itself is an occurrence,
    it will be returned.

    rruleset.between(after, before, inc=False)
    Returns all the occurrences of the rrule between after and before. The inc keyword defines
    what happens if after and/or before are themselves occurrences. With inc == True, they will
    be included in the list, if they are found in the recurrence set.

    rruleset.count()
    Returns the number of recurrences in this set. It will have go trough the whole recurrence,
    if this hasn't been done before.

    more in: http://labix.org/python-dateutil/#head-717a8f5a506d997f07db99aeb71b76ea991f9309

    Besides these methods, rruleset instances also support the __getitem__() and __contains__() special methods
    """

    # set a fixed time because all instances must have the same
    # hour time - otherwise the exclude rules not working correctly
    TIME = time(hour=12, minute=0, second=0)
    TIME_ZONE_LIST = [
        (tz, tz) for tz in pytz.all_timezones
    ]

    timezone = models.CharField(max_length=30, choices=TIME_ZONE_LIST)

    def __str__(self):
        return _("recurrence #%(pk)s timezone: %(timezone)s rules: %(rules)d rdates: %(dates)s") % {
            'pk': self.pk,
            'timezone': self.timezone,
            'rules': self.rules.all().count(),
            'dates': self.r_dates.all().count()
        }

    def to_dateutil_ruleset(self, cache=False):
        """
        get a dateutil rruleset object
        exdate method needs a datetime with same time part of dtstart
        because dtstart is the base for the recurrence
        """
        recurrence_tz = pytz.timezone(self.timezone)
        rule_set = rruleset(cache=cache)
        rules = self.rules.all()
        r_dates = self.r_dates.all()

        if rules.exists():
            for rule in rules:
                dateutil_object = rule.to_dateutil_rule
                if rule.exclude:
                    rule_set.exrule(dateutil_object)
                else:
                    rule_set.rrule(dateutil_object)
        if r_dates.exists():
            for day in r_dates:
                dt = datetime.combine(day.naive_dt, self.TIME)
                dt = recurrence_tz.localize(dt)
                if day.exclude:
                    rule_set.exdate(dt)
                else:
                    rule_set.rdate(dt)
        return rule_set


class Rule(models.Model):
    """
    generate dateutils rrule instance

    rrule
    The rrule module offers a small, complete, and very fast, implementation of the
    recurrence rules documented in the iCalendar RFC, including support for caching
    of results.

    rrule type
    That's the base of the rrule operation. It accepts all the keywords defined in
    the RFC as its constructor parameters (except byday, which was renamed to byweekday)
    and more. The constructor prototype is:

    rrule(freq)
    Where freq must be one of YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, or SECONDLY.

    Additionally, it supports the following and others keyword arguments:

    dtstart
    The recurrence start. Besides being the base for the recurrence, missing parameters
     in the final recurrence instances will also be extracted from this date. If not
    given, datetime.now() will be used instead.

    interval
    The interval between each freq iteration. For example, when using YEARLY, an interval
    of 2 means once every two years, but with HOURLY, it means once every two hours.
    The default interval is 1.

    wkst
    The week start day. Must be one of the MO, TU, WE constants, or an integer, specifying
    the first day of the week. This will affect recurrences based on weekly periods.
    The default week start is got from calendar.firstweekday(),and may be modified by
    calendar.setfirstweekday().

    count
    How many occurrences will be generated.

    until
    If given, this must be a datetime instance, that will specify the limit of the
    recurrence. If a recurrence instance happens to be the same as the datetime instance
     given in the until keyword, this will be the last occurrence.

    bysetpos
    If given, it must be either an integer, or a sequence of integers, positive or
    negative. Each given integer will specify an occurrence number, corresponding to
    the nth occurrence of the rule inside the frequency period. For example, a bysetpos
    of -1 if combined with a MONTHLY frequency, and a byweekday of (MO, TU, WE, TH, FR),
    will result in the last work day of every month.

    bymonth
    If given, it must be either an integer, or a sequence of integers, meaning the
    months to apply the recurrence to.

    bymonthday
    If given, it must be either an integer, or a sequence of integers, meaning the
    month days to apply the recurrence to.

    byweekday
    If given, it must be either an integer (0 == MO), a sequence of integers, one of
    the weekday constants (MO, TU, etc), or a sequence of these constants. When given,
    these variables will define the weekdays where the recurrence will be applied.
    It's also possible to use an argument n for the weekday instances, which will mean
    the nth occurrence of this weekday in the period. For example, with MONTHLY, or
    with YEARLY and BYMONTH, using FR in byweekday will specify the first friday
    of the month where the recurrence happens. Notice that in the RFC documentation,
    this is specified as BYDAY, but was renamed to avoid the ambiguity of that keyword.

    doc from: http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57

    """

    (YEARLY, MONTHLY, WEEKLY, DAILY) = range(4)

    FREQUENCIES = [
        (YEARLY, _('YEARLY')),
        (MONTHLY, _('MONTHLY')),
        (WEEKLY, _('WEEKLY')),
        (DAILY, _('DAILY'))
    ]

    (MONDAY, TUESDAY, WEDNESDAY, THURSDAY,
     FRIDAY, SATURDAY, SUNDAY) = list(range(0, 7))

    WEEKDAYS = [
        (MONDAY, _('Monday')),
        (TUESDAY, _('Tuesday')),
        (WEDNESDAY, _('Wednesday')),
        (THURSDAY, _('Thursday')),
        (FRIDAY, _('Friday')),
        (SATURDAY, _('Saturday')),
        (SUNDAY, _('Sunday'))
    ]

    (JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE, JULY, AUGUST,
     SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER) = list(range(1, 13))

    MONTH_CHOICES = [
        (JANUARY, _('January')),
        (FEBRUARY, _('February')),
        (MARCH, _('March')),
        (APRIL, _('April')),
        (MAY, _('May')),
        (JUNE, _('June')),
        (JULY, _('July')),
        (AUGUST, _('August')),
        (SEPTEMBER, _('September')),
        (OCTOBER, _('October')),
        (NOVEMBER, _('November')),
        (DECEMBER, _('December'))
    ]

    (FIRST_DAY, SECOND_DAY, THIRD_DAY, FOURTH_DAY, FIFTH_DAY,
     SIXTH_DAY, SEVENTH_DAY, EIGHTH_DAY, NINTH_DAY, TENTH_DAY,
     ELEVENTH_DAY, TWELFTH_DAY, THIRTEENTH_DAY, FOURTEENTH_DAY,
     FIFTEENTH_DAY, SIXTEENTH_DAY, SEVENTEENTH_DAY, EIGHTEENTH_DAY,
     NINETEENTH_DAY, TWENTIETH_DAY, TWENTY_FIRST_DAY, TWENTY_SECOND_DAY,
     TWENTY_THIRD_DAY, TWENTY_FOURTH_DAY, TWENTY_FIFTH_DAY, TWENTY_SIXTH_DAY,
     TWENTY_SEVENTH_DAY, TWENTY_EIGHTH_DAY, TWENTY_NINTH_DAY, THIRTIETH_DAY,
     THIRTY_FIRST_DAY) = range(1, 32)

    ORDINAL_MONTHDAY = [
        (FIRST_DAY, _("1st day")),
        (SECOND_DAY, _("2nd day")),
        (THIRD_DAY, _("3rd day")),
        (FOURTH_DAY, _("4th day")),
        (FIFTH_DAY, _("5th day")),
        (SIXTH_DAY, _("6th day")),
        (SEVENTH_DAY, _("7th day")),
        (EIGHTH_DAY, _("8th day")),
        (NINTH_DAY, _("9th day")),
        (TENTH_DAY, _("10th day")),
        (ELEVENTH_DAY, _("11th day")),
        (TWELFTH_DAY, _("12th day")),
        (THIRTEENTH_DAY, _("13th day")),
        (FOURTEENTH_DAY, _("14th day")),
        (FIFTEENTH_DAY, _("15th day")),
        (SIXTEENTH_DAY, _("16th day")),
        (SEVENTEENTH_DAY, _("17th day")),
        (EIGHTEENTH_DAY, _("18th day")),
        (NINETEENTH_DAY, _("19th day")),
        (TWENTIETH_DAY, _("20th day")),
        (TWENTY_FIRST_DAY, _("21st day")),
        (TWENTY_SECOND_DAY, _("22nd day")),
        (TWENTY_THIRD_DAY, _("23rd day")),
        (TWENTY_FOURTH_DAY, _("24th day")),
        (TWENTY_FIFTH_DAY, _("25th day")),
        (TWENTY_SIXTH_DAY, _("26th day")),
        (TWENTY_SEVENTH_DAY, _("27th day")),
        (TWENTY_EIGHTH_DAY, _("28th day")),
        (TWENTY_NINTH_DAY, _("29th day")),
        (THIRTIETH_DAY, _("30th day")),
        (THIRTY_FIRST_DAY, _("31st day")),
    ]
    ORDINAL_MONTHDAY += [
        (-1, _('last day')),
        (-2, _('the penultimate day')),
        (-3, _('antepenultimate day')),
        (-4, _('fourth day before last day'))
    ]
    CONSTANT_WEEKDAYS = [
        (_('nth-weekday'), (
            ('1MO', _('First Monday')),
            ('1TU', _('First Tuesday')),
            ('1WE', _('First Wednesday')),
            ('1TH', _('First Thursday')),
            ('1FR', _('First Friday')),
            ('1SA', _('First Saturday')),
            ('1SU', _('First Sunday')),
            ('2MO', _('Second Monday')),
            ('2TU', _('Second Tuesday')),
            ('2WE', _('Second Wednesday')),
            ('2TH', _('Second Thursday')),
            ('2FR', _('Second Friday')),
            ('2SA', _('Second Saturday')),
            ('2SU', _('Second Sunday')),
            ('3MO', _('Third Monday')),
            ('3TU', _('Third Tuesday')),
            ('3WE', _('Third Wednesday')),
            ('3TH', _('Third Thursday')),
            ('3FR', _('Third Friday')),
            ('3SA', _('Third Saturday')),
            ('3SU', _('Third Sunday')),
            ('4MO', _('Fourth Monday')),
            ('4TU', _('Fourth Tuesday')),
            ('4WE', _('Fourth Wednesday')),
            ('4TH', _('Fourth Thursday')),
            ('4FR', _('Fourth Friday')),
            ('4SA', _('Fourth Saturday')),
            ('4SU', _('Fourth Sunday')),
            ('5MO', _('Fifth Monday')),
            ('5TU', _('Fifth Tuesday')),
            ('5WE', _('Fifth Wednesday')),
            ('5TH', _('Fifth Thursday')),
            ('5FR', _('Fifth Friday')),
            ('5SA', _('Fifth Saturday')),
            ('5SU', _('Fifth Sunday')),
            ('-1MO', _('Last Monday')),
            ('-1TU', _('Last Tuesday')),
            ('-1WE', _('Last Wednesday')),
            ('-1TH', _('Last Thursday')),
            ('-1FR', _('Last Friday')),
            ('-1SA', _('Last Saturday')),
            ('-1SU', _('Last Sunday'))
        )
         ),
        (_('weekdays'), (
            ('MO', _('On Monday')),
            ('TU', _('Tuesdays')),
            ('WE', _('The Wednesday')),
            ('TH', _('Thursdays')),
            ('FR', _('Fridays')),
            ('SA', _('Saturdays')),
            ('SU', _('Sundays')),
        )
         )
    ]

    BY_DATE = 1
    BY_DAY = 2
    YEARLY_MONTH_MODE = [
        (None, _('Select a mode')),
        (BY_DATE, _('by date')),
        (BY_DAY, _('by day'))
    ]

    FOREVER = 'forever'
    UNTIL = 'until'
    COUNT = 'count'

    FREQ_TYPE = [
        (FOREVER, _('Repeat forever')),
        (UNTIL, _('Until')),
        (COUNT, _('Occurrence(s)'))
    ]

    # bysetpos min and max values
    MIN_BYSETPOS = -3
    MAX_BYSETPOS = 4

    BYSETPOS_NTH = [
        (1, _('first occurrence')),
        (2, _('second occurrence')),
        (3, _('third occurrence')),
        (4, _('fourth occurrence')),
        (-1, _('last occurrence')),
        (-2, _('the penultimate occurrence')),
        (-3, _('antepenultimate occurrence')),
    ]

    recurrence = models.ForeignKey(
        Recurrence, related_name="rules", related_query_name="rule",
        on_delete=models.CASCADE
    )
    freq = models.PositiveSmallIntegerField(_("Frequency"), choices=FREQUENCIES)
    year_month_mode = models.PositiveSmallIntegerField(
        'mode',
        choices=YEARLY_MONTH_MODE,
        blank=True, null=True,
        default=None,
        validators=[MinValueValidator(BY_DATE),
                    MaxValueValidator(BY_DAY)
                    ]
    )
    dtstart = models.DateField(default=timezone.now)
    utc_dtstart = models.DateTimeField(editable=False)
    interval = models.PositiveIntegerField(default=None, validators=[MinValueValidator(1)])
    wkst = models.PositiveSmallIntegerField(_("First Weekday"), choices=WEEKDAYS, default=MONDAY)
    bymonth = MultiSelectField(choices=MONTH_CHOICES, blank=True, null=True, default=None)
    bymonthday = MultiSelectField(choices=ORDINAL_MONTHDAY, blank=True, null=True, default=None)
    byweekday = MultiSelectField(choices=CONSTANT_WEEKDAYS, blank=True, null=True, default=None, max_length=300)
    bysetpos = MultiSelectField(blank=True, null=True, default=None, choices=BYSETPOS_NTH,
                                validators=[MinValueValidator(MIN_BYSETPOS), MaxValueValidator(MAX_BYSETPOS)])
    freq_type = models.CharField(choices=FREQ_TYPE, max_length=30, default=FOREVER)
    count = models.PositiveIntegerField(blank=True, null=True, default=None, validators=[MinValueValidator(1)])
    until_date = models.DateField(blank=True, null=True, default=None)
    utc_until = models.DateTimeField(blank=True, null=True, default=None, editable=False)
    # naive_until_time = models.TimeField(blank=True, null=True, default=None)
    exclude = models.BooleanField(default=False)

    def __str__(self):
        return self.rule_to_text(True)

    def clean(self):
        byweekday = self.byweekday
        freq = self.freq
        check_pattern = self._get_byweekday_pattern
        # patter regex with nth value e.g +1MO
        pattern_weekday_with_nth = "^(?:[0-9]{1}|[-+][0-9]{1})?[AEOUMTHWSFR]{2}$"

        if not self.year_month_mode and (freq == self.YEARLY or freq == self.MONTHLY):
            raise ValidationError({'year_month_mode': _('mode field is required')}, code='mode_required')
        elif self.year_month_mode and (freq != self.YEARLY and freq != self.MONTHLY):
            raise ValidationError({'year_month_mode': _('mode field is unnecessary')}, code='mode_required')

        if self.bymonthday and self.byweekday:
            raise ValidationError(_('bymonth and byweekday fields are excluded from each other'),
                                  code='bymonth_or_byweekday_forbidden')

        if self.year_month_mode == self.BY_DATE and self.byweekday:
            raise ValidationError(
                {'byweekday': _(f'mode field must be {self.YEARLY_MONTH_MODE[self.BY_DAY][1]}')},
                code='mode_required')

        elif self.year_month_mode == self.BY_DAY and self.bymonthday:
            raise ValidationError(
                {'bymonthday': _(f'mode field must be {self.YEARLY_MONTH_MODE[self.BY_DATE][1]}')},
                code='mode_required')

        if freq == self.DAILY or freq == self.WEEKLY:
            if self.bymonthday:
                raise ValidationError({
                    'bymonthday': _("Must not be specified when the Freq is set to WEEKLY or DAILY")
                },
                    code="unnecessary_bymonthday"
                )

        if freq == self.WEEKLY and not byweekday:
            ValidationError({'byweekday': _('this field is required ')}, code='required')

        if byweekday:
            if freq == self.DAILY:
                raise ValidationError({
                    'byweekday': _("Can't specify by weekday With Freq DAILY")
                },
                    code="unnecessary_byweekday"
                )
            if not all(check_pattern(i) == check_pattern(byweekday[0]) for i in byweekday):
                raise ValidationError({
                    'byweekday': _("by weekday must be in the form (1MO, +1MO, -1MO) or (MO, WE)"
                                   "you cannot use both formats at the same time")
                },
                    code="different_formats"
                )

            for value in byweekday:
                s = re.search(pattern_weekday_with_nth, value)
                if s is None:
                    raise ValidationError({
                        'byweekday': _("by weekday must be in the format (1MO, +1MO, -1MO, MO)")
                    },
                        code="wrong_value"
                    )

            if freq == self.WEEKLY:
                for value in byweekday:
                    s = re.search("^([AEOUMTHWSFR]{2}$)", value)
                    if s is None:
                        raise ValidationError({
                            'byweekday': _("With Freq Weekly by weekday must be in the form (MO, WE)")
                        },
                            code="invalid_weekday"
                        )

        if self.count and self.until_date:
            raise ValidationError(
                _('count and until fields are excluded from each other'),
                code='count_or_utc_forbidden'
            )

        if self.freq_type == self.FOREVER and (self.until_date or self.count):
            raise ValidationError(
                _('count or until values are unnecessary with forever freq type'),
                code='unnecessary'
            )
        elif self.freq_type == self.UNTIL and not self.until_date:
            raise ValidationError({'until_date': _('this field is required')}, code='until_required')
        elif self.freq_type == self.COUNT and not self.count:
            raise ValidationError({'count': _('this field is required')}, code='count_required')

        if self.bysetpos and (not any([self.byweekday, self.bymonthday]) or self.freq == self.WEEKLY):
            raise ValidationError({
                'bysetpos': _(
                    "Must be specified with the freq. YEARLY or MONTHLY with byweekday or bymonthday parameters")
            },
                code="unnecessary_bysetpos"
            )

    def save(self, *args, **kwargs):
        tzname = pytz.timezone(self.recurrence.timezone)
        self.utc_dtstart = tzname.localize(datetime.combine(self.dtstart, Recurrence.TIME))
        if self.until_date:
            dt = datetime.combine(self.until_date, Recurrence.TIME)
            dt = tzname.localize(dt)
            self.utc_until = dt
        else:
            self.utc_until = None
        super().save(*args, **kwargs)

    @staticmethod
    def _get_byweekday_pattern(value):
        pattern_weekday_with_nth = "^([0-9]{1}|[-+][0-9]{1})[AEOUMTHWSFR]{2}$"
        pattern_weekday_without_nth = "^([AEOUMTHWSFR]{2}$)"
        if re.search(pattern_weekday_with_nth, value) is not None:
            return pattern_weekday_with_nth
        elif re.search(pattern_weekday_without_nth, value) is not None:
            return pattern_weekday_without_nth
        else:
            raise ValidationError({
                'byweekday': _("by weekday must be in the form (1MO, +1MO, -1MO, MO)")
            },
                code="wrong_value"
            )

    @property
    def handle_byweekday(self):
        """
        a fork from dateutil.rrule source code
        """
        if not self.byweekday:
            return False

        weekday_dict = {
            "MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4,
            "SA": 5, "SU": 6
        }

        weekdays_constants = []
        for wday in self.byweekday:
            i = 0
            for i in range(len(wday)):
                if wday[i] not in '+-0123456789':
                    break
            n = wday[:i] or None
            w = wday[i:]
            if n:
                n = int(n)
            weekdays_constants.append(weekday(weekday_dict[w], n))
        return weekdays_constants

    @property
    def to_dateutil_rule(self):
        freq = self.freq
        dt_tz = pytz.timezone(self.recurrence.timezone)
        dtstart = datetime.combine(self.dtstart, Recurrence.TIME)
        dtstart = dt_tz.localize(dtstart)
        count = self.count or None

        if self.freq_type == self.UNTIL:
            until = datetime.combine(self.until_date, Recurrence.TIME)
            until = dt_tz.localize(until)
        else:
            until = None

        bymonth = None if not self.bymonth else [int(day) for day in self.bymonth]
        bysetpos = self.bysetpos or None
        bymonthday = None if not self.bymonthday else [int(day) for day in self.bymonthday]
        byweekday = self.handle_byweekday or None
        rule = rrule(freq, dtstart=dtstart, interval=self.interval, wkst=self.wkst, count=count, until=until,
                     bymonth=bymonth, bymonthday=bymonthday, byweekday=byweekday, bysetpos=bysetpos)
        return rule

    def rule_to_text(self, short=False):
        rule = self
        """
        fork from django recurrences
        Render the given `Rule` as natural text.
        :Parameters:
            `short` : bool
                Use abbreviated labels, i.e. 'Fri' instead of 'Friday'.
        """
        conjunction = 'and'  # use as last separator in join() method

        frequencies = (
            _('annually'), _('monthly'), _('weekly'), _('daily'),
        )
        time_intervals = (
            _('years'), _('months'), _('weeks'), _('days')
        )
        weekdays_display = (
            _('Monday'), _('Tuesday'), _('Wednesday'),
            _('Thursday'), _('Friday'), _('Saturday'), _('Sunday'),
        )

        if short:
            positional_display = {
                1: _('1st %(weekday)s'),
                2: _('2nd %(weekday)s'),
                3: _('3rd %(weekday)s'),
                4: _('4th %(weekday)s'),
                -1: _('last %(weekday)s'),
                -2: _('2nd last %(weekday)s'),
                -3: _('3rd last %(weekday)s'),
            }
            # only this case only are permit from -3 up 4
            bysetpos_nth_instances = {
                1: _('1st'),
                2: _('2nd'),
                3: _('3rd'),
                4: _('4th'),
                -1: _('last'),
                -2: _('2nd last'),
                -3: _('3rd last'),
            }
            last_of_month_display = {
                -1: _('last day'),
                -2: _('2nd last day'),
                -3: _('3rd last day'),
                -4: _('4th last day'),
            }

            months_display = (
                _('Jan'), _('Feb'), _('Mar'), _('Apr'),
                _p('month name', 'May'), _('Jun'), _('Jul'), _('Aug'),
                _('Sep'), _('Oct'), _('Nov'), _('Dec'),
            )

        else:
            positional_display = {
                1: _('first %(weekday)s'),
                2: _('second %(weekday)s'),
                3: _('third %(weekday)s'),
                4: _('fourth %(weekday)s'),
                -1: _('last %(weekday)s'),
                -2: _('second last %(weekday)s'),
                -3: _('third last %(weekday)s'),
            }

            bysetpos_nth_instances = {
                1: _('first'),
                2: _('second'),
                3: _('third'),
                4: _('fourth'),
                -1: _('last'),
                -2: _('second last'),
                -3: _('third last'),
            }

            last_of_month_display = {
                -1: _('last day'),
                -2: _('second last day'),
                -3: _('third last day'),
                -4: _('fourth last day'),
            }
            months_display = (
                _('January'), _('February'), _('March'), _('April'),
                _p('month name', 'May'), _('June'), _('July'), _('August'),
                _('September'), _('October'), _('November'), _('December'),
            )

        parts = []

        if self.interval > 1:
            parts.append(
                _('every %(number)s %(freq)s') % {
                    'number': rule.interval,
                    'freq': time_intervals[self.freq]
                })
        else:
            parts.append(frequencies[self.freq])

        if self.bymonth:
            # bymonth are 1-indexed (January is 1), months_display
            # are 0-indexed (January is 0).
            # change conjunction to 'and' with freq monthly and bysetpos
            # bysetpos with monthly apply nth only to byweekday and bymonthday
            # however with yearly apply to bymonth, byweekday and bymonth day
            if self.bysetpos and self.freq == self.MONTHLY:
                conjunction = 'and'
            elif self.bysetpos and self.freq == self.YEARLY:
                conjunction = 'or'

            months = [months_display[int(month_index) - 1] for month_index in self.bymonth]
            items = join_with_conjunction(months, conjunction)
            parts.append(_('in %(items)s') % {'items': items})

        if self.bysetpos:
            conjunction = 'or'

        if self.bymonthday and not self.bymonth:
            if self.freq == self.YEARLY:
                parts.append('each month')

        if self.freq == self.YEARLY or self.freq == self.MONTHLY:
            if self.bymonthday:
                bymonthday = [int(day) for day in self.bymonthday]
                items = [
                    dateformat.format(datetime(1, 1, day), 'jS') if day > 0
                    else last_of_month_display.get(day, day)
                    for day in bymonthday
                ]
                items = join_with_conjunction(items, conjunction)
                parts.append(_('on the %(items)s') % {'items': items})

            elif self.byweekday:
                items = []
                for byday in rule.handle_byweekday:
                    items.append(
                        positional_display.get(byday.n, '%(weekday)s') % {
                            'weekday': weekdays_display[byday.weekday]
                        })
                items = join_with_conjunction(items, conjunction)
                parts.append(
                    _('on the %(items)s') % {
                        'items': items
                    })

        if self.freq == self.WEEKLY:
            if self.byweekday:
                items = [weekdays_display[day.weekday] for day in self.handle_byweekday]
                items = join_with_conjunction(items, conjunction)
                parts.append(_('each %(items)s') % {'items': items})

        # daily frequencies has no additional formatting,

        if self.bysetpos:
            nth_text = ' instance'
            items = []
            for setpos in self.bysetpos:
                items.append(bysetpos_nth_instances.get(int(setpos)))
            items = join_with_conjunction(items, conjunction) + nth_text

            parts.append(_('only the %(items)s') % {'items': items})

        if self.count:
            if self.count == 1:
                parts.append(_('for once'))
            else:
                parts.append(_('for %(number)s occurrences') % {
                    'number': self.count
                })
        elif self.until_date:
            parts.append(_('until the %(date)s') % {
                'date': dateformat.format(self.until_date, 'D d F Y')
            })
        else:
            parts.append(_('forever'))
        return _(', ').join(str(part) for part in parts)


class RDate(models.Model):
    recurrence = models.ForeignKey(Recurrence, related_name='r_dates', related_query_name='r_date',
                                   on_delete=models.CASCADE)
    naive_dt = models.DateField(verbose_name=_('Date'), blank=True)
    # naive_dt_time = models.TimeField(blank=True)
    utc_dt = models.DateTimeField(editable=False)
    exclude = models.BooleanField(default=False)

    def __str__(self):
        dt = datetime.combine(self.naive_dt, Recurrence.TIME)
        dt_tz = pytz.timezone(self.recurrence.timezone)
        dt = dt_tz.localize(dt)
        return f"date: {dateformat.format(dt, 'D d F Y')} " \
               f"{'excluded from rule' if self.exclude else 'included in rule'}"

    def save(self, *args, **kwargs):
        if self.naive_dt:
            self.utc_dt = datetime.combine(self.naive_dt, Recurrence.TIME)
        super().save(*args, **kwargs)
