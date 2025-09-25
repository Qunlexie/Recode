#!/usr/bin/env python3
"""
Batch Code Cleaning Utility
Automated tool for cleaning all code blocks in the database
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from code_validator import CodeValidator, BatchCodeCleaner, ValidationLevel
from database_utils import get_all_problems, update_problem


class DatabaseCodeCleaner:
    """Clean all code in the database using the advanced validator"""
    
    def __init__(self, db_path: str = "recode.db"):
        self.db_path = db_path
        self.validator = CodeValidator(ValidationLevel.COMPREHENSIVE)
        self.batch_cleaner = BatchCodeCleaner(ValidationLevel.COMPREHENSIVE)
    
    def clean_all_problems(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean all problems in the database
        
        Args:
            dry_run: If True, don't actually update the database
            
        Returns:
            Dictionary with cleaning results and statistics
        """
        print("🔍 Loading problems from database...")
        problems = get_all_problems()
        
        print(f"📊 Found {len(problems)} problems to process")
        
        cleaning_results = {
            'total_problems': len(problems),
            'cleaned_problems': 0,
            'problems_with_errors': 0,
            'problems_with_warnings': 0,
            'validation_errors': [],
            'detailed_results': []
        }
        
        for i, problem in enumerate(problems, 1):
            print(f"🔄 Processing problem {i}/{len(problems)}: {problem.get('title', 'Unknown')}")
            
            if not problem.get('solution_code'):
                print("  ⚠️ No solution code found, skipping...")
                continue
            
            # Validate and clean the code
            result = self.validator.validate_and_fix_code(problem['solution_code'])
            
            problem_result = {
                'id': problem['id'],
                'title': problem['title'],
                'original_code_length': len(problem['solution_code']),
                'cleaned_code_length': len(result.fixed_code),
                'is_valid': result.is_valid,
                'errors': result.errors,
                'warnings': result.warnings,
                'suggestions': result.suggestions,
                'code_changed': result.fixed_code != problem['solution_code']
            }
            
            cleaning_results['detailed_results'].append(problem_result)
            
            # Update statistics
            if result.fixed_code != problem['solution_code']:
                cleaning_results['cleaned_problems'] += 1
            
            if result.errors:
                cleaning_results['problems_with_errors'] += 1
                cleaning_results['validation_errors'].extend([
                    f"{problem['title']}: {error}" for error in result.errors
                ])
            
            if result.warnings:
                cleaning_results['problems_with_warnings'] += 1
            
            # Update database if not dry run
            if not dry_run and result.fixed_code != problem['solution_code']:
                try:
                    update_problem(
                        problem['id'],
                        solution_code=result.fixed_code
                    )
                    print(f"  ✅ Updated problem {problem['id']}")
                except Exception as e:
                    print(f"  ❌ Failed to update problem {problem['id']}: {str(e)}")
                    problem_result['update_error'] = str(e)
        
        # Calculate final statistics
        cleaning_results['success_rate'] = (
            (cleaning_results['total_problems'] - cleaning_results['problems_with_errors']) / 
            cleaning_results['total_problems'] * 100
        ) if cleaning_results['total_problems'] > 0 else 0
        
        return cleaning_results
    
    def clean_specific_problems(self, problem_ids: List[int], dry_run: bool = True) -> Dict[str, Any]:
        """Clean specific problems by their IDs"""
        problems = get_all_problems()
        target_problems = [p for p in problems if p['id'] in problem_ids]
        
        print(f"🎯 Cleaning {len(target_problems)} specific problems...")
        
        # Use the same cleaning logic but with filtered problems
        all_problems = get_all_problems()
        filtered_problems = [p for p in all_problems if p['id'] in problem_ids]
        
        return self._clean_problems_list(filtered_problems, dry_run)
    
    def clean_problems_by_category(self, category: str, dry_run: bool = True) -> Dict[str, Any]:
        """Clean problems by category"""
        problems = get_all_problems()
        target_problems = [p for p in problems if p.get('category') == category]
        
        print(f"📂 Cleaning {len(target_problems)} problems in category: {category}")
        
        return self._clean_problems_list(target_problems, dry_run)
    
    def _clean_problems_list(self, problems: List[Dict], dry_run: bool) -> Dict[str, Any]:
        """Internal method to clean a list of problems"""
        cleaning_results = {
            'total_problems': len(problems),
            'cleaned_problems': 0,
            'problems_with_errors': 0,
            'problems_with_warnings': 0,
            'validation_errors': [],
            'detailed_results': []
        }
        
        for problem in problems:
            if not problem.get('solution_code'):
                continue
            
            result = self.validator.validate_and_fix_code(problem['solution_code'])
            
            problem_result = {
                'id': problem['id'],
                'title': problem['title'],
                'is_valid': result.is_valid,
                'errors': result.errors,
                'warnings': result.warnings,
                'code_changed': result.fixed_code != problem['solution_code']
            }
            
            cleaning_results['detailed_results'].append(problem_result)
            
            if result.fixed_code != problem['solution_code']:
                cleaning_results['cleaned_problems'] += 1
            
            if result.errors:
                cleaning_results['problems_with_errors'] += 1
                cleaning_results['validation_errors'].extend([
                    f"{problem['title']}: {error}" for error in result.errors
                ])
            
            if result.warnings:
                cleaning_results['problems_with_warnings'] += 1
            
            if not dry_run and result.fixed_code != problem['solution_code']:
                try:
                    update_problem(problem['id'], solution_code=result.fixed_code)
                except Exception as e:
                    problem_result['update_error'] = str(e)
        
        return cleaning_results
    
    def generate_cleaning_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed cleaning report"""
        report = []
        report.append("# 🔧 Code Cleaning Report")
        report.append("")
        
        # Summary statistics
        report.append("## 📊 Summary Statistics")
        report.append(f"- **Total Problems Processed:** {results['total_problems']}")
        report.append(f"- **Problems Cleaned:** {results['cleaned_problems']}")
        report.append(f"- **Problems with Errors:** {results['problems_with_errors']}")
        report.append(f"- **Problems with Warnings:** {results['problems_with_warnings']}")
        report.append(f"- **Success Rate:** {results['success_rate']:.1f}%")
        report.append("")
        
        # Validation errors
        if results['validation_errors']:
            report.append("## ❌ Validation Errors")
            for error in results['validation_errors']:
                report.append(f"- {error}")
            report.append("")
        
        # Detailed results for problems that were changed
        changed_problems = [r for r in results['detailed_results'] if r['code_changed']]
        if changed_problems:
            report.append("## 🔄 Problems That Were Cleaned")
            for result in changed_problems:
                report.append(f"### {result['title']} (ID: {result['id']})")
                if result['errors']:
                    report.append("**Errors Fixed:**")
                    for error in result['errors']:
                        report.append(f"- {error}")
                if result['warnings']:
                    report.append("**Warnings:**")
                    for warning in result['warnings']:
                        report.append(f"- {warning}")
                report.append("")
        
        # Problems that still have issues
        problematic_problems = [r for r in results['detailed_results'] if not r['is_valid']]
        if problematic_problems:
            report.append("## ⚠️ Problems That Still Need Attention")
            for result in problematic_problems:
                report.append(f"### {result['title']} (ID: {result['id']})")
                if result['errors']:
                    report.append("**Errors:**")
                    for error in result['errors']:
                        report.append(f"- {error}")
                report.append("")
        
        return "\n".join(report)
    
    def export_cleaning_results(self, results: Dict[str, Any], filename: str = "cleaning_results.json"):
        """Export cleaning results to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📄 Results exported to {filename}")


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean code blocks in the Recode database")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually update the database")
    parser.add_argument("--category", type=str, help="Clean only problems in this category")
    parser.add_argument("--ids", type=str, help="Comma-separated list of problem IDs to clean")
    parser.add_argument("--report", type=str, help="Generate report file with this name")
    
    args = parser.parse_args()
    
    cleaner = DatabaseCodeCleaner()
    
    if args.ids:
        # Clean specific problems
        problem_ids = [int(id.strip()) for id in args.ids.split(",")]
        results = cleaner.clean_specific_problems(problem_ids, dry_run=args.dry_run)
    elif args.category:
        # Clean problems by category
        results = cleaner.clean_problems_by_category(args.category, dry_run=args.dry_run)
    else:
        # Clean all problems
        results = cleaner.clean_all_problems(dry_run=args.dry_run)
    
    # Generate and display report
    report = cleaner.generate_cleaning_report(results)
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    # Export results if requested
    if args.report:
        cleaner.export_cleaning_results(results, args.report)
        with open(args.report.replace('.json', '.md'), 'w') as f:
            f.write(report)
        print(f"📄 Report saved to {args.report.replace('.json', '.md')}")
    
    if args.dry_run:
        print("\n🔍 This was a dry run. Use --dry-run=false to actually update the database.")
    else:
        print(f"\n✅ Cleaning complete! {results['cleaned_problems']} problems were updated.")


if __name__ == "__main__":
    main()
