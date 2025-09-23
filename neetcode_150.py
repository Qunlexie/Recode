"""
NeetCode 150 Problems Database
All 150 problems from NeetCode's curated list
"""

NEETCODE_150 = [
    {
        "title": "Two Sum",
        "question": """
**Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.**

**Example 1:**
**Input:** `nums = [2,7,11,15], target = 9`
**Output:** `[0,1]`

**Example 2:**
**Input:** `nums = [3,2,4], target = 6`
**Output:** `[1,2]`
        """,
        "answer": """
**Solution: Hash Map**

```python
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

**Time Complexity:** O(n)
**Space Complexity:** O(n)
        """
    },
    
    {
        "title": "Best Time to Buy and Sell Stock",
        "question": """
**You are given an array prices where prices[i] is the price of a given stock on the ith day.**

**You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.**

**Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.**

**Example 1:**
**Input:** `prices = [7,1,5,3,6,4]`
**Output:** `5`
        """,
        "answer": """
**Solution: Keep Track of Minimum Price**

```python
def maxProfit(prices):
    min_price = float('inf')
    max_profit = 0
    
    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    
    return max_profit
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Contains Duplicate",
        "question": """
**Given an integer array nums, return true if any value appears at least twice in the array, and return false if every element is distinct.**

**Example 1:**
**Input:** `nums = [1,2,3,1]`
**Output:** `true`

**Example 2:**
**Input:** `nums = [1,2,3,4]`
**Output:** `false`
        """,
        "answer": """
**Solution: Set**

```python
def containsDuplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
```

**Time Complexity:** O(n)
**Space Complexity:** O(n)
        """
    },
    
    {
        "title": "Product of Array Except Self",
        "question": """
**Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i].**

**You must write an algorithm that runs in O(n) time and without using the division operator.**

**Example 1:**
**Input:** `nums = [1,2,3,4]`
**Output:** `[24,12,8,6]`
        """,
        "answer": """
**Solution: Two Passes**

```python
def productExceptSelf(nums):
    n = len(nums)
    result = [1] * n
    
    # First pass: left products
    for i in range(1, n):
        result[i] = result[i-1] * nums[i-1]
    
    # Second pass: right products
    right = 1
    for i in range(n-1, -1, -1):
        result[i] *= right
        right *= nums[i]
    
    return result
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Maximum Subarray",
        "question": """
**Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.**

**Example 1:**
**Input:** `nums = [-2,1,-3,4,-1,2,1,-5,4]`
**Output:** `6`
**Explanation:** `[4,-1,2,1]` has the largest sum = 6.
        """,
        "answer": """
**Solution: Kadane's Algorithm**

```python
def maxSubArray(nums):
    max_sum = current_sum = nums[0]
    
    for i in range(1, len(nums)):
        current_sum = max(nums[i], current_sum + nums[i])
        max_sum = max(max_sum, current_sum)
    
    return max_sum
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Maximum Product Subarray",
        "question": """
**Given an integer array nums, find a contiguous non-empty subarray within the array that has the largest product, and return the product.**

**Example 1:**
**Input:** `nums = [2,3,-2,4]`
**Output:** `6`
**Explanation:** `[2,3]` has the largest product = 6.
        """,
        "answer": """
**Solution: Keep Track of Min and Max**

```python
def maxProduct(nums):
    if not nums:
        return 0
    
    max_prod = min_prod = result = nums[0]
    
    for i in range(1, len(nums)):
        if nums[i] < 0:
            max_prod, min_prod = min_prod, max_prod
        
        max_prod = max(nums[i], max_prod * nums[i])
        min_prod = min(nums[i], min_prod * nums[i])
        result = max(result, max_prod)
    
    return result
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Find Minimum in Rotated Sorted Array",
        "question": """
**Suppose an array of length n sorted in ascending order is rotated between 1 and n times.**

**Given the sorted rotated array nums of unique elements, return the minimum element of this array.**

**Example 1:**
**Input:** `nums = [3,4,5,1,2]`
**Output:** `1`
        """,
        "answer": """
**Solution: Binary Search**

```python
def findMin(nums):
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    
    return nums[left]
```

**Time Complexity:** O(log n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Search in Rotated Sorted Array",
        "question": """
**There is an integer array nums sorted in ascending order (with distinct values).**

**Prior to being passed to your function, nums is possibly rotated at an unknown pivot index k.**

**Given the array nums after the possible rotation and an integer target, return the index of target if it is in nums, or -1 if it is not in nums.**

**Example 1:**
**Input:** `nums = [4,5,6,7,0,1,2], target = 0`
**Output:** `4`
        """,
        "answer": """
**Solution: Binary Search with Rotation Check**

```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        
        # Check which half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1
```

**Time Complexity:** O(log n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "3Sum",
        "question": """
**Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.**

**Notice that the solution set must not contain duplicate triplets.**

**Example 1:**
**Input:** `nums = [-1,0,1,2,-1,-4]`
**Output:** `[[-1,-1,2],[-1,0,1]]`
        """,
        "answer": """
**Solution: Sort + Two Pointers**

```python
def threeSum(nums):
    nums.sort()
    result = []
    
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        
        left, right = i + 1, len(nums) - 1
        
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    
    return result
```

**Time Complexity:** O(n²)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Container With Most Water",
        "question": """
**You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).**

**Find two lines that together with the x-axis form a container, such that the container contains the most water.**

**Example 1:**
**Input:** `height = [1,8,6,2,5,4,8,3,7]`
**Output:** `49`
        """,
        "answer": """
**Solution: Two Pointers**

```python
def maxArea(height):
    left, right = 0, len(height) - 1
    max_area = 0
    
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        max_area = max(max_area, area)
        
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_area
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Valid Parentheses",
        "question": """
**Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.**

**A string is valid if:**
1. Open brackets must be closed by the same type of brackets
2. Open brackets must be closed in the correct order
3. Every close bracket has a corresponding open bracket of the same type

**Example 1:**
**Input:** `s = "()"`
**Output:** `true`

**Example 2:**
**Input:** `s = "()[]{}"`
**Output:** `true`

**Example 3:**
**Input:** `s = "(]"`
**Output:** `false`
        """,
        "answer": """
**Solution: Stack**

```python
def isValid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            stack.append(char)
    
    return len(stack) == 0
```

**Key Insight:**
- Use stack to track opening brackets
- When we see closing bracket, check if it matches the most recent opening bracket
- Valid string must have empty stack at the end

**Time Complexity:** O(n)
**Space Complexity:** O(n)
        """
    },
    
    {
        "title": "Longest Common Prefix",
        "question": """
**Write a function to find the longest common prefix string amongst an array of strings.**

**If there is no common prefix, return an empty string "".**

**Example 1:**
**Input:** `strs = ["flower","flow","flight"]`
**Output:** `"fl"`

**Example 2:**
**Input:** `strs = ["dog","racecar","car"]`
**Output:** `""`
        """,
        "answer": """
**Solution: Vertical Scanning**

```python
def longestCommonPrefix(strs):
    if not strs:
        return ""
    
    for i in range(len(strs[0])):
        char = strs[0][i]
        for j in range(1, len(strs)):
            if i >= len(strs[j]) or strs[j][i] != char:
                return strs[0][:i]
    
    return strs[0]
```

**Key Insight:**
- Compare characters vertically (same position across all strings)
- Return prefix up to first mismatch
- Worst case: all strings are identical

**Time Complexity:** O(S) where S is sum of all characters
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Merge Two Sorted Lists",
        "question": """
**You are given the heads of two sorted linked lists list1 and list2.**

**Merge the two lists in a one sorted list. The list should be made by splicing together the nodes of the first two lists.**

**Return the head of the merged linked list.**

**Example 1:**
**Input:** `list1 = [1,2,4], list2 = [1,3,4]`
**Output:** `[1,1,2,3,4,4]`
        """,
        "answer": """
**Solution: Two Pointers**

```python
def mergeTwoLists(list1, list2):
    dummy = ListNode(0)
    current = dummy
    
    while list1 and list2:
        if list1.val <= list2.val:
            current.next = list1
            list1 = list1.next
        else:
            current.next = list2
            list2 = list2.next
        current = current.next
    
    # Attach remaining nodes
    current.next = list1 if list1 else list2
    
    return dummy.next
```

**Key Insight:**
- Use dummy node to simplify edge cases
- Compare values and link smaller node
- Attach remaining nodes from non-empty list

**Time Complexity:** O(n + m)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Remove Duplicates from Sorted Array",
        "question": """
**Given an integer array nums sorted in non-decreasing order, remove the duplicates in-place such that each unique element appears only once.**

**The relative order of the elements should be kept the same.**

**Return k after placing the final result in the first k slots of nums.**

**Example 1:**
**Input:** `nums = [1,1,2]`
**Output:** `2, nums = [1,2,_]`
        """,
        "answer": """
**Solution: Two Pointers**

```python
def removeDuplicates(nums):
    if not nums:
        return 0
    
    write_index = 1
    
    for read_index in range(1, len(nums)):
        if nums[read_index] != nums[read_index - 1]:
            nums[write_index] = nums[read_index]
            write_index += 1
    
    return write_index
```

**Key Insight:**
- Use two pointers: read and write
- Only write when we find a new unique value
- Write index tracks position for next unique element

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Remove Element",
        "question": """
**Given an integer array nums and an integer val, remove all occurrences of val in-place.**

**The order of the elements may be changed. Then return the number of elements in nums which are not equal to val.**

**Example 1:**
**Input:** `nums = [3,2,2,3], val = 3`
**Output:** `2, nums = [2,2,_,_]`
        """,
        "answer": """
**Solution: Two Pointers**

```python
def removeElement(nums, val):
    write_index = 0
    
    for read_index in range(len(nums)):
        if nums[read_index] != val:
            nums[write_index] = nums[read_index]
            write_index += 1
    
    return write_index
```

**Key Insight:**
- Similar to remove duplicates
- Write only non-target values
- Write index tracks next position for valid element

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Search Insert Position",
        "question": """
**Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.**

**Example 1:**
**Input:** `nums = [1,3,5,6], target = 5`
**Output:** `2`

**Example 2:**
**Input:** `nums = [1,3,5,6], target = 2`
**Output:** `1`
        """,
        "answer": """
**Solution: Binary Search**

```python
def searchInsert(nums, target):
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return left
```

**Key Insight:**
- Standard binary search
- If not found, left pointer gives insertion position
- Left will be at first position where nums[left] >= target

**Time Complexity:** O(log n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Length of Last Word",
        "question": """
**Given a string s consisting of words and spaces, return the length of the last word in the string.**

**A word is a maximal substring consisting of non-space characters only.**

**Example 1:**
**Input:** `s = "Hello World"`
**Output:** `5`

**Example 2:**
**Input:** `s = "   fly me   to   the moon  "`
**Output:** `4`
        """,
        "answer": """
**Solution: Traverse from End**

```python
def lengthOfLastWord(s):
    length = 0
    i = len(s) - 1
    
    # Skip trailing spaces
    while i >= 0 and s[i] == ' ':
        i -= 1
    
    # Count characters in last word
    while i >= 0 and s[i] != ' ':
        length += 1
        i -= 1
    
    return length
```

**Key Insight:**
- Start from end and skip trailing spaces
- Count characters until we hit a space or beginning
- More efficient than splitting string

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Plus One",
        "question": """
**You are given a large integer represented as an integer array digits, where each digits[i] is the ith digit of the integer.**

**Increment the large integer by one and return the resulting array of digits.**

**Example 1:**
**Input:** `digits = [1,2,3]`
**Output:** `[1,2,4]`

**Example 2:**
**Input:** `digits = [9]`
**Output:** `[1,0]`
        """,
        "answer": """
**Solution: Handle Carry**

```python
def plusOne(digits):
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    
    # If we get here, all digits were 9
    return [1] + digits
```

**Key Insight:**
- Start from rightmost digit
- If digit < 9, increment and return
- If digit == 9, set to 0 and continue
- If all digits were 9, prepend 1

**Time Complexity:** O(n)
**Space Complexity:** O(1)
        """
    },
    
    {
        "title": "Add Binary",
        "question": """
**Given two binary strings a and b, return their sum as a binary string.**

**Example 1:**
**Input:** `a = "11", b = "1"`
**Output:** `"100"`

**Example 2:**
**Input:** `a = "1010", b = "1011"`
**Output:** `"10101"`
        """,
        "answer": """
**Solution: Simulate Addition**

```python
def addBinary(a, b):
    result = []
    carry = 0
    i, j = len(a) - 1, len(b) - 1
    
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i])
            i -= 1
        if j >= 0:
            total += int(b[j])
            j -= 1
        
        result.append(str(total % 2))
        carry = total // 2
    
    return ''.join(reversed(result))
```

**Key Insight:**
- Process digits from right to left
- Handle carry for binary addition
- Result digits are (sum + carry) % 2
- New carry is (sum + carry) // 2

**Time Complexity:** O(max(len(a), len(b)))
**Space Complexity:** O(max(len(a), len(b)))
        """
    }
]
