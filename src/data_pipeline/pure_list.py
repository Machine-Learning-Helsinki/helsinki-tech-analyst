# checker_util.py

from typing import Union, List, Dict, Any

def process_list_or_dict(data: Any) -> Union[Dict, List, Any]:
    """
    Checks the type of the input data and processes it accordingly:

    1. If the input `data` is already a dictionary, it returns the dictionary as is.
    2. If the input `data` is a list:
        a. If the list contains exactly one element AND that element is a dictionary,
           it extracts and returns that single dictionary.
        b. In all other list scenarios (e.g., empty list, list with multiple dictionaries,
           list containing non-dictionary elements, or a mix), it returns the list as is.
    3. For any other data type (e.g., string, int, None), it returns the input as is.

    This function is useful for standardizing data structures where a list
    containing a single dictionary should be treated as just that dictionary.

    Args:
        data: The input data, which could be a dictionary, a list, or any other type.

    Returns:
        A dictionary, a list, or the original data type, depending on the input
        and the rules described above.
    """
    if isinstance(data, dict):
        return data
    elif isinstance(data, list):
        if len(data) == 1 and isinstance(data[0], dict):
            return data[0]
        else:
            return data
    else:
        return data
    
# checker_util.py

from typing import Union, List, Dict, Any

def ensure_dict_output(data: Any) -> Dict:
    
    if isinstance(data, dict):
        # Case 1: Input is already a dictionary
        return data
    elif isinstance(data, list):
        # Case 2: Input is a list
        if len(data) == 1 and isinstance(data[0], dict):
            # Case 2a: List contains exactly one dictionary
            return data[0]
        elif not data:
            # Case 2b: Empty list
            return {}
        else:
            # Case 2c: List with multiple items (dicts or non-dicts), convert to indexed dict
            return {str(i): item for i, item in enumerate(data)}
    else:
        # Case 3: Any other data type (string, int, None, etc.)
        return {"value": data}