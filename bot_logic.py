import numpy as np
import re
from typing import Dict, List, Tuple, Optional

class GroupDecisionBot:
    def __init__(self):
        # Store active sessions: {group_id: session_data}
        self.sessions = {}
    
    def start_session(self, group_id: str, items: List[str]) -> bool:
        """Start a new assignment session"""
        if group_id in self.sessions:
            return False  # Session already exists
        
        self.sessions[group_id] = {
            'items': items,
            'preferences': {},
            'status': 'collecting',
            'probabilities': None,
            'final_assignments': None
        }
        return True
    
    def cancel_session(self, group_id: str) -> bool:
        """Cancel an active session"""
        if group_id in self.sessions:
            del self.sessions[group_id]
            return True
        return False
    
    def is_ranking_format(self, text: str, expected_length: int = None) -> bool:
        """Check if text looks like a ranking (numbers separated by commas)"""
        # Remove spaces and check if it's comma-separated numbers
        cleaned = re.sub(r'\s+', '', text)
        if not re.match(r'^\d+(,\d+)*$', cleaned):
            return False
        
        # Check if numbers are sequential starting from 1
        numbers = [int(x) for x in cleaned.split(',')]
        expected = list(range(1, len(numbers) + 1))
        
        # If expected_length is provided, check that the ranking has the right length
        if expected_length is not None and len(numbers) != expected_length:
            return False
            
        return sorted(numbers) == expected
    
    def submit_ranking(self, group_id: str, user_id: str, ranking_text: str) -> Tuple[bool, str]:
        """Submit a user's preference ranking"""
        if group_id not in self.sessions:
            return False, "❌ No active session. Type 'start assignment' to begin."
        
        session = self.sessions[group_id]
        
        if session['status'] != 'collecting':
            return False, "❌ Rankings are no longer being collected."
        
        # Clean and validate ranking
        ranking_text = re.sub(r'\s+', '', ranking_text)
        if not self.is_ranking_format(ranking_text, len(session['items'])):
            return False, "❌ Invalid ranking format. Use numbers separated by commas (e.g., '3,1,2')."
        
        # Convert to 0-based indices
        ranking = [int(x) - 1 for x in ranking_text.split(',')]
        
        if len(ranking) != len(session['items']):
            return False, f"❌ Expected {len(session['items'])} items, got {len(ranking)}."
        
        # Store the ranking
        session['preferences'][user_id] = ranking
        
        return True, f"✅ Ranking submitted! ({len(session['preferences'])}/{len(session['items'])} people have ranked)"
    
    def get_status(self, group_id: str) -> str:
        """Get current session status"""
        if group_id not in self.sessions:
            return "❌ No active session. Type 'start assignment' to begin."
        
        session = self.sessions[group_id]
        items_list = '\n'.join([f"{i+1}. {item}" for i, item in enumerate(session['items'])])
        
        status_text = f"📊 Session Status:\n\nItems:\n{items_list}\n\n"
        status_text += f"Status: {session['status']}\n"
        status_text += f"Rankings collected: {len(session['preferences'])}/{len(session['items'])}\n"
        
        if session['preferences']:
            status_text += "\nParticipants who have ranked:\n"
            for user_id in session['preferences']:
                status_text += f"• User {user_id[:8]}...\n"
        
        if session['status'] == 'collecting' and len(session['preferences']) >= len(session['items']):
            status_text += "\n🎯 Ready to run algorithm! Type 'run algorithm'"
        
        return status_text
    
    def run_algorithm(self, group_id: str) -> str:
        """Run the Bogomolnaia-Moulin algorithm"""
        if group_id not in self.sessions:
            return "❌ No active session."
        
        session = self.sessions[group_id]
        
        if session['status'] != 'collecting':
            return "❌ Algorithm already run. Type 'make assignments' for final results."
        
        if len(session['preferences']) < len(session['items']):
            return f"❌ Need {len(session['items'])} rankings, got {len(session['preferences'])}."
        
        # Run the Bogomolnaia-Moulin algorithm
        try:
            probabilities = self._bogomolnaia_moulin(session['items'], session['preferences'])
            session['probabilities'] = probabilities
            session['status'] = 'algorithm_run'
            
            # Format results
            result = "🎯 Bogomolnaia-Moulin Algorithm Results:\n\n"
            result += self._format_probabilities(probabilities, session['items'], session['preferences'])
            result += "\nType 'make assignments' to get final assignments!"
            
            return result
            
        except Exception as e:
            return f"❌ Error running algorithm: {str(e)}"
    
    def make_final_assignments(self, group_id: str) -> str:
        """Make final assignments from probabilities"""
        if group_id not in self.sessions:
            return "❌ No active session."
        
        session = self.sessions[group_id]
        
        if session['status'] != 'algorithm_run':
            return "❌ Run the algorithm first with 'run algorithm'."
        
        # Convert probabilities to assignments
        assignments = self._probabilities_to_assignments(session['probabilities'])
        session['final_assignments'] = assignments
        session['status'] = 'completed'
        
        # Format results
        result = "🎉 Final Assignments:\n\n"
        result += self._format_assignments(assignments, session['items'], session['preferences'])
        
        return result
    
    def _bogomolnaia_moulin(self, items: List[str], preferences: Dict[str, List[int]]) -> np.ndarray:
        """Pure probabilistic serial (Bogomolnaia-Moulin) implementation.
        Returns an n_participants × n_items matrix of probabilities."""
        n_participants = len(preferences)
        n_items = len(items)

        # Convert preference lists to numpy array for fast indexing
        pref_matrix = np.zeros((n_participants, n_items), dtype=int)
        user_ids = list(preferences.keys())
        for i, uid in enumerate(user_ids):
            pref_matrix[i] = preferences[uid]

        # Remaining capacities
        item_remaining = np.ones(n_items, dtype=float)  # each item has 1 unit total
        person_remaining = np.ones(n_participants, dtype=float)  # each person must consume 1 unit total

        # Result probability matrix
        prob = np.zeros((n_participants, n_items), dtype=float)

        # Main eating loop
        while np.any(person_remaining > 1e-9):
            # Determine each active person's current top available item
            top_choice = np.full(n_participants, -1, dtype=int)
            for p in range(n_participants):
                if person_remaining[p] <= 1e-9:
                    continue  # already full
                for item in pref_matrix[p]:
                    if item_remaining[item] > 1e-9:
                        top_choice[p] = item
                        break
            # For each item, collect eaters
            eaters_per_item = {j: [] for j in range(n_items)}
            for p, itm in enumerate(top_choice):
                if itm >= 0:
                    eaters_per_item[itm].append(p)

            # Compute smallest time step until a boundary event (item or person exhausted)
            dt_candidates = []
            for itm, eaters in eaters_per_item.items():
                if not eaters:
                    continue
                k = len(eaters)
                dt_item = item_remaining[itm] / k  # time until item exhausted
                dt_candidates.append(dt_item)
            for p in range(n_participants):
                if person_remaining[p] > 1e-9 and top_choice[p] != -1:
                    dt_candidates.append(person_remaining[p])
            if not dt_candidates:
                # No valid moves (shouldn't happen if preferences cover all items)
                break
            dt = min(dt_candidates)

            # Eat for dt
            for itm, eaters in eaters_per_item.items():
                if not eaters:
                    continue
                k = len(eaters)
                consume_amount_item = dt * k
                consume_per_person = dt
                # Update item remaining
                item_remaining[itm] -= consume_amount_item
                if item_remaining[itm] < 0:
                    item_remaining[itm] = 0.0
                # Update each eater
                for p in eaters:
                    prob[p, itm] += consume_per_person
                    person_remaining[p] -= consume_per_person
                    if person_remaining[p] < 0:
                        person_remaining[p] = 0.0
        # Normalize tiny numerical negatives to 0 / ensure rows sum to 1
        prob[prob < 0] = 0
        row_sums = prob.sum(axis=1, keepdims=True)
        # Guard against division by zero (in case of numerical errors)
        row_sums[row_sums == 0] = 1.0
        prob = prob / row_sums
        return prob
    
    def _probabilities_to_assignments(self, probabilities: np.ndarray) -> List[int]:
        """Convert probability matrix to concrete assignments using randomized rounding"""
        n_participants, n_items = probabilities.shape
        assignments = []
        
        # Use randomized rounding
        for person in range(n_participants):
            # Sample from the probability distribution
            assignment = np.random.choice(n_items, p=probabilities[person])
            assignments.append(assignment)
        
        return assignments
    
    def _format_probabilities(self, probabilities: np.ndarray, items: List[str], preferences: Dict[str, List[int]]) -> str:
        """Format probability results for display"""
        result = ""
        user_ids = list(preferences.keys())
        
        for i, user_id in enumerate(user_ids):
            result += f"User {user_id[:8]}...:\n"
            for j, item in enumerate(items):
                prob = probabilities[i, j]
                if prob > 0:
                    result += f"  {item}: {prob:.1%}\n"
            result += "\n"
        
        return result
    
    def _format_assignments(self, assignments: List[int], items: List[str], preferences: Dict[str, List[int]]) -> str:
        """Format final assignments for display"""
        result = ""
        user_ids = list(preferences.keys())
        
        for i, user_id in enumerate(user_ids):
            assigned_item = items[assignments[i]]
            result += f"User {user_id[:8]}... → {assigned_item}\n"
        
        return result 