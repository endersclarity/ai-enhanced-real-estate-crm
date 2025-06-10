#!/usr/bin/env python3
"""
AI-generated fix for the DatabaseConfig missing method issue
"""

def add_missing_methods_to_database_config():
    """
    Add the missing get_all_clients method to DatabaseConfig class
    """
    
    # The method to add to DatabaseConfig class
    new_method = '''
    def get_all_clients(self):
        """Get all clients from the database"""
        if self.use_supabase:
            try:
                # Get all clients from Supabase
                response = requests.get(
                    f"{self.supabase_url}/rest/v1/clients",
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error fetching clients from Supabase: {response.status_code}")
                    return []
            except Exception as e:
                print(f"Error fetching clients from Supabase: {e}")
                return []
        else:
            # SQLite fallback
            query = "SELECT * FROM clients ORDER BY created_at DESC"
            return self.execute_query(query, fetch_all=True)
'''
    
    print("📝 Fix: Add get_all_clients method to DatabaseConfig class")
    print("\nLocation: database_config.py")
    print("\nAdd this method to the DatabaseConfig class:")
    print(new_method)
    
    # Alternative simpler fix
    print("\n--- OR SIMPLER FIX ---")
    print("\nChange line 2041 in core_app/real_estate_crm.py:")
    print("FROM: clients = db.get_all_clients()")
    print("TO:   clients = db.execute_query('SELECT * FROM clients ORDER BY created_at DESC', fetch_all=True)")
    

if __name__ == "__main__":
    add_missing_methods_to_database_config()