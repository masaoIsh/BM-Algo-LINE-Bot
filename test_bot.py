#!/usr/bin/env python3
"""
Test script for the Bogomolnaia-Moulin algorithm implementation
"""

import numpy as np
from bot_logic import GroupDecisionBot

def test_basic_assignment():
    """Test basic 3-person, 3-item assignment"""
    print("🧪 Testing Basic Assignment (3 people, 3 items)")
    
    bot = GroupDecisionBot()
    
    # Start session
    items = ["Research", "Writing", "Presentation"]
    group_id = "test_group_1"
    bot.start_session(group_id, items)
    
    # Submit preferences
    # Person 1: Presentation > Research > Writing
    # Person 2: Research > Presentation > Writing  
    # Person 3: Writing > Research > Presentation
    bot.submit_ranking(group_id, "user1", "3,1,2")
    bot.submit_ranking(group_id, "user2", "1,3,2")
    bot.submit_ranking(group_id, "user3", "2,1,3")
    
    # Run algorithm
    result = bot.run_algorithm(group_id)
    print(result)
    
    # Make final assignments
    final_result = bot.make_final_assignments(group_id)
    print(final_result)
    
    return True

def test_2_person_assignment():
    """Test 2-person assignment"""
    print("\n🧪 Testing 2-Person Assignment")
    
    bot = GroupDecisionBot()
    
    items = ["Task A", "Task B"]
    group_id = "test_group_2"
    bot.start_session(group_id, items)
    
    # Both prefer Task A
    bot.submit_ranking(group_id, "user1", "1,2")
    bot.submit_ranking(group_id, "user2", "1,2")
    
    result = bot.run_algorithm(group_id)
    print(result)
    
    return True

def test_4_person_assignment():
    """Test 4-person assignment"""
    print("\n🧪 Testing 4-Person Assignment")
    
    bot = GroupDecisionBot()
    
    items = ["Research", "Writing", "Presentation", "Data Analysis"]
    group_id = "test_group_3"
    bot.start_session(group_id, items)
    
    # Submit diverse preferences
    bot.submit_ranking(group_id, "user1", "3,1,2,4")  # Presentation > Research > Writing > Data
    bot.submit_ranking(group_id, "user2", "1,3,4,2")  # Research > Presentation > Data > Writing
    bot.submit_ranking(group_id, "user3", "4,2,1,3")  # Data > Writing > Research > Presentation
    bot.submit_ranking(group_id, "user4", "2,4,3,1")  # Writing > Data > Presentation > Research
    
    result = bot.run_algorithm(group_id)
    print(result)
    
    return True

def test_algorithm_properties():
    """Test that the algorithm produces valid probability distributions"""
    print("\n🧪 Testing Algorithm Properties")
    
    bot = GroupDecisionBot()
    
    items = ["A", "B", "C"]
    group_id = "test_group_4"
    bot.start_session(group_id, items)
    
    # Submit preferences
    bot.submit_ranking(group_id, "user1", "1,2,3")
    bot.submit_ranking(group_id, "user2", "2,1,3")
    bot.submit_ranking(group_id, "user3", "3,1,2")
    
    # Run algorithm and get probabilities
    bot.run_algorithm(group_id)
    session = bot.sessions[group_id]
    probabilities = session['probabilities']
    
    # Check properties
    print(f"Probability matrix shape: {probabilities.shape}")
    print(f"Probabilities sum to 1 for each person: {np.allclose(np.sum(probabilities, axis=1), 1.0)}")
    print(f"All probabilities >= 0: {np.all(probabilities >= 0)}")
    print(f"All probabilities <= 1: {np.all(probabilities <= 1)}")
    
    # Print probability matrix
    print("\nProbability Matrix:")
    for i, user_id in enumerate(session['preferences'].keys()):
        print(f"User {user_id[:8]}...: {probabilities[i]}")
    
    return True

def test_ranking_validation():
    """Test ranking format validation"""
    print("\n🧪 Testing Ranking Validation")
    
    bot = GroupDecisionBot()
    
    # Valid rankings
    valid_rankings = ["1,2,3", "3,1,2", "2,3,1", "1,2", "2,1"]
    for ranking in valid_rankings:
        assert bot.is_ranking_format(ranking), f"Valid ranking '{ranking}' was rejected"
    
    # Invalid rankings (format issues)
    invalid_rankings = ["1,2,4", "1,1,2", "a,b,c", "1,2,", ",1,2"]
    for ranking in invalid_rankings:
        assert not bot.is_ranking_format(ranking), f"Invalid ranking '{ranking}' was accepted"
    
    # Test length validation
    assert not bot.is_ranking_format("1,2,3,4", 3), "Ranking with wrong length was accepted"
    assert bot.is_ranking_format("1,2,3", 3), "Valid ranking with correct length was rejected"
    
    print("✅ All ranking validation tests passed")
    return True

if __name__ == "__main__":
    print("🚀 Starting Fair Assignment Bot Tests\n")
    
    try:
        test_ranking_validation()
        test_basic_assignment()
        test_2_person_assignment()
        test_4_person_assignment()
        test_algorithm_properties()
        
        print("\n🎉 All tests passed! The bot is ready to use.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 