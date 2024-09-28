user_profiles = {}

class UserProfile:
    
    def update_user_profile(self, user_id, severity):
        if user_id not in user_profiles:
            user_profiles[user_id] = {'total_reports': 0, 'real_reports': 0, 'fake_reports': 0, 'confidence_score': 0.5}
        
        profile = user_profiles[user_id]
        profile['total_reports'] += 1
        
        reward, penalty = self._get_severity_reward_penalty(severity)
        profile['confidence_score'] += reward
        
        profile['confidence_score'] = max(0, min(1, profile['confidence_score']))
        
        return profile['confidence_score']
    
    def get_user_profile(self, user_id):
        if user_id not in user_profiles:
            user_profiles[user_id] = {'total_reports': 0, 'real_reports': 0, 'fake_reports': 0, 'confidence_score': 0.5}
        
        return user_profiles[user_id]
    
    def _get_severity_reward_penalty(self, severity):
        if severity == 'high':
            return 0.1, -0.2
        elif severity == 'medium':
            return 0.05, -0.1
        return 0.025, -0.05
