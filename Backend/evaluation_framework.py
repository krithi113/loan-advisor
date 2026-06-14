"""
Evaluation Framework for Loan Eligibility Advisor
This file contains test cases and metrics for evaluating system performance
"""

import json
import requests
from typing import List, Dict
from datetime import datetime

# Test cases with expected outcomes
TEST_CASES = [
    {
        "name": "Prime Borrower - Should qualify for Prime + Standard",
        "input": {
            "annual_income": 100000,
            "existing_debt": 20000,
            "credit_score": 780,
            "requested_loan_amount": 30000,
        },
        "expected": {
            "min_eligible_products": 2,
            "should_require_review": False,
            "should_have_high_risk_flags": False,
        },
    },
    {
        "name": "Standard Borrower - Should qualify for Standard",
        "input": {
            "annual_income": 50000,
            "existing_debt": 10000,
            "credit_score": 680,
            "requested_loan_amount": 15000,
        },
        "expected": {
            "min_eligible_products": 1,
            "should_require_review": False,
            "should_have_high_risk_flags": False,
        },
    },
    {
        "name": "High Debt Ratio - Should flag for review",
        "input": {
            "annual_income": 40000,
            "existing_debt": 25000,
            "credit_score": 720,
            "requested_loan_amount": 10000,
        },
        "expected": {
            "min_eligible_products": 0,
            "should_require_review": True,
            "should_have_high_risk_flags": True,
        },
    },
    {
        "name": "Low Credit Score - Should flag risk but may qualify",
        "input": {
            "annual_income": 60000,
            "existing_debt": 12000,
            "credit_score": 620,
            "requested_loan_amount": 20000,
        },
        "expected": {
            "min_eligible_products": 0,
            "should_require_review": True,
            "should_have_high_risk_flags": True,
        },
    },
    {
        "name": "Low Income - Should not qualify",
        "input": {
            "annual_income": 25000,
            "existing_debt": 5000,
            "credit_score": 700,
            "requested_loan_amount": 20000,
        },
        "expected": {
            "min_eligible_products": 0,
            "should_require_review": True,
            "should_have_high_risk_flags": True,
        },
    },
]

class EvaluationFramework:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results = []
        self.metrics = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "accuracy": 0,
            "test_results": [],
        }

    def run_test(self, test_case: Dict) -> Dict:
        """Run a single test case"""
        try:
            response = requests.post(
                f"{self.api_url}/evaluate",
                json=test_case["input"],
                timeout=180,
            )
            
            if response.status_code != 200:
                return {
                    "test_name": test_case["name"],
                    "passed": False,
                    "error": f"HTTP {response.status_code}",
                }
            
            result = response.json()
            expected = test_case["expected"]
            
            # Check expectations
            passed = True
            failures = []
            
            # Check number of eligible products
            num_products = len(result.get("eligible_products", []))
            if num_products < expected["min_eligible_products"]:
                passed = False
                failures.append(
                    f"Expected at least {expected['min_eligible_products']} products, got {num_products}"
                )
            
            # Check if review is needed
            if result.get("requires_human_review") != expected["should_require_review"]:
                passed = False
                failures.append(
                    f"Expected review={expected['should_require_review']}, got {result.get('requires_human_review')}"
                )
            
            # Check risk flags
            has_high_risk = any("HIGH" in flag for flag in result.get("risk_assessment", []))
            if has_high_risk != expected["should_have_high_risk_flags"]:
                passed = False
                failures.append(
                    f"Expected high_risk={expected['should_have_high_risk_flags']}, got {has_high_risk}"
                )
            
            return {
                "test_name": test_case["name"],
                "passed": passed,
                "input": test_case["input"],
                "output": result,
                "failures": failures,
            }
        
        except Exception as e:
            return {
                "test_name": test_case["name"],
                "passed": False,
                "error": str(e),
            }

    def run_all_tests(self) -> Dict:
        """Run all test cases and compute metrics"""
        print("\n" + "="*60)
        print("LOAN ELIGIBILITY SYSTEM EVALUATION")
        print("="*60 + "\n")
        
        for test_case in TEST_CASES:
            print(f"Running: {test_case['name']}...", end=" ")
            result = self.run_test(test_case)
            self.results.append(result)
            
            if result["passed"]:
                print("✅ PASS")
            else:
                print("❌ FAIL")
                if result.get("failures"):
                    for failure in result["failures"]:
                        print(f"   - {failure}")
                if result.get("error"):
                    print(f"   - Error: {result['error']}")
        
        # Compute metrics
        self.metrics["total_tests"] = len(self.results)
        self.metrics["passed"] = sum(1 for r in self.results if r.get("passed", False))
        self.metrics["failed"] = self.metrics["total_tests"] - self.metrics["passed"]
        self.metrics["accuracy"] = round(
            (self.metrics["passed"] / max(1, self.metrics["total_tests"])) * 100, 2
        )
        self.metrics["test_results"] = self.results
        
        return self.metrics

    def print_summary(self):
        """Print evaluation summary"""
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.metrics['total_tests']}")
        print(f"Passed: {self.metrics['passed']} ✅")
        print(f"Failed: {self.metrics['failed']} ❌")
        print(f"Accuracy: {self.metrics['accuracy']}%")
        print("="*60 + "\n")

    def save_report(self, filepath: str = "evaluation_report.json"):
        """Save detailed evaluation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.metrics["total_tests"],
                "passed": self.metrics["passed"],
                "failed": self.metrics["failed"],
                "accuracy_percent": self.metrics["accuracy"],
            },
            "detailed_results": self.results,
        }
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to {filepath}")

if __name__ == "__main__":
    # Run evaluation
    evaluator = EvaluationFramework()
    evaluator.run_all_tests()
    evaluator.print_summary()
    evaluator.save_report()
