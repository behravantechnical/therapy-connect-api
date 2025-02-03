from django.db.models import Q


def get_day_of_week_number(day_name):
    """Convert 'Monday' to Django's `week_day` format (Sunday=1, Monday=2, ..., Saturday=7)"""
    days = {
        "Sunday": 1,
        "Monday": 2,
        "Tuesday": 3,
        "Wednesday": 4,
        "Thursday": 5,
        "Friday": 6,
        "Saturday": 7,
    }
    return days.get(day_name)


def filter_availability(queryset, params):
    """
    Applies filters to the availability queryset based on provided query parameters.
    Supports:
    - therapist_id
    - day_of_week
    - start_time_after / start_time_before
    - end_time_after / end_time_before
    """

    therapist_id = params.get("therapist_id")
    day_of_week = params.get("day_of_week")
    start_time_after = params.get("start_time_after")
    start_time_before = params.get("start_time_before")
    end_time_after = params.get("end_time_after")
    end_time_before = params.get("end_time_before")

    # Filter by therapist ID
    if therapist_id:
        queryset = queryset.filter(therapist_id=therapist_id)

    # Filter by day of the week
    if day_of_week:
        day_number = get_day_of_week_number(day_of_week)
        if day_number:
            queryset = queryset.filter(date__week_day=day_number)

    # Filter by time ranges
    time_filters = Q()
    if start_time_after:
        time_filters &= Q(start_time__gte=start_time_after)
    if start_time_before:
        time_filters &= Q(start_time__lte=start_time_before)
    if end_time_after:
        time_filters &= Q(end_time__gte=end_time_after)
    if end_time_before:
        time_filters &= Q(end_time__lte=end_time_before)

    queryset = queryset.filter(time_filters)

    return queryset
