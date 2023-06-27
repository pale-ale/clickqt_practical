def is_nested_list(lst):
        if isinstance(lst, list):
            for item in lst:
                if isinstance(item, list):
                    return True
            return False
        else:
            return False