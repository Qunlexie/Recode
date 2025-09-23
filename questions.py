"""
Simple questions and answers for coding interview practice.
Easy to add new questions here!
"""

QUESTIONS = [
    {
        "title": "Group Anagrams",
        "question": """
**Given an array of strings strs, group the anagrams together. You can return the answer in any order.**

**Example 1:**

**Input:** `strs = ["eat","tea","tan","ate","nat","bat"]`

**Output:** `[["bat"],["nat","tan"],["ate","eat","tea"]]`

**Explanation:**

- There is no string in strs that can be rearranged to form "bat".
- The strings "nat" and "tan" are anagrams as they can be rearranged to form each other.
- The strings "ate", "eat", and "tea" are anagrams as they can be rearranged to form each other.
        """,
        "answer": """
**Solution: Use Hash Map with Sorted Characters**

```python
def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        # dict_ = coll{[]: [str1, str2, str3]}
        dict_ = defaultdict(list)
        for s in strs:
            count = [0]*26
            for ch in s:
                count[ord(ch)-ord("a")] += 1
            dict_[tuple(count)].append(s)
        return dict_.values()
```

**Key Insight:**
- Anagrams have the same characters when sorted
- Use sorted string as hash map key
- Group all strings with same sorted key

**Time Complexity:** O(N * M log M) where N = number of strings, M = average length
**Space Complexity:** O(N * M) for the hash map
        """
    },
    
    # Add more questions here! Just copy the format above.
    # {
    #     "title": "Your Question Title",
    #     "question": "Your question text here...",
    #     "answer": "Your answer text here..."
    # },
]
