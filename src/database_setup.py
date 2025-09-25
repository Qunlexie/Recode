#!/usr/bin/env python3
"""
Enhanced database setup script using high-quality NeetCode-Solutions-1 repository.
This version imports clean, well-structured Python solutions with detailed explanations,
complexity analysis, and proper formatting.
"""

import sqlite3
import os
import re
import json
from pathlib import Path
from textwrap import dedent
import ast

def create_enhanced_database():
    """Create the enhanced SQLite database with comprehensive schema."""
    conn = sqlite3.connect('recode.db')
    cur = conn.cursor()
    
    # Drop existing tables to start fresh
    cur.execute('DROP TABLE IF EXISTS problems')
    cur.execute('DROP TABLE IF EXISTS user_stats')
    
    # Create enhanced problems table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            leetcode_id INTEGER,
            title TEXT NOT NULL,
            difficulty TEXT,
            category TEXT,
            description TEXT,
            key_idea TEXT,
            solution_code TEXT,
            solution_language TEXT DEFAULT 'python',
            time_complexity TEXT,
            space_complexity TEXT,
            explanation TEXT,
            leetcode_link TEXT,
            file_path TEXT,
            tags TEXT,  -- JSON array of tags
            times_reviewed INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            last_reviewed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_stats table for tracking progress
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER,
            session_id TEXT,
            success BOOLEAN,
            review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems (id)
        )
    ''')
    
    conn.commit()
    return conn

def parse_python_solution_file(file_path):
    """Parse a high-quality Python solution file and extract all components."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the docstring to extract problem information
        problem_info = extract_problem_info_from_docstring(content)
        
        # Extract the clean solution code
        solution_code = extract_solution_code(content)
        
        # Extract leetcode ID from filename
        filename = os.path.basename(file_path)
        leetcode_id_match = re.match(r'(\d+)-', filename)
        leetcode_id = int(leetcode_id_match.group(1)) if leetcode_id_match else None
        
        return {
            'leetcode_id': leetcode_id,
            'key_idea': problem_info.get('key_idea', ''),
            'time_complexity': problem_info.get('time_complexity', ''),
            'space_complexity': problem_info.get('space_complexity', ''),
            'solution_code': solution_code,
            'raw_content': content
        }
        
    except Exception as e:
        print(f"Error parsing {file_path}: {str(e)}")
        return None

def extract_problem_info_from_docstring(content):
    """Extract structured information from the docstring."""
    info = {}
    
    try:
        # Parse the AST to get the module docstring
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        
        if docstring:
            # Extract key idea
            key_idea_match = re.search(r'Key Idea:(.*?)(?=Time Complexity:|Space Complexity:|$)', docstring, re.DOTALL | re.IGNORECASE)
            if key_idea_match:
                info['key_idea'] = key_idea_match.group(1).strip()
            
            # Extract time complexity
            time_complexity_match = re.search(r'Time Complexity:(.*?)(?=Space Complexity:|$)', docstring, re.DOTALL | re.IGNORECASE)
            if time_complexity_match:
                info['time_complexity'] = time_complexity_match.group(1).strip()
            
            # Extract space complexity
            space_complexity_match = re.search(r'Space Complexity:(.*?)(?=Time Complexity:|$)', docstring, re.DOTALL | re.IGNORECASE)
            if space_complexity_match:
                info['space_complexity'] = space_complexity_match.group(1).strip()
                
    except Exception as e:
        print(f"Error extracting docstring info: {e}")
        
    return info

def extract_solution_code(content):
    """Extract and auto-format clean solution code from the file."""
    try:
        # Parse AST and find the Solution class
        tree = ast.parse(content)
        raw_code = content.strip()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'Solution':
                # Get the source code for the Solution class
                lines = content.split('\n')
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
                
                solution_lines = lines[start_line:end_line]
                raw_code = '\n'.join(solution_lines)
                break
        else:
            # If no Solution class found, return the content after docstring
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            if docstring:
                # Find where docstring ends and return the rest
                docstring_end = content.find('"""', content.find('"""') + 3) + 3
                raw_code = content[docstring_end:].strip()
        
        # Auto-format the extracted code
        try:
            # Import here to avoid circular imports
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from code_validator import CodeValidator, ValidationLevel
            
            validator = CodeValidator(ValidationLevel.COMPREHENSIVE)
            result = validator.validate_and_fix_code(raw_code, debug=False)
            return result.fixed_code
        except Exception as format_error:
            print(f"Warning: Could not format code, using original: {format_error}")
            return raw_code
        
    except Exception as e:
        print(f"Error extracting solution code: {e}")
        return content

def get_category_mapping():
    """Map directory names to clean category names."""
    return {
        '01_Arrays_&_Hashing': 'Arrays & Hashing',
        '02_Two_Pointers': 'Two Pointers',
        '03_Sliding_Window': 'Sliding Window',
        '04_Stack': 'Stack',
        '05_Binary_Search': 'Binary Search',
        '06_Linked_List': 'Linked List',
        '07_Trees': 'Trees',
        '08_Tries': 'Tries',
        '09_Heap_Priority_Queues': 'Heap/Priority Queue',
        '10_Backtracking': 'Backtracking',
        '11_Graphs': 'Graphs',
        '12_Advanced_Graphs': 'Advanced Graphs',
        '13_1-D_Dynamic_Programming': '1-D Dynamic Programming',
        '14_2-D_Dynamic_Programming': '2-D Dynamic Programming',
        '15_Greedy': 'Greedy',
        '16_Intervals': 'Intervals',
        '17_Math_&_Geometry': 'Math & Geometry',
        '18_Bit_Manipulation': 'Bit Manipulation'
    }

def get_difficulty_from_leetcode_id(leetcode_id):
    """Map leetcode IDs to difficulty levels (simplified mapping)."""
    # This is a simplified mapping - in practice, you might want to
    # fetch this from LeetCode API or maintain a comprehensive mapping
    easy_problems = [1, 26, 53, 70, 121, 125, 136, 141, 155, 169, 189, 190, 191, 217, 226, 242, 268, 283, 292, 338, 344, 349, 383, 387, 389, 412, 434, 448, 461, 463, 476, 496, 500, 504, 506, 509, 520, 543, 557, 559, 561, 575, 589, 590, 594, 598, 637, 643, 645, 653, 657, 661, 674, 680, 682, 686, 687, 693, 696, 697, 704, 717, 724, 733, 744, 746, 747, 748, 754, 758, 766, 771, 783, 784, 788, 796, 804, 806, 811, 812, 819, 821, 824, 830, 832, 836, 844, 849, 852, 859, 860, 867, 868, 872, 883, 884, 888, 892, 896, 905, 908, 917, 922, 929, 933, 937, 941, 942, 944, 949, 953, 961, 965, 970, 976, 977, 985, 989, 993, 997, 1002, 1005, 1009, 1013, 1018, 1021, 1025, 1030, 1037, 1041, 1046, 1047, 1051, 1056, 1064, 1065, 1071, 1078, 1089, 1108, 1122, 1128, 1134, 1137, 1154, 1160, 1165, 1170, 1175, 1184, 1189, 1192, 1200, 1207, 1213, 1217, 1221, 1226, 1232, 1237, 1252, 1260, 1266, 1271, 1275, 1281, 1287, 1290, 1295, 1299, 1304, 1309, 1313, 1317, 1323, 1331, 1337, 1342, 1346, 1351, 1356, 1360, 1365, 1370, 1374, 1380, 1385, 1389, 1394, 1399, 1403, 1408, 1413, 1417, 1422, 1427, 1431, 1436, 1441, 1446, 1450, 1455, 1460, 1464, 1469, 1474, 1478, 1480, 1486, 1491, 1496, 1502, 1507, 1512, 1518, 1523, 1528, 1534, 1539, 1544, 1550, 1556, 1560, 1566, 1570, 1576, 1582, 1588, 1592, 1598, 1603, 1608, 1614, 1619, 1624, 1629, 1636, 1640, 1646, 1652, 1656, 1662, 1668, 1672, 1678, 1684, 1688, 1694, 1700, 1704, 1710, 1716, 1720, 1725, 1732, 1736, 1742, 1748, 1752, 1758, 1763, 1768, 1773, 1779, 1784, 1790, 1796, 1800, 1805, 1812, 1816, 1822, 1827, 1832, 1837, 1844, 1848, 1854, 1859, 1863, 1869, 1876, 1880, 1886, 1893, 1897, 1903, 1909, 1913, 1920, 1925, 1929, 1935, 1941, 1945, 1952, 1957, 1961, 1967, 1971, 1977, 1984, 1988, 1995, 2000, 2006, 2011, 2016, 2022, 2027, 2032, 2037, 2042, 2047, 2053, 2057, 2062, 2068, 2073, 2078, 2083, 2089, 2094, 2099, 2103, 2108, 2114, 2119, 2124, 2129, 2133, 2138, 2144, 2148, 2154, 2160, 2164, 2169, 2176, 2180, 2185, 2190, 2194, 2200, 2206, 2210, 2215, 2220, 2224, 2231, 2235, 2239, 2243, 2248, 2255, 2259, 2264, 2269, 2273, 2278, 2283, 2287, 2293, 2299, 2303, 2309, 2315, 2319, 2325, 2331, 2335, 2341, 2347, 2351, 2357, 2363, 2367, 2373, 2379, 2383, 2389, 2395, 2399, 2404, 2409, 2413, 2418, 2423, 2427, 2432, 2437, 2441, 2446, 2451, 2455, 2460, 2465, 2469, 2474, 2479, 2483, 2488, 2493, 2497, 2500, 2506, 2511, 2515, 2520, 2525, 2529, 2535, 2540, 2544, 2549, 2554, 2558, 2563, 2568, 2572, 2577, 2582, 2586, 2591, 2596, 2600, 2605, 2610, 2614, 2619, 2624, 2628, 2633, 2638, 2642, 2647, 2652, 2656, 2661, 2666, 2670, 2675, 2680, 2684, 2689, 2694, 2698, 2703, 2708, 2712, 2717, 2722, 2726, 2731, 2736, 2740, 2745, 2750, 2754, 2759, 2764, 2768, 2773, 2778, 2782, 2787, 2792, 2796, 2801, 2806, 2810, 2815, 2824, 2828, 2833, 2839, 2843, 2848, 2855, 2859, 2864, 2869, 2873, 2878, 2885, 2889, 2894, 2899, 2903, 2908, 2913, 2917, 2923, 2928, 2932, 2937, 2942, 2946, 2951, 2956, 2960, 2965, 2970, 2974, 2980, 2985, 2989, 2994, 3000]
    
    if leetcode_id in easy_problems:
        return 'Easy'
    elif leetcode_id and leetcode_id < 1000:
        return 'Medium'  # Most problems below 1000 are medium
    else:
        return 'Medium'  # Default to medium

def clean_title(title):
    """Clean the title from directory name."""
    # Remove number prefix and replace underscores
    title = re.sub(r'^\d+_', '', title)
    title = title.replace('_', ' ')
    
    # Handle special characters
    title = title.replace('&', 'and')
    title = title.replace('-', ' ')
    
    # Convert to title case but preserve certain words
    words = title.split()
    result = []
    preserve_case = {'II', 'III', 'IV', 'BST', 'LRU', 'API', 'K', 'N'}
    
    for word in words:
        if word.upper() in preserve_case:
            result.append(word.upper())
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)

def import_neetcode_solutions(conn, neetcode_path):
    """Import all NeetCode solutions from the high-quality repository."""
    cur = conn.cursor()
    category_mapping = get_category_mapping()
    problems_imported = 0
    
    neetcode_root = Path(neetcode_path)
    
    if not neetcode_root.exists():
        print(f"Error: NeetCode repository not found at {neetcode_path}")
        return 0
    
    print(f"🔍 Scanning NeetCode repository: {neetcode_path}")
    
    # Walk through each category directory
    for category_dir in sorted(neetcode_root.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith('.'):
            continue
        
        category_name = category_mapping.get(category_dir.name, category_dir.name)
        print(f"📂 Processing category: {category_name}")
        
        # Walk through each problem directory
        for problem_dir in sorted(category_dir.iterdir()):
            if not problem_dir.is_dir():
                continue
            
            # Look for Python solution file
            python_files = list(problem_dir.glob("*.py"))
            if not python_files:
                continue
            
            python_file = python_files[0]  # Take the first Python file
            print(f"  📄 Processing: {python_file.name}")
            
            # Parse the solution file
            solution_data = parse_python_solution_file(python_file)
            if not solution_data:
                continue
            
            # Extract title from directory name
            title = clean_title(problem_dir.name)
            
            # Get difficulty
            difficulty = get_difficulty_from_leetcode_id(solution_data['leetcode_id'])
            
            # Create LeetCode link - strip the leetcode ID prefix from filename
            if solution_data['leetcode_id']:
                # Extract problem slug from filename by removing the leetcode ID prefix
                # e.g., "0100-same-tree" -> "same-tree"
                problem_slug = re.sub(r'^\d{4}-', '', python_file.stem.replace('_', '-'))
                leetcode_link = f"https://leetcode.com/problems/{problem_slug}/"
            else:
                leetcode_link = None
            
            # Create tags
            tags = [category_name, difficulty]
            
            # Create description from key idea
            description = f"LeetCode {solution_data['leetcode_id']} - {title}"
            if solution_data['key_idea']:
                description += f"\n\n**Approach:** {solution_data['key_idea']}"
            
            # Insert into database
            try:
                cur.execute('''
                    INSERT INTO problems (
                        leetcode_id, title, difficulty, category, description, key_idea,
                        solution_code, solution_language, time_complexity, space_complexity,
                        leetcode_link, file_path, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    solution_data['leetcode_id'], title, difficulty, category_name, description,
                    solution_data['key_idea'], solution_data['solution_code'], 'python',
                    solution_data['time_complexity'], solution_data['space_complexity'],
                    leetcode_link, str(python_file), json.dumps(tags)
                ))
                
                problems_imported += 1
                print(f"    ✅ Imported: {title}")
                
            except sqlite3.Error as e:
                print(f"    ❌ Database error for {title}: {e}")
                continue
    
    conn.commit()
    print(f"\n🎉 Successfully imported {problems_imported} problems!")
    return problems_imported

