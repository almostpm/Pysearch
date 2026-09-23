def binary_search(sorted_list, target):
    """
    Returns the index of target in sorted_list if found, or None if not found.
    Assumes sorted_list is already sorted ascending.
    """
    # Initialize the lower bound pointer to the array start
    low = 0
    # Set the higher bound pointer to the final index
    high = len(sorted_list) - 1
    # Continue searching until the boundary pointers cross each other
    while low <= high:
        # Calculate the middle index using floor integer division
        mid = (low + high) // 2
        # Retrieve the value stored at the middle index position
        guess = sorted_list[mid]
        # Check if the middle value matches the target item
        if guess == target:
            # Return the correct matching index position immediately
            return mid
        # Check if the middle value is too low
        elif guess < target:
            # Shift the lower bound pointer past the mid index
            low = mid + 1
        # Execute if the middle value is too high
        else:
            # Shift the higher bound pointer below the mid index
            high = mid - 1
    # Return None if the target value is not found
    return None