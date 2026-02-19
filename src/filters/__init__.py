def register_filters(templates):
    from .datetime_filters import human_date

    templates.env.filters["human_date"] = human_date
    # app.template_filter('time_ago')(time_ago)
