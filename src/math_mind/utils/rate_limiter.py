# import time
# from collections import deque
# from math_mind.engines.exceptions import RateLimitExceededError

# class RateLimiter:
#     def __init__(self, rpm_limit: int, rpd_limit: int):
#         self.rpm_limit = rpm_limit
#         self.rpd_limit = rpd_limit
#         self._requests = deque() # Holds timestamps of requests

#     def check_limit(self):
#         now = time.time()
        
#         # 1. Clean up timestamps older than 24 hours (RPD)
#         while self._requests and self._requests[0] < now - 86400:
#             self._requests.popleft()
            
#         # 2. Check RPM (Requests in the last 60 seconds)
#         one_minute_ago = now - 60
#         rpm_count = sum(1 for t in self._requests if t > one_minute_ago)
        
#         if rpm_count >= self.rpm_limit:
#             raise RateLimitExceededError(f"RPM limit of {self.rpm_limit} reached.")
            
#         # 3. Check RPD (Total requests remaining in deque after cleanup)
#         if len(self._requests) >= self.rpd_limit:
#             raise RateLimitExceededError(f"RPD limit of {self.rpd_limit} reached.")
            
#         # 4. Record the request
#         self._requests.append(now)