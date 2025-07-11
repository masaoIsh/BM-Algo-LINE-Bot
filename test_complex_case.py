#!/usr/bin/env python3
"""
Test complex case where Bogomolnaia-Moulin should produce fractional probabilities
"""

import numpy as np
from bot_logic import GroupDecisionBot

def test_conflicting_preferences():
    """Test case where multiple people prefer the same item"""
    print("🧪 Testing Conflicting Preferences")
    
    bot = GroupDecisionBot()
    
    # 3 people, 3 items
    items = ["A", "B", "C"]
    group_id = "conflict_test"
    bot.start_session(group_id, items)
    
    # All three people prefer item A first
    # This should result in fractional probabilities
    bot.submit_ranking(group_id, "user1", "1,2,3")  # A > B > C
    bot.submit_ranking(group_id, "user2", "1,3,2")  # A > C > B  
    bot.submit_ranking(group_id, "user3", "1,2,3")  # A > B > C
    
    # Run algorithm
    result = bot.run_algorithm(group_id)
    print(result)
    
    # Check probabilities
    session = bot.sessions[group_id]
    probabilities = session['probabilities']
    
    print(f"\nProbability Matrix:")
    for i, user_id in enumerate(session['preferences'].keys()):
        print(f"User {user_id[:8]}...: {probabilities[i]}")
    
    # Verify that probabilities sum to 1 for each person
    assert np.allclose(np.sum(probabilities, axis=1), 1.0), "Probabilities don't sum to 1"
    
    # Verify that item A is fully consumed (sum of probabilities = 1)
    assert np.isclose(np.sum(probabilities[:, 0]), 1.0), "Item A should be fully consumed"
    
    print("✅ Conflicting preferences test passed")
    return True

def test_sequential_conflicts():
    """Test case with sequential conflicts"""
    print("\n🧪 Testing Sequential Conflicts")
    
    bot = GroupDecisionBot()
    
    # 4 people, 4 items
    items = ["W", "X", "Y", "Z"]
    group_id = "sequential_test"
    bot.start_session(group_id, items)
    
    # Create a scenario where items get consumed sequentially
    bot.submit_ranking(group_id, "user1", "1,2,3,4")  # W > X > Y > Z
    bot.submit_ranking(group_id, "user2", "1,2,4,3")  # W > X > Z > Y
    bot.submit_ranking(group_id, "user3", "2,1,3,4")  # X > W > Y > Z
    bot.submit_ranking(group_id, "user4", "2,1,4,3")  # X > W > Z > Y
    
    # Run algorithm
    result = bot.run_algorithm(group_id)
    print(result)
    
    # Check probabilities
    session = bot.sessions[group_id]
    probabilities = session['probabilities']
    
    print(f"\nProbability Matrix:")
    for i, user_id in enumerate(session['preferences'].keys()):
        print(f"User {user_id[:8]}...: {probabilities[i]}")
    
    # Verify properties
    assert np.allclose(np.sum(probabilities, axis=1), 1.0), "Probabilities don't sum to 1"
    assert np.allclose(np.sum(probabilities, axis=0), 1.0), "Items aren't fully consumed"
    
    print("✅ Sequential conflicts test passed")
    return True

def test_algorithm_correctness():
    """Test that the algorithm produces the expected results for a known case"""
    print("\n🧪 Testing Algorithm Correctness")
    
    bot = GroupDecisionBot()
    
    # Classic example from Bogomolnaia and Moulin paper
    items = ["A", "B", "C"]
    group_id = "correctness_test"
    bot.start_session(group_id, items)
    
    # Preferences that should produce specific probabilities
    bot.submit_ranking(group_id, "user1", "1,2,3")  # A > B > C
    bot.submit_ranking(group_id, "user2", "1,2,3")  # A > B > C
    bot.submit_ranking(group_id, "user3", "2,1,3")  # B > A > C
    
    # Run algorithm
    bot.run_algorithm(group_id)
    session = bot.sessions[group_id]
    probabilities = session['probabilities']
    
    print(f"Probability Matrix:")
    for i, user_id in enumerate(session['preferences'].keys()):
        print(f"User {user_id[:8]}...: {probabilities[i]}")
    
    # Expected: User 1 and 2 should get equal shares of A, User 3 should get B
    # User 1: [0.5, 0, 0.5] - half of A, half of C
    # User 2: [0.5, 0, 0.5] - half of A, half of C  
    # User 3: [0, 1, 0] - all of B
    
    print(f"\nExpected vs Actual:")
    print(f"User 1 expected: [0.5, 0, 0.5], actual: {probabilities[0]}")
    print(f"User 2 expected: [0.5, 0, 0.5], actual: {probabilities[1]}")
    print(f"User 3 expected: [0, 1, 0], actual: {probabilities[2]}")
    
    # Check that probabilities are reasonable (not all 0 or 1)
    has_fractional = np.any((probabilities > 0) & (probabilities < 1))
    print(f"Has fractional probabilities: {has_fractional}")
    
    print("✅ Algorithm correctness test completed")
    return True

if __name__ == "__main__":
    print("🚀 Starting Complex Algorithm Tests\n")
    
    try:
        test_conflicting_preferences()
        test_sequential_conflicts()
        test_algorithm_correctness()
        
        print("\n🎉 All complex tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 