def main():
    """Main function to set up the enhanced database."""
    print("🚀 Setting up enhanced Recode database with high-quality NeetCode solutions...")
    
    # Path to the NeetCode-Solutions-1 repository
    neetcode_path = "/Users/oowola01/Library/Mobile Documents/com~apple~CloudDocs/OneDrive - Tufts/Personal Development/Coding/Code Repo/NeetCode-Solutions-1"
    
    try:
        # Create database
        conn = create_enhanced_database()
        print("✅ Database schema created successfully")
        
        # Import solutions
        problems_count = import_neetcode_solutions(conn, neetcode_path)
        
        if problems_count > 0:
            print(f"\n📊 Database Statistics:")
            print(f"   Total Problems: {problems_count}")
            
            # Show category breakdown
            cur = conn.cursor()
            cur.execute("SELECT category, COUNT(*) FROM problems GROUP BY category ORDER BY category")
            for category, count in cur.fetchall():
                print(f"   {category}: {count} problems")
            
            print(f"\n✅ Enhanced database setup complete!")
            print(f"   Database file: recode.db")
            print(f"   Ready for use with the Recode app!")
        else:
            print("\n❌ No problems were imported. Please check the repository path.")
            
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        return 1
    
    finally:
        if 'conn' in locals():
            conn.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
