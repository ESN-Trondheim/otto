import arrow


def format_date_range(from_iso: str, to_iso: str) -> str:
    date_format = "Do of MMMM"
    collapsed_date_format = "Do"

    if from_iso is None and to_iso is None:
        return ""

    if from_iso is None:
        return arrow.get(to_iso).format(date_format)

    if to_iso is None:
        return arrow.get(from_iso).format(date_format)

    from_date = arrow.get(from_iso)
    to_date = arrow.get(to_iso)

    if from_date == to_date:
        return from_date.format(date_format)

    if from_date.month == to_date.month:
        return (
            f"{from_date.format(collapsed_date_format)} - {to_date.format(date_format)}"
        )
    else:
        return f"{from_date.format(date_format)} - {to_date.format(date_format)}"
