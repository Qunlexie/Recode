"""
Sample question to show proper formatting
"""

SAMPLE_QUESTION = {
    "title": "Top K Frequent Elements",
    "question": """
**Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.**

**Example 1:**

**Input:** `nums = [1,1,1,2,2,3], k = 2`

**Output:** `[1,2]`

**Explanation:**
- 1 appears 3 times
- 2 appears 2 times  
- 3 appears 1 time
- So the 2 most frequent are [1,2]
    """,
    "answer": """
**Solution: Use Counter and Bucket Sort**

```python
def topKFrequent(nums, k):
    from collections import Counter
    
    # Count frequency of each number
    count = Counter(nums)
    
    # Create buckets: index = frequency, value = list of numbers
    max_freq = max(count.values())
    bucket = [[] for _ in range(max_freq + 1)]
    
    # Put numbers in buckets by their frequency
    for num, freq in count.items():
        bucket[freq].append(num)
    
    # Collect results from highest frequency bucket
    result = []
    for i in range(len(bucket) - 1, -1, -1):
        for num in bucket[i]:
            result.append(num)
            if len(result) == k:
                return result
    
    return result
```

**Key Insight:**
- Count frequency of each number
- Use bucket sort: index = frequency, value = numbers with that frequency
- Traverse buckets from highest to lowest frequency

**Time Complexity:** O(n) where n = length of nums
**Space Complexity:** O(n) for the counter and buckets
    """
}
