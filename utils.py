def formatted_list_date(string_date: str):
    if len(string_date) != 8:
        return False
    else:
        d_date = [int(string_date[0:4]), int(string_date[4:6]), int(string_date[6:8])]
        if 1900 < d_date[0] < 2200 and 1 <= d_date[1] <= 12 and 1 <= d_date[2] <= 31:
            return d_date
        return False